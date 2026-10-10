import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

print("Loading dashboard data...")

# Load master dataset
master = pd.read_csv(
    BASE_DIR / "python" / "master_ecommerce_data.csv"
)

# Load original orders dataset
orders = pd.read_csv(
    BASE_DIR / "data" / "olist_orders_dataset.csv"
)

# Load category translation
translation = pd.read_csv(
    BASE_DIR / "data" / "product_category_name_translation.csv"
)

# Load customer segments
segments = pd.read_csv(
    BASE_DIR / "python" / "customer_segments.csv"
)

print(f"Master rows: {len(master):,}")
print(f"Orders rows: {len(orders):,}")
print(f"Translation rows: {len(translation):,}")
print(f"Customer segments: {len(segments):,}")


# --------------------------------------------------
# 1. ADD ORDER DATE
# --------------------------------------------------

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

# Keep only the columns needed from orders
order_dates = orders[
    ["order_id", "order_purchase_timestamp"]
].copy()

master = master.merge(
    order_dates,
    on="order_id",
    how="left"
)


# --------------------------------------------------
# 2. TRANSLATE PRODUCT CATEGORIES
# --------------------------------------------------

master = master.merge(
    translation,
    on="product_category_name",
    how="left"
)

master["product_category_english"] = (
    master["product_category_name_english"]
    .fillna(master["product_category_name"])
)


# --------------------------------------------------
# 3. ADD CUSTOMER SEGMENTS
# --------------------------------------------------

master = master.merge(
    segments[["customer_unique_id", "segment"]],
    on="customer_unique_id",
    how="left"
)


# --------------------------------------------------
# 4. CREATE MONTH COLUMN
# --------------------------------------------------

master["month"] = (
    master["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)


# --------------------------------------------------
# 5. SELECT DASHBOARD COLUMNS
# --------------------------------------------------

dashboard_columns = [
    "order_id",
    "customer_unique_id",
    "customer_state",
    "order_status",
    "order_purchase_timestamp",
    "month",
    "product_category_english",
    "price",
    "freight_value",
    "segment"
]

dashboard = master[dashboard_columns].copy()


# --------------------------------------------------
# 6. SAVE FINAL DATASET
# --------------------------------------------------

output_file = (
    BASE_DIR / "python" / "dashboard_data.csv"
)

dashboard.to_csv(
    output_file,
    index=False
)


print("\n" + "=" * 70)
print("DASHBOARD DATA PREPARED")
print("=" * 70)

print(f"Rows: {len(dashboard):,}")
print(f"Columns: {len(dashboard.columns)}")

print("\nColumns:")
print(dashboard.columns.tolist())

print("\nSample:")
print(dashboard.head().to_string(index=False))

print("\nSaved to:")
print(output_file)