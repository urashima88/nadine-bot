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
            
    def register_user(self, tg_user_id: int, username: str = None, full_name: str = None) -> Optional[str]:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("""
                    INSERT INTO users (tg_user_id, tg_username, tg_full_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (tg_user_id) DO NOTHING
                    RETURNING id;            
                """, (tg_user_id, username, full_name))
                row = cur.fetchone()
                if row:
                    return row['id']
                
                cur.execute("SELECT id FROM users WHERE tg_user_id = %s", (tg_user_id,))
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
                    return self.remove_cart_item(tg_user_id, article_number)
                cur.execute("""
                    UPDATE cart
                    SET quantity = %s, updated_at = NOW()
                    WHERE user_id = (SELECT id FROM users WHERE tg_user_id = %s)
                    AND product_id = (SELECT id FROM products WHERE article_number = %s)
                    RETURNING id
                """, (new_quantity, tg_user_id, article_number))
                return cur.fetchone() is not None
                
    def close(self):
        self.pool.closeall()
        self.logger.info("PostgreSQL connection pool closed")