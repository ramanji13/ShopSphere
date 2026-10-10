

SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(f.price)::numeric, 2) AS total_revenue,
    ROUND(SUM(f.freight_value)::numeric, 2) AS total_freight,
    ROUND(SUM(f.total_item_value)::numeric, 2) AS total_sales_value
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;