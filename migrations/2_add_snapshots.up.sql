DELETE FROM delivery_points
WHERE id IN (
    SELECT id FROM (
        SELECT id, user_id,
               ROW_NUMBER() OVER (
                   PARTITION BY user_id 
                   ORDER BY is_default DESC, created_at DESC
               ) AS rn
        FROM delivery_points
    ) ranked
    WHERE rn > 1
);

ALTER TABLE delivery_points ADD CONSTRAINT unique_user_delivery UNIQUE (user_id);

ALTER TABLE orders ADD COLUMN delivery_company_snapshot VARCHAR(100);
ALTER TABLE orders ADD COLUMN delivery_address_snapshot TEXT;

ALTER TABLE delivery_points DROP COLUMN IF EXISTS is_default;