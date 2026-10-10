

SELECT
    COALESCE(p.category_name_english, 'Unknown') AS category,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(f.price)::numeric, 2) AS total_revenue,
    ROUND(SUM(f.freight_value)::numeric, 2) AS total_freight,
    ROUND(SUM(f.total_item_value)::numeric, 2) AS total_sales_value
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.category_name_english
ORDER BY
    total_sales_value DESC;