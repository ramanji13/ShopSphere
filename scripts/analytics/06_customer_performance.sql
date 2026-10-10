
SELECT
    customer_id,
    customer_city,
    customer_state,
    total_orders,
    total_items,
    ROUND(total_spending::numeric, 2) AS total_spending,
    ROUND(average_order_value::numeric, 2) AS average_order_value,
    ROUND(average_review_score::numeric, 2) AS average_review_score,
    total_reviews,
    preferred_payment_type
FROM customer_360
WHERE total_spending IS NOT NULL
ORDER BY
    total_spending DESC
LIMIT 10;