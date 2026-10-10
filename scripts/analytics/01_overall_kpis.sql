
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(price)::numeric, 2) AS total_revenue,
    ROUND(SUM(freight_value)::numeric, 2) AS total_freight,
    ROUND(SUM(total_item_value)::numeric, 2) AS total_sales_value,
    ROUND(
        (SUM(total_item_value) / COUNT(DISTINCT order_id))::numeric,
        2
    ) AS average_order_value
FROM fact_sales;