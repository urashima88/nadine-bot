DROP TRIGGER IF EXISTS update_products_updated_at ON products;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_delivery_points_updated_at ON delivery_points;
DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
DROP TRIGGER IF EXISTS update_cart_updated_at ON cart;

DROP FUNCTION IF EXISTS update_updated_at_column();
DROP FUNCTION IF EXISTS can_user_order(UUID, INTEGER);

DROP TABLE IF EXISTS order_products CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS order_attempts CASCADE;
DROP TABLE IF EXISTS cart CASCADE;
DROP TABLE IF EXISTS delivery_points CASCADE;
DROP TABLE IF EXISTS product_materials CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;