import pandas as pd
import duckdb
from pathlib import Path

# ==========================================
# E-COMMERCE SALES & CUSTOMER ANALYTICS
# ==========================================

DATA_DIR = Path("data")
OUTPUT_DIR = Path("python")

print("\nLoading datasets...\n")

# ==========================================
# 1. LOAD DATA
# ==========================================

orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")

print("Datasets loaded successfully!")

print(f"Orders: {len(orders):,}")
print(f"Order items: {len(order_items):,}")
print(f"Customers: {len(customers):,}")
print(f"Products: {len(products):,}")
print(f"Payments: {len(payments):,}")


# ==========================================
# 2. CREATE SQL CONNECTION
# ==========================================

con = duckdb.connect()

con.register("orders", orders)
con.register("order_items", order_items)
con.register("customers", customers)
con.register("products", products)
con.register("payments", payments)


# ==========================================
# 3. AGGREGATE PAYMENTS FIRST
# ==========================================

payment_summary_query = """
SELECT
    order_id,
    SUM(payment_value) AS total_payment_value
FROM payments
GROUP BY order_id
"""

payment_summary = con.execute(payment_summary_query).fetchdf()

con.register("payment_summary", payment_summary)

print("\nPayments aggregated successfully!")


# ==========================================
# 4. CREATE MASTER DATASET
# ==========================================

query = """
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,

    CAST(o.order_purchase_timestamp AS TIMESTAMP)
        AS order_date,

    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    oi.order_item_id,
    oi.product_id,
    oi.seller_id,

    oi.price,
    oi.freight_value,

    p.product_category_name,

    ps.total_payment_value

FROM orders o

LEFT JOIN customers c
    ON o.customer_id = c.customer_id

LEFT JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN payment_summary ps
    ON o.order_id = ps.order_id

WHERE o.order_status = 'delivered'
"""

master = con.execute(query).fetchdf()

print("\nMaster dataset created!")

print(f"Master rows: {len(master):,}")
print(f"Master columns: {len(master.columns)}")


# ==========================================
# 5. BUSINESS KPIs
# ==========================================

# Revenue should come from order item prices.
total_revenue = master["price"].sum()

# Count unique delivered orders.
total_orders = master["order_id"].nunique()

# Count unique customers.
total_customers = master["customer_unique_id"].nunique()

# Average Order Value.
aov = total_revenue / total_orders


# ==========================================
# 6. REPEAT CUSTOMERS
# ==========================================

customer_orders = (
    master
    .groupby("customer_unique_id")["order_id"]
    .nunique()
)

repeat_customers = (customer_orders > 1).sum()

repeat_rate = (
    repeat_customers / total_customers
) * 100


# ==========================================
# 7. PRINT BUSINESS KPIs
# ==========================================

print("\n")
print("=" * 60)
print("BUSINESS KPIs")
print("=" * 60)

print(f"Revenue: R${total_revenue:,.2f}")
print(f"Orders: {total_orders:,}")
print(f"Customers: {total_customers:,}")
print(f"AOV: R${aov:,.2f}")
print(f"Repeat Customers: {repeat_customers:,}")
print(f"Repeat Rate: {repeat_rate:.2f}%")


# ==========================================
# 8. MONTHLY SALES
# ==========================================

monthly_sales = (
    master
    .groupby(master["order_date"].dt.to_period("M"))
    .agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_unique_id", "nunique")
    )
    .reset_index()
)

monthly_sales["order_date"] = (
    monthly_sales["order_date"].astype(str)
)


# ==========================================
# 9. CATEGORY PERFORMANCE
# ==========================================

category_sales = (
    master
    .groupby("product_category_name")
    .agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
        units=("order_item_id", "count")
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)


# ==========================================
# 10. REGIONAL PERFORMANCE
# ==========================================

regional_sales = (
    master
    .groupby("customer_state")
    .agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_unique_id", "nunique")
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)


# ==========================================
# 11. SAVE DATASETS
# ==========================================

master.to_csv(
    OUTPUT_DIR / "master_ecommerce_data.csv",
    index=False
)

monthly_sales.to_csv(
    OUTPUT_DIR / "monthly_sales.csv",
    index=False
)

category_sales.to_csv(
    OUTPUT_DIR / "category_sales.csv",
    index=False
)

regional_sales.to_csv(
    OUTPUT_DIR / "regional_sales.csv",
    index=False
)


# ==========================================
# 12. SHOW IMPORTANT RESULTS
# ==========================================

print("\n")
print("=" * 60)
print("TOP 10 PRODUCT CATEGORIES")
print("=" * 60)

print(
    category_sales.head(10).to_string(index=False)
)


print("\n")
print("=" * 60)
print("REGIONAL PERFORMANCE")
print("=" * 60)

print(
    regional_sales.to_string(index=False)
)


# ==========================================
# 13. FINISH
# ==========================================

print("\n")
print("=" * 60)
print("PROJECT ANALYSIS COMPLETED SUCCESSFULLY!")
print("=" * 60)

print("\nFiles created:")

print("1. master_ecommerce_data.csv")
print("2. monthly_sales.csv")
print("3. category_sales.csv")
print("4. regional_sales.csv")

con.close()