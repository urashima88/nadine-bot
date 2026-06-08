ALTER TABLE orders ADD COLUMN order_number BIGSERIAL NOT NULL;

CREATE INDEX idx_orders_order_number ON orders(order_number);