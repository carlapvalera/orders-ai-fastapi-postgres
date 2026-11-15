CREATE VIEW sales_by_month_country AS
SELECT
    DATE_TRUNC('month', order_date)::DATE AS month,
    country,
    ROUND(SUM(amount), 2) AS total_sales,
    COUNT(*) AS order_count
FROM orders
WHERE status <> 'cancelled'
GROUP BY 1, 2;

CREATE VIEW top_customers AS
SELECT
    customer,
    ROUND(SUM(amount), 2) AS total_spend,
    COUNT(*) AS order_count
FROM orders
WHERE status <> 'cancelled'
GROUP BY customer
ORDER BY total_spend DESC
LIMIT 10;

