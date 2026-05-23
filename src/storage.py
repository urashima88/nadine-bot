from logging import Logger
from typing import List, Tuple, Optional, Any, Dict
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool, sql, extras

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
            
    def get_cart_items(self, tg_user_id: int) -> List[Dict[str, Any]]:
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
                        COALESCE(string_agg(m.name, ', '), '') AS materials_list
                    FROM products p
                    LEFT JOIN product_materials pm ON p.id = pm.product_id
                    LEFT JOIN materials m ON pm.material_id = m.id
                    WHERE p.article_number = %s
                    GROUP BY p.id;
                """, (article_number,))
                return cur.fetchone()
    
    def add_to_cart(self, tg_user_id: int, article_number: int, quantity: int = 1) -> bool:
        with self._get_connection() as conn:
            with self._get_cursor(conn) as cur:
                cur.execute("SELECT id FROM users WHERE tg_user_id = %s", (tg_user_id,))
                user_row = cur.fetchone()
                if not user_row:
                    self.logger.warning(f"User {tg_user_id} not found")
                    return False
                user_id = user_row['id']
                
                cur.execute("SELECT id FROM products WHERE article_number = %s", (article_number,))
                product_row = cur.fetchone()
                if not product_row:
                    self.logger.warning(f"Product with article {article_number} not found")
                    return False
                product_id = product_row['id']
                
                cur.execute("""
                    SELECT id, quantity 
                    FROM cart 
                    WHERE user_id = %s AND product_id = %s
                """, (user_id, product_id))
                existing = cur.fetchone()
                
                if existing:
                    new_quantity = existing['quantity'] + quantity
                    cur.execute("""
                        UPDATE cart 
                        SET quantity = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (new_quantity, existing['id']))
                else:
                    cur.execute("""
                        INSERT INTO cart (user_id, product_id, quantity)
                        VALUES (%s, %s, %s)
                    """, (user_id, product_id, quantity))
                
                return True 
    
    def close(self):
        self.pool.closeall()
        self.logger.info("PostgreSQL connection pool closed")