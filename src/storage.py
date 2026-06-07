from logging import Logger
from typing import List, Tuple, Optional, Any, Dict
from contextlib import contextmanager
from enum import IntEnum

import psycopg2
from psycopg2 import pool, sql, extras

class AddToCartResult(IntEnum):
    SUCCESS = 0
    PRODUCT_NOT_FOUND = 1
    LIMIT_EXCEEDED = 2
    USER_NOT_FOUND = 3 

class Storage:
    def __init__(self, conn_args: Dict[str, str], logger: Logger, min_conn: int = 1, max_conn: int = 10):
        self.conn_args = conn_args
        self.logger = logger
        self.pool = pool.SimpleConnectionPool(min_conn, max_conn, **conn_args)
        self.logger.info("PostgreSQL connection pool created")
        
    @contextmanager
    def _get_connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
            
    @contextmanager
    def _get_cursor(self, conn):
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            yield cur
            
    def register_user(self, tg_user_id: int, tg_username: str = None, tg_full_name: str = None) -> Optional[str]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    INSERT INTO users (tg_user_id, tg_username, tg_full_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (tg_user_id) DO UPDATE
                    SET tg_username = COALESCE(EXCLUDED.tg_username, users.tg_username),
                        tg_full_name = COALESCE(EXCLUDED.tg_full_name, users.tg_full_name),
                        updated_at = NOW()
                    RETURNING id;
                """, (tg_user_id, tg_username, tg_full_name))
                row = cur.fetchone()
                return row['id'] if row else None
            
    def get_cart_products(self, tg_user_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT 
                        p.article_number,
                        p.name,
                        p.price,
                        c.quantity,
                        p.image_dir
                    FROM cart c
                    JOIN users u ON c.user_id = u.id
                    JOIN products p ON c.product_id = p.id
                    WHERE u.tg_user_id = %s
                    ORDER BY c.added_at;
                """, (tg_user_id,))
                return cur.fetchall()
        
    def get_all_products(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT 
                        article_number,
                        name,
                        price,
                        image_dir
                    FROM products
                    ORDER BY article_number;
                """)
                return cur.fetchall()
            
    def get_category_products(self, category: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT
                        article_number,
                        name,
                        price,
                        image_dir
                    FROM products
                    WHERE category = %s
                    ORDER BY article_number;
                """, (category,))
                return cur.fetchall()
    
    def get_product_by_article_number(self, article_number: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT 
                        p.name,
                        p.description,
                        p.price,
                        p.category,
                        p.image_dir,
                        p.production_time,
                        p.prod_limit,
                        COALESCE(string_agg(m.name, ', '), '') AS materials_list
                    FROM products p
                    LEFT JOIN product_materials pm ON p.id = pm.product_id
                    LEFT JOIN materials m ON pm.material_id = m.id
                    WHERE p.article_number = %s
                    GROUP BY p.id;
                """, (article_number,))
                return cur.fetchone()
    
    def add_to_cart(self, tg_user_id: int, article_number: int, quantity: int = 1) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    WITH 
                    user_product AS (
                        SELECT u.id AS user_id, p.id AS product_id, p.prod_limit
                        FROM users u
                        CROSS JOIN products p
                        WHERE u.tg_user_id = %s AND p.article_number = %s
                    ),
                    current_qty AS (
                        SELECT COALESCE(c.quantity, 0) AS qty
                        FROM user_product up
                        LEFT JOIN cart c ON c.user_id = up.user_id AND c.product_id = up.product_id
                    ),
                    check_limit AS (
                        SELECT 
                            (cq.qty + %s) AS new_qty,
                            CASE 
                                WHEN up.prod_limit IS NULL THEN true
                                ELSE (cq.qty + %s) <= up.prod_limit
                            END AS within_limit
                        FROM user_product up, current_qty cq
                    )
                    INSERT INTO cart (user_id, product_id, quantity)
                    SELECT up.user_id, up.product_id, cq.qty + %s
                    FROM user_product up, current_qty cq, check_limit cl
                    WHERE cl.within_limit = true
                    ON CONFLICT (user_id, product_id) DO UPDATE
                    SET quantity = EXCLUDED.quantity,
                        updated_at = NOW()
                    RETURNING quantity;
                """, (tg_user_id, article_number, quantity, quantity, quantity))
                row = cur.fetchone()
                if row:
                    return AddToCartResult.SUCCESS, row["quantity"]
                else:
                    cur.execute("SELECT 1 FROM products WHERE article_number = %s", (article_number,))
                    if not cur.fetchone():
                        return AddToCartResult.PRODUCT_NOT_FOUND, 0
                    cur.execute("SELECT 1 FROM users WHERE tg_user_id = %s", (tg_user_id,))
                    if not cur.fetchone():
                        return AddToCartResult.USER_NOT_FOUND, 0
                    return AddToCartResult.LIMIT_EXCEEDED, 0
                
    def get_admin_contacts(self):
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT
                        tg_username,
                        phone
                    FROM users
                    WHERE is_admin;
                """)
                return cur.fetchone()
            
    def clear_cart(self, tg_user_id: int) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    DELETE FROM cart
                    WHERE user_id = (SELECT id FROM users WHERE tg_user_id = %s)
                """, (tg_user_id,))
                return cur.rowcount > 0
            
    def remove_cart_product(self, tg_user_id: int, article_number: int) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    DELETE FROM cart
                    USING users u, products p
                    WHERE cart.user_id = u.id
                    AND cart.product_id = p.id
                    AND u.tg_user_id = %s
                    AND p.article_number = %s
                    RETURNING cart.id
                """, (tg_user_id, article_number))
                return cur.fetchone() is not None
            
    def update_cart_quantity(self, tg_user_id: int, article_number: int, new_quantity: int) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                if new_quantity <= 0:
                    return self.remove_cart_product(tg_user_id, article_number)
                cur.execute("""
                    UPDATE cart
                    SET quantity = %s, updated_at = NOW()
                    WHERE user_id = (SELECT id FROM users WHERE tg_user_id = %s)
                    AND product_id = (SELECT id FROM products WHERE article_number = %s)
                    AND (
                        (SELECT prod_limit FROM products WHERE article_number = %s) IS NULL
                        OR %s <= (SELECT prod_limit FROM products WHERE article_number = %s)
                    )
                    RETURNING id
                """, (new_quantity, tg_user_id, article_number, article_number, new_quantity, article_number))
                return cur.fetchone() is not None
            
    def get_user_profile_data(self, tg_user_id: int) -> Tuple[str]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT 
                        u.full_name, 
                        u.phone,
                        COALESCE(d.company, '') AS company,
                        COALESCE(d.address, '') AS address
                    FROM users u
                    LEFT JOIN delivery_points d ON u.id = d.user_id
                    WHERE tg_user_id = %s
                """, (tg_user_id,))
                row = cur.fetchone()
                if row:
                    return (
                        row.get('full_name') or '', 
                        row.get('phone') or '', 
                        row.get('company') or '', 
                        row.get('address') or ''
                    )
                return ('', '', '', '')
            
    def update_user_full_name(self, tg_user_id: int, full_name: str) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    UPDATE users
                    SET full_name = %s, updated_at = NOW()
                    WHERE tg_user_id = %s
                    RETURNING id
                """, (full_name, tg_user_id))
                return cur.fetchone() is not None
            
    def update_user_phone(self, tg_user_id: int, phone: str) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    UPDATE users
                    SET phone = %s, updated_at = NOW()
                    WHERE tg_user_id = %s
                    RETURNING id
                """, (phone, tg_user_id))
                return cur.fetchone() is not None
            
    def update_delivery_company(self, tg_user_id: int, company: str) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    INSERT INTO delivery_points (user_id, company, address)
                    SELECT id, %s, ''
                    FROM users WHERE tg_user_id = %s
                    ON CONFLICT (user_id) DO UPDATE
                    SET company = EXCLUDED.company, updated_at = NOW()
                    RETURNING id
                """, (company, tg_user_id))
                return cur.fetchone() is not None

    def update_delivery_point_address(self, tg_user_id: int, address: str) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    INSERT INTO delivery_points (user_id, company, address)
                    SELECT id, '', %s
                    FROM users WHERE tg_user_id = %s
                    ON CONFLICT (user_id) DO UPDATE
                    SET address = EXCLUDED.address, updated_at = NOW()
                    RETURNING id
                """, (address, tg_user_id))
                return cur.fetchone() is not None
            
    def get_user_today_orders_count(self, tg_user_id: int) -> int:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT COUNT(*) AS cnt
                    FROM orders o
                    JOIN users u ON o.user_id = u.id
                    WHERE u.tg_user_id = %s
                        AND o.status NOT IN ('отменён', 'ошибка')
                        AND o.created_at >= DATE_TRUNC('day', NOW())
                """, (tg_user_id,))
                return cur.fetchone()['cnt']
            
    def can_user_create_order(self, tg_user_id: int, max_orders_per_day: int = 5) -> bool:
        today_orders = self.get_user_today_orders_count(tg_user_id)
        return today_orders < max_orders_per_day
    
    def get_user_tg_data(self, tg_user_id: int) -> str:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT
                        tg_username,
                        tg_full_name
                    FROM users
                    WHERE tg_user_id = %s
                """, (tg_user_id,))
                row = cur.fetchone()
                if row:
                    return (
                        row.get('tg_username') or '', 
                        row.get('tg_full_name') or '', 
                    )
                return ('', '')
    
    def create_order(
        self, 
        tg_user_id: int, 
        total_price: float,
        delivery_company: str, 
        delivery_point_address: str
    ) -> Optional[str]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    WITH 
                    cur_user AS (
                        SELECT id FROM users WHERE tg_user_id = %s
                    ),
                    inserted_order AS (
                        INSERT INTO orders (user_id, delivery_company_snapshot, delivery_address_snapshot,
                                            order_price, status, created_at, updated_at)
                        SELECT id, %s, %s, %s, 'на рассмотрении', NOW(), NOW()
                        FROM cur_user
                        RETURNING id
                    ),
                    moved_products AS (
                        INSERT INTO order_products (order_id, product_id, quantity, price_at_order)
                        SELECT (SELECT id FROM inserted_order),
                            p.id,
                            c.quantity,
                            p.price
                        FROM cart c
                        JOIN products p ON c.product_id = p.id
                        JOIN cur_user u ON c.user_id = u.id
                    ),
                    deleted_cart AS (
                        DELETE FROM cart
                        USING cur_user
                        WHERE cart.user_id = cur_user.id
                    )
                    SELECT id FROM inserted_order;
                """, (tg_user_id, delivery_company, delivery_point_address, total_price))
                row = cur.fetchone()
                return row['id'] if row else None
            
    def is_admin(self, tg_user_id: int) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("SELECT is_admin FROM users WHERE tg_user_id = %s", (tg_user_id,))
                row = cur.fetchone()
                return row['is_admin'] if row else False

    def get_admin_user_id(self) -> Optional[int]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT tg_user_id
                    FROM users
                    WHERE is_admin = true
                    LIMIT 1
                """)
                row = cur.fetchone()
                return row['tg_user_id'] if row else None  

    def set_delivery_price(self, order_id: str, delivery_price: float) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    UPDATE orders
                    SET delivery_price = %s
                    WHERE id = %s::uuid
                    RETURNING id
                """, (delivery_price, order_id))
                row = cur.fetchone()
                return row is not None   
            
    def get_order(self, order_id: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    SELECT 
                        o.id AS order_id,
                        u.tg_username,
                        u.tg_full_name,
                        u.full_name,
                        u.phone,
                        COALESCE(d.company, '') AS delivery_company,
                        COALESCE(d.address, '') AS delivery_point_address,
                        o.order_price,
                        o.delivery_price,
                        o.status,
                        o.created_at,
                        COALESCE(
                            (SELECT json_agg(
                                json_build_object(
                                    'name', p.name,
                                    'article_number', p.article_number,
                                    'quantity', op.quantity,
                                    'price_at_order', op.price_at_order,
                                    'category', p.category,
                                    'materials', COALESCE(
                                        (SELECT string_agg(m.name, ', ') 
                                        FROM product_materials pm 
                                        JOIN materials m ON pm.material_id = m.id 
                                        WHERE pm.product_id = p.id), ''),
                                    'production_time', p.production_time
                                )
                            )
                            FROM order_products op
                            JOIN products p ON op.product_id = p.id
                            WHERE op.order_id = o.id
                        ), '[]'::json) AS products
                    FROM orders o
                    JOIN users u ON o.user_id = u.id
                    LEFT JOIN delivery_points d ON u.id = d.user_id
                    WHERE o.id = %s::uuid
                """, (order_id,))
                row = cur.fetchone()
                if row:
                    return dict(row)
                return None
    
    def close(self):
        self.pool.closeall()
        self.logger.info("PostgreSQL connection pool closed")