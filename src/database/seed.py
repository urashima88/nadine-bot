import os
import sys
import json
from decimal import Decimal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logging import Logger

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from src.logging.logger import setup_logger


class SeedManager:
    def __init__(self, db_config: Dict[str, str], logger: Logger):
        self.db_config = db_config
        self.logger = logger
        self.conn = psycopg2.connect(**self.db_config)
        self.seed_dir = Path(__file__).parent.parent.parent / "seeds"

    def _load_json(self, filename: str) -> List[Dict]:
        path = self.seed_dir / filename
        if not path.exists():
            self.logger.warning(f"Seed file {path} not found, skipping.")
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _execute_values(
        self, 
        table: str, 
        columns: List[str], 
        values: List[tuple],
        conflict_target: Optional[str] = None
    ) -> None:
        if not values:
            return
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES %s"
        if conflict_target:
            sql += f" ON CONFLICT ({conflict_target}) DO NOTHING"
        with self.conn.cursor() as cur:
            execute_values(cur, sql, values, page_size=1000)
        self.conn.commit()

    def _fetch_id_map(self, table: str, key_column: str) -> Dict:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT id, {key_column} FROM {table}")
            return {row[1]: row[0] for row in cur.fetchall()}

    def clear_tables(self):
        tables_order = [
            'order_products', 'orders', 'order_attempts', 'cart',
            'delivery_points', 'product_materials', 'materials', 'products', 'users'
        ]
        with self.conn.cursor() as cur:
            for table in tables_order:
                cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
            self.conn.commit()
        self.logger.info("All tables cleared.")

    def seed_materials(self, filename: str) -> Dict[str, str]:
        data = self._load_json(filename)
        if not data:
            return {}
        values = [(item['name'],) for item in data]
        self._execute_values('materials', ['name'], values, conflict_target='name')
        return self._fetch_id_map('materials', 'name')

    def seed_products(self, filename: str, materials: Dict[str, str]) -> Dict[int, str]:
        data = self._load_json(filename)
        if not data:
            return {}
        product_ids = {}
        with self.conn.cursor() as cur:
            for item in data:
                cur.execute("""
                    INSERT INTO products (
                        name, article_number, description, price,
                        category, production_time, prod_limit, image_dir
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_number) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id, article_number
                """, (
                    item['name'], item['article_number'], item.get('description'),
                    Decimal(str(item['price'])), item.get('category'),
                    item.get('production_time'), item.get('prod_limit'), item.get('image_dir')
                ))
                row = cur.fetchone()
                product_id = row[0]
                article_number = row[1]
                product_ids[article_number] = product_id

                if 'materials' in item:
                    for mat_name in item['materials']:
                        material_id = materials.get(mat_name)
                        if material_id:
                            cur.execute("""
                                INSERT INTO product_materials (product_id, material_id)
                                VALUES (%s, %s) ON CONFLICT DO NOTHING
                            """, (product_id, material_id))
                        else:
                            self.logger.warning(f"Material {mat_name} not found for product {item['name']}")
            self.conn.commit()
        self.logger.info(f"Loaded {len(product_ids)} products.")
        return product_ids

    def seed_users(self, filename: str) -> Dict[int, str]:
        data = self._load_json(filename)
        if not data:
            return {}
        with self.conn.cursor() as cur:
            for u in data:
                cur.execute("""
                    INSERT INTO users (tg_user_id, tg_username, tg_full_name, full_name, phone, is_admin, timezone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tg_user_id) DO UPDATE SET
                        tg_username = EXCLUDED.tg_username,
                        tg_full_name = EXCLUDED.tg_full_name,
                        full_name = EXCLUDED.full_name,
                        phone = EXCLUDED.phone,
                        is_admin = EXCLUDED.is_admin,
                        timezone = EXCLUDED.timezone
                """, (
                    u['tg_user_id'], u.get('tg_username'), u.get('tg_full_name'),
                    u.get('full_name'), u.get('phone'), u.get('is_admin', False),
                    u.get('timezone', '')
                ))
            self.conn.commit()
        return self._fetch_id_map('users', 'tg_user_id')

    def seed_delivery_points(self, filename: str, users: Dict[int, str]) -> Dict[str, Tuple[str]]:
        data = self._load_json(filename)
        if not data:
            return {}
        values = []
        for item in data:
            user_id = users.get(item['tg_user_id'])
            if not user_id:
                self.logger.warning(f"Unknown user {item['tg_user_id']}")
                continue
            values.append((user_id, item['company'], item['address']))
        self._execute_values('delivery_points', ['user_id', 'company', 'address'], values)
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id, company, address FROM delivery_points")
            mapping = {}
            for row in cur.fetchall():
                mapping[row[0]] = (row[2], row[3]) # user_id: (company, address)
        self.logger.info(f"Loaded {len(values)} delivery points.")
        return mapping

    def seed_cart(self, filename: str, users: Dict[int, str], products: Dict[int, str]):
        data = self._load_json(filename)
        if not data:
            return
        values = []
        for item in data:
            user_id = users.get(item['tg_user_id'])
            product_id = products.get(item['article_number'])
            if not user_id:
                self.logger.warning(f"Unknown user {item['tg_user_id']}")
                continue
            if not product_id:
                self.logger.warning(f"Unknown product article {item['article_number']}")
                continue
            values.append((user_id, product_id, item.get('quantity', 1)))
        self._execute_values('cart', ['user_id', 'product_id', 'quantity'],
                             values, conflict_target='user_id, product_id')
        self.logger.info(f"Loaded {len(values)} cart items.")

    def seed_orders_and_items(
        self, 
        filename: str, 
        users: Dict[int, str],
        delivery_points: Dict[tuple, str], 
        products: Dict[int, str]
    ):
        data = self._load_json(filename)
        if not data:
            return
        with self.conn.cursor() as cur:
            for order in data:
                user_id = users.get(order['tg_user_id'])
                if not user_id:
                    self.logger.warning(f"Unknown user {order['tg_user_id']}")
                    continue
                
                delivery_company, delivery_point_address = delivery_points.get(user_id)

                created_at = datetime.now() - timedelta(days=order.get('created_at_days_ago', 0))
                cur.execute("""
                    INSERT INTO orders (
                        user_id, 
                        order_price, 
                        delivery_price, 
                        status, 
                        created_at, 
                        delivery_company_snapshot, 
                        delivery_point_address_snapshot,
                        delivery_info
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_id, 
                    Decimal(str(order['order_price'])),
                    Decimal(str(order['delivery_price'])), 
                    order['status'], 
                    created_at,
                    delivery_company,
                    delivery_point_address,
                    order.get('delivery_info', '')
                ))
                order_id = cur.fetchone()[0]

                for item in order['items']:
                    product_id = products.get(item['article_number'])
                    if not product_id:
                        self.logger.warning(f"Unknown product article {item['article_number']}")
                        continue
                    cur.execute("""
                        INSERT INTO order_products (order_id, product_id, quantity, price_at_order)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        order_id, product_id, item['quantity'],
                        Decimal(str(item['price_at_order']))
                    ))
            self.conn.commit()
        self.logger.info("Orders and order items loaded.")

    def seed_all(self):
        self.clear_tables()

        materials = self.seed_materials('01_materials.json')
        products = self.seed_products('02_products.json', materials)
        users = self.seed_users('03_users.json')
        delivery_points = self.seed_delivery_points('04_delivery_points.json', users)
        self.seed_cart('05_cart.json', users, products)
        self.seed_orders_and_items('06_orders.json', users, delivery_points, products)

        self.logger.info("All test data loaded successfully!")


def main():
    load_dotenv()
    logger = setup_logger(
        os.getenv("LOG_LEVEL", "DEBUG"),
        bool(int(os.getenv("USE_STREAM_HANDLER", 1))),
        bool(int(os.getenv("USE_FILE_HANDLER", 1))),
        os.getenv("LOGS_DIR", "logs")
    )
    conn_args = {
        "host": os.getenv('DB_HOST', 'localhost'),
        "port": os.getenv('DB_PORT', '5432'),
        "database": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD')
    }
    logger.info("Starting test data loading...")
    try:
        seed_manager = SeedManager(conn_args, logger)
        seed_manager.seed_all()
    except Exception as e:
        logger.exception("Error loading test data: %s", e)
        sys.exit(1)
    finally:
        if 'seed_manager' in locals():
            seed_manager.conn.close()


if __name__ == "__main__":
    main()