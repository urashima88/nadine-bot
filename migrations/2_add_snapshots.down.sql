ALTER TABLE delivery_points DROP CONSTRAINT IF EXISTS unique_user_delivery;
ALTER TABLE orders DROP COLUMN IF EXISTS delivery_company_snapshot;
ALTER TABLE orders DROP COLUMN IF EXISTS delivery_address_snapshot;
ALTER TABLE delivery_points ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;