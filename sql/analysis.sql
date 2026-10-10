-- ==========================================
-- E-COMMERCE SALES & CUSTOMER ANALYTICS
-- SQL ANALYSIS
-- ==========================================


-- 1. TOTAL REVENUE

SELECT
    ROUND(SUM(price), 2) AS total_revenue
FROM master_ecommerce_data;


-- 2. TOTAL ORDERS

SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM master_ecommerce_data;


-- 3. TOTAL CUSTOMERS

SELECT
    COUNT(DISTINCT customer_unique_id) AS total_customers
FROM master_ecommerce_data;


-- 4. AVERAGE ORDER VALUE

SELECT
    ROUND(
        SUM(price) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM master_ecommerce_data;


-- 5. REPEAT CUSTOMERS

SELECT
    COUNT(*) AS repeat_customers
FROM (
    SELECT
        customer_unique_id
    FROM master_ecommerce_data
    GROUP BY customer_unique_id
    HAVING COUNT(DISTINCT order_id) > 1
) AS customers;


-- 6. CUSTOMER ORDER FREQUENCY

SELECT
    customer_unique_id,
    COUNT(DISTINCT order_id) AS number_of_orders
FROM master_ecommerce_data
GROUP BY customer_unique_id
ORDER BY number_of_orders DESC;


-- 7. TOP 10 PRODUCT CATEGORIES

SELECT
    product_category_name,
    ROUND(SUM(price), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(order_item_id) AS units_sold
FROM master_ecommerce_data
WHERE product_category_name IS NOT NULL
GROUP BY product_category_name
ORDER BY revenue DESC
LIMIT 10;


-- 8. BOTTOM 10 PRODUCT CATEGORIES

SELECT
    product_category_name,
    ROUND(SUM(price), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(order_item_id) AS units_sold
FROM master_ecommerce_data
WHERE product_category_name IS NOT NULL
GROUP BY product_category_name
ORDER BY revenue ASC
LIMIT 10;


-- 9. REGIONAL PERFORMANCE

SELECT
    customer_state,
    ROUND(SUM(price), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_unique_id) AS customers
FROM master_ecommerce_data
GROUP BY customer_state
ORDER BY revenue DESC;


-- 10. MONTHLY PERFORMANCE

SELECT
    DATE_TRUNC(
        'month',
        order_date
    ) AS month,
    ROUND(SUM(price), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_unique_id) AS customers
FROM master_ecommerce_data
GROUP BY month
ORDER BY month;


-- 11. TOP 10 PRODUCTS BY REVENUE

SELECT
    product_id,
    ROUND(SUM(price), 2) AS revenue,
    COUNT(order_item_id) AS units_sold
FROM master_ecommerce_data
GROUP BY product_id
ORDER BY revenue DESC
LIMIT 10;


-- 12. TOP CUSTOMERS BY REVENUE

SELECT
    customer_unique_id,
    ROUND(SUM(price), 2) AS customer_revenue,
    COUNT(DISTINCT order_id) AS orders
FROM master_ecommerce_data
GROUP BY customer_unique_id
ORDER BY customer_revenue DESC
LIMIT 20;