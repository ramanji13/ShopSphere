
-- 1. Overall sales totals
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(price)::numeric, 2) AS total_revenue,
    ROUND(SUM(freight_value)::numeric, 2) AS total_freight,
    ROUND(SUM(total_item_value)::numeric, 2) AS total_sales_value
FROM fact_sales;


-- 2. Monthly sales coverage
SELECT
    COUNT(*) AS monthly_rows,
    MIN(year) AS first_year,
    MAX(year) AS last_year
FROM (
    SELECT
        d.year,
        d.month
    FROM fact_sales f
    JOIN dim_date d
        ON f.date_key = d.date_key
    GROUP BY
        d.year,
        d.month
) monthly;


-- 3. Product performance
SELECT
    COUNT(*) AS product_rows
FROM (
    SELECT
        p.product_id
    FROM fact_sales f
    JOIN dim_product p
        ON f.product_key = p.product_key
    GROUP BY
        p.product_id,
        p.category_name_english
) products;


-- 4. Category performance
SELECT
    COUNT(*) AS category_rows
FROM (
    SELECT
        p.category_name_english
    FROM fact_sales f
    JOIN dim_product p
        ON f.product_key = p.product_key
    GROUP BY
        p.category_name_english
) categories;


-- 5. Seller performance
SELECT
    COUNT(*) AS seller_rows
FROM (
    SELECT
        s.seller_id
    FROM fact_sales f
    JOIN dim_seller s
        ON f.seller_key = s.seller_key
    GROUP BY
        s.seller_id,
        s.seller_city,
        s.seller_state
) sellers;


-- 6. Customer performance
SELECT
    COUNT(*) AS customers_with_spending,
    ROUND(MAX(total_spending)::numeric, 2) AS highest_customer_spending
FROM customer_360
WHERE total_spending IS NOT NULL;