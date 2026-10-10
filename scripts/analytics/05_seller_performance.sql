
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(f.price)::numeric, 2) AS total_revenue,
    ROUND(SUM(f.freight_value)::numeric, 2) AS total_freight,
    ROUND(SUM(f.total_item_value)::numeric, 2) AS total_sales_value
FROM fact_sales f
JOIN dim_seller s
    ON f.seller_key = s.seller_key
GROUP BY
    s.seller_id,
    s.seller_city,
    s.seller_state
ORDER BY
    total_sales_value DESC
LIMIT 10;