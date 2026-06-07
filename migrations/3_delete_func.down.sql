ALTER TABLE orders ADD COLUMN delivery_point_id UUID;

CREATE OR REPLACE FUNCTION can_user_order (
    p_user_id UUID,
    p_max_orders_per_24h INTEGER DEFAULT 5
) RETURNS BOOLEAN AS $$
DECLARE
    v_recent_orders INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_recent_orders
    FROM order_attempts
    WHERE user_id = p_user_id
    AND attempted_at >= NOW() - INTERVAL '24 hours';
    RETURN v_recent_orders < p_max_orders_per_24h;
END;
$$ LANGUAGE plpgsql;