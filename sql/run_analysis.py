import duckdb
from pathlib import Path

# ==========================================
# E-COMMERCE SQL ANALYSIS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "python" / "master_ecommerce_data.csv"

con = duckdb.connect()

# Load CSV as a SQL table
con.execute(f"""
    CREATE OR REPLACE VIEW master_ecommerce_data AS
    SELECT *
    FROM read_csv_auto('{DATA_FILE}')
""")

print("\nSQL ANALYSIS STARTED")
print("=" * 60)


# ==========================================
# 1. TOTAL REVENUE
# ==========================================

result = con.execute("""
    SELECT
        SUM(price) AS total_revenue
    FROM master_ecommerce_data
""").fetchdf()

print("\n1. TOTAL REVENUE")
print(result)


# ==========================================
# 2. TOTAL ORDERS
# ==========================================

result = con.execute("""
    SELECT
        COUNT(DISTINCT order_id) AS total_orders
    FROM master_ecommerce_data
""").fetchdf()

print("\n2. TOTAL ORDERS")
print(result)


# ==========================================
# 3. TOTAL CUSTOMERS
# ==========================================

result = con.execute("""
    SELECT
        COUNT(DISTINCT customer_unique_id) AS total_customers
    FROM master_ecommerce_data
""").fetchdf()

print("\n3. TOTAL CUSTOMERS")
print(result)


# ==========================================
# 4. AVERAGE ORDER VALUE
# ==========================================

result = con.execute("""
    SELECT
        SUM(price) / COUNT(DISTINCT order_id) AS average_order_value
    FROM master_ecommerce_data
""").fetchdf()

print("\n4. AVERAGE ORDER VALUE")
print(result)


# ==========================================
# 5. TOP 10 PRODUCT CATEGORIES
# ==========================================

result = con.execute("""
    SELECT
        product_category_name,
        SUM(price) AS revenue,
        COUNT(DISTINCT order_id) AS orders,
        COUNT(order_item_id) AS units
    FROM master_ecommerce_data
    WHERE product_category_name IS NOT NULL
    GROUP BY product_category_name
    ORDER BY revenue DESC
    LIMIT 10
""").fetchdf()

print("\n5. TOP 10 PRODUCT CATEGORIES")
print(result.to_string(index=False))


# ==========================================
# 6. TOP 10 STATES
# ==========================================

result = con.execute("""
    SELECT
        customer_state,
        SUM(price) AS revenue,
        COUNT(DISTINCT order_id) AS orders,
        COUNT(DISTINCT customer_unique_id) AS customers
    FROM master_ecommerce_data
    GROUP BY customer_state
    ORDER BY revenue DESC
    LIMIT 10
""").fetchdf()

print("\n6. TOP 10 STATES")
print(result.to_string(index=False))


# ==========================================
# 7. MONTHLY REVENUE
# ==========================================

result = con.execute("""
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(price) AS revenue,
        COUNT(DISTINCT order_id) AS orders
    FROM master_ecommerce_data
    GROUP BY month
    ORDER BY month
""").fetchdf()

print("\n7. MONTHLY REVENUE")
print(result.to_string(index=False))


# ==========================================
# 8. CUSTOMER ORDER FREQUENCY
# ==========================================

result = con.execute("""
    SELECT
        order_count,
        COUNT(*) AS customers
    FROM (
        SELECT
            customer_unique_id,
            COUNT(DISTINCT order_id) AS order_count
        FROM master_ecommerce_data
        GROUP BY customer_unique_id
    )
    GROUP BY order_count
    ORDER BY order_count
""").fetchdf()

print("\n8. CUSTOMER ORDER FREQUENCY")
print(result.to_string(index=False))


# ==========================================
# 9. TOP CUSTOMERS
# ==========================================

result = con.execute("""
    SELECT
        customer_unique_id,
        SUM(price) AS revenue,
        COUNT(DISTINCT order_id) AS orders
    FROM master_ecommerce_data
    GROUP BY customer_unique_id
    ORDER BY revenue DESC
    LIMIT 10
""").fetchdf()

print("\n9. TOP CUSTOMERS")
print(result.to_string(index=False))


print("\n")
print("=" * 60)
print("SQL ANALYSIS COMPLETED")
print("=" * 60)

con.close()