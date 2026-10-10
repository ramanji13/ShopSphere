

-- ============================================
-- 1. Verify Row Counts
-- ============================================

SELECT
    'dim_customer' AS table_name,
    COUNT(*) AS row_count
FROM dim_customer

UNION ALL

SELECT 'dim_category', COUNT(*)
FROM dim_category

UNION ALL

SELECT 'dim_product', COUNT(*)
FROM dim_product

UNION ALL

SELECT 'dim_seller', COUNT(*)
FROM dim_seller

UNION ALL

SELECT 'dim_date', COUNT(*)
FROM dim_date

UNION ALL

SELECT 'fact_sales', COUNT(*)
FROM fact_sales

UNION ALL

SELECT 'fact_payments', COUNT(*)
FROM fact_payments

UNION ALL

SELECT 'fact_reviews', COUNT(*)
FROM fact_reviews

UNION ALL

SELECT 'customer_360', COUNT(*)
FROM customer_360

ORDER BY table_name;


-- ============================================
-- 2. Check Duplicate Keys
-- ============================================

SELECT
    'dim_customer' AS table_name,
    COUNT(*) - COUNT(DISTINCT customer_key) AS duplicate_keys
FROM dim_customer

UNION ALL

SELECT
    'dim_category',
    COUNT(*) - COUNT(DISTINCT category_key)
FROM dim_category

UNION ALL

SELECT
    'dim_product',
    COUNT(*) - COUNT(DISTINCT product_key)
FROM dim_product

UNION ALL

SELECT
    'dim_seller',
    COUNT(*) - COUNT(DISTINCT seller_key)
FROM dim_seller

UNION ALL

SELECT
    'dim_date',
    COUNT(*) - COUNT(DISTINCT date_key)
FROM dim_date

UNION ALL

SELECT
    'fact_sales',
    COUNT(*) - COUNT(DISTINCT sales_key)
FROM fact_sales

UNION ALL

SELECT
    'fact_payments',
    COUNT(*) - COUNT(DISTINCT payment_key)
FROM fact_payments

UNION ALL

SELECT
    'fact_reviews',
    COUNT(*) - COUNT(DISTINCT review_key)
FROM fact_reviews

UNION ALL

SELECT
    'customer_360',
    COUNT(*) - COUNT(DISTINCT customer_key)
FROM customer_360

ORDER BY table_name;


-- ============================================
-- 3. Check NULL Foreign Keys in fact_sales
-- ============================================

SELECT
    'fact_sales_customer_key' AS check_name,
    COUNT(*) AS invalid_rows
FROM fact_sales
WHERE customer_key IS NULL

UNION ALL

SELECT
    'fact_sales_product_key',
    COUNT(*)
FROM fact_sales
WHERE product_key IS NULL

UNION ALL

SELECT
    'fact_sales_seller_key',
    COUNT(*)
FROM fact_sales
WHERE seller_key IS NULL

UNION ALL

SELECT
    'fact_sales_date_key',
    COUNT(*)
FROM fact_sales
WHERE date_key IS NULL;


-- ============================================
-- 4. Check fact_sales Relationships
-- ============================================

SELECT
    'sales_to_customer' AS check_name,
    COUNT(*) AS invalid_rows
FROM fact_sales f
LEFT JOIN dim_customer c
    ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL

UNION ALL

SELECT
    'sales_to_product',
    COUNT(*)
FROM fact_sales f
LEFT JOIN dim_product p
    ON f.product_key = p.product_key
WHERE p.product_key IS NULL

UNION ALL

SELECT
    'sales_to_seller',
    COUNT(*)
FROM fact_sales f
LEFT JOIN dim_seller s
    ON f.seller_key = s.seller_key
WHERE s.seller_key IS NULL

UNION ALL

SELECT
    'sales_to_date',
    COUNT(*)
FROM fact_sales f
LEFT JOIN dim_date d
    ON f.date_key = d.date_key
WHERE d.date_key IS NULL;


-- ============================================
-- 5. Validate customer_360
-- ============================================

SELECT
    'customer_360_customer_key_null' AS check_name,
    COUNT(*) AS invalid_rows
FROM customer_360
WHERE customer_key IS NULL

UNION ALL

SELECT
    'customer_360_customer_id_null',
    COUNT(*)
FROM customer_360
WHERE customer_id IS NULL;