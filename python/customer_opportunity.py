import pandas as pd
from pathlib import Path

# ==========================================
# CUSTOMER OPPORTUNITY ANALYSIS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_FILE = BASE_DIR / "python" / "master_ecommerce_data.csv"
RFM_FILE = BASE_DIR / "python" / "customer_segments.csv"

print("\nLoading datasets...")

master = pd.read_csv(MASTER_FILE)
rfm = pd.read_csv(RFM_FILE)

print(f"Master rows: {len(master):,}")
print(f"RFM customers: {len(rfm):,}")


# ==========================================
# 1. MERGE CUSTOMER SEGMENTS
# ==========================================

df = master.merge(
    rfm[
        [
            "customer_unique_id",
            "segment"
        ]
    ],
    on="customer_unique_id",
    how="left"
)


# ==========================================
# 2. AT-RISK BY CATEGORY
# ==========================================

at_risk_category = (
    df[df["segment"] == "At Risk"]
    .groupby("product_category_name")
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


print("\n")
print("=" * 70)
print("AT-RISK CUSTOMERS — TOP CATEGORIES")
print("=" * 70)

print(
    at_risk_category
    .head(10)
    .to_string(index=False)
)


# ==========================================
# 3. AT-RISK BY STATE
# ==========================================

at_risk_state = (
    df[df["segment"] == "At Risk"]
    .groupby("customer_state")
    .agg(
        revenue=("price", "sum"),
        customers=("customer_unique_id", "nunique"),
        orders=("order_id", "nunique")
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)


print("\n")
print("=" * 70)
print("AT-RISK CUSTOMERS — TOP STATES")
print("=" * 70)

print(
    at_risk_state
    .head(10)
    .to_string(index=False)
)


# ==========================================
# 4. CHAMPIONS BY CATEGORY
# ==========================================

champion_category = (
    df[df["segment"] == "Champions"]
    .groupby("product_category_name")
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


print("\n")
print("=" * 70)
print("CHAMPIONS — TOP CATEGORIES")
print("=" * 70)

print(
    champion_category
    .head(10)
    .to_string(index=False)
)


# ==========================================
# 5. SAVE RESULTS
# ==========================================

at_risk_category.to_csv(
    BASE_DIR / "python" / "at_risk_category.csv",
    index=False
)

at_risk_state.to_csv(
    BASE_DIR / "python" / "at_risk_state.csv",
    index=False
)

champion_category.to_csv(
    BASE_DIR / "python" / "champion_category.csv",
    index=False
)


print("\n")
print("=" * 70)
print("CUSTOMER OPPORTUNITY ANALYSIS COMPLETED")
print("=" * 70)

print("\nFiles created:")
print("1. at_risk_category.csv")
print("2. at_risk_state.csv")
print("3. champion_category.csv")