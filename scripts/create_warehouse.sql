

-- ============================================
-- DIMENSION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    customer_unique_id TEXT,
    customer_zip_code BIGINT,
    customer_city TEXT,
    customer_state TEXT
);


CREATE TABLE IF NOT EXISTS dim_category (
    category_key BIGINT PRIMARY KEY,
    category_name_original TEXT,
    category_name TEXT
);


CREATE TABLE IF NOT EXISTS dim_product (
    product_key BIGINT PRIMARY KEY,
    product_id TEXT NOT NULL,
    category_key BIGINT,
    product_category_name_original TEXT,
    category_name_english TEXT,
    product_name_length DOUBLE PRECISION,
    product_description_length DOUBLE PRECISION,
    product_photos_qty DOUBLE PRECISION,
    product_weight_g DOUBLE PRECISION,
    product_length_cm DOUBLE PRECISION,
    product_height_cm DOUBLE PRECISION,
    product_width_cm DOUBLE PRECISION
);


CREATE TABLE IF NOT EXISTS dim_seller (
    seller_key BIGINT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    seller_zip_code BIGINT,
    seller_city TEXT,
    seller_state TEXT
);


CREATE TABLE IF NOT EXISTS dim_date (
    date_key BIGINT PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    quarter TEXT,
    month INTEGER,
    month_name TEXT,
    day INTEGER,
    day_name TEXT,
    day_of_week INTEGER,
    week_of_year BIGINT
);


-- ============================================
-- FACT TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGINT PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_item_id BIGINT,
    customer_key BIGINT,
    product_key BIGINT,
    seller_key BIGINT,
    date_key BIGINT,
    order_status TEXT,
    shipping_limit_date TEXT,
    order_purchase_timestamp TIMESTAMP,
    price DOUBLE PRECISION,
    freight_value DOUBLE PRECISION,
    total_item_value DOUBLE PRECISION
);


CREATE TABLE IF NOT EXISTS fact_payments (
    payment_key BIGINT PRIMARY KEY,
    order_id TEXT NOT NULL,
    payment_sequential BIGINT,
    customer_key BIGINT,
    date_key BIGINT,
    order_status TEXT,
    payment_type TEXT,
    payment_installments BIGINT,
    payment_value DOUBLE PRECISION,
    order_purchase_timestamp TIMESTAMP
);


CREATE TABLE IF NOT EXISTS fact_reviews (
    review_key BIGINT PRIMARY KEY,
    review_id TEXT,
    order_id TEXT,
    customer_key BIGINT,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);


-- ============================================
-- ANALYTICS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS customer_360 (
    customer_key BIGINT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    customer_city TEXT,
    customer_state TEXT,
    total_orders DOUBLE PRECISION,
    total_items DOUBLE PRECISION,
    total_spending DOUBLE PRECISION,
    average_order_value DOUBLE PRECISION,
    first_purchase_date TIMESTAMP,
    last_purchase_date TIMESTAMP,
    customer_lifetime_days DOUBLE PRECISION,
    average_review_score DOUBLE PRECISION,
    total_reviews BIGINT,
    total_payment_value DOUBLE PRECISION,
    payment_transactions DOUBLE PRECISION,
    preferred_payment_type TEXT
);