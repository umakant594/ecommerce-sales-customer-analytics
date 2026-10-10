import pandas as pd
from pathlib import Path

# ==========================================
# CUSTOMER RFM ANALYSIS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "python" / "master_ecommerce_data.csv"
OUTPUT_FILE = BASE_DIR / "python" / "customer_segments.csv"

print("\nLoading master dataset...")

df = pd.read_csv(DATA_FILE)

df["order_date"] = pd.to_datetime(df["order_date"])

print(f"Rows loaded: {len(df):,}")


# ==========================================
# 1. SET ANALYSIS DATE
# ==========================================

analysis_date = df["order_date"].max()

print(f"Analysis date: {analysis_date.date()}")


# ==========================================
# 2. CREATE CUSTOMER RFM
# ==========================================

rfm = (
    df.groupby("customer_unique_id")
    .agg(
        last_purchase=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("price", "sum")
    )
    .reset_index()
)


# ==========================================
# 3. CALCULATE RECENCY
# ==========================================

rfm["recency"] = (
    analysis_date - rfm["last_purchase"]
).dt.days


# ==========================================
# 4. CREATE RFM SCORES
# ==========================================

rfm["R_score"] = pd.qcut(
    rfm["recency"],
    4,
    labels=[4, 3, 2, 1],
    duplicates="drop"
).astype(int)

rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    4,
    labels=[1, 2, 3, 4]
).astype(int)

rfm["M_score"] = pd.qcut(
    rfm["monetary"].rank(method="first"),
    4,
    labels=[1, 2, 3, 4]
).astype(int)


# ==========================================
# 5. TOTAL RFM SCORE
# ==========================================

rfm["RFM_score"] = (
    rfm["R_score"]
    + rfm["F_score"]
    + rfm["M_score"]
)


# ==========================================
# 6. CUSTOMER SEGMENTS
# ==========================================

def segment_customer(row):

    if (
        row["R_score"] >= 3
        and row["F_score"] >= 3
        and row["M_score"] >= 3
    ):
        return "Champions"

    elif (
        row["R_score"] >= 3
        and row["F_score"] >= 2
    ):
        return "Loyal Customers"

    elif (
        row["R_score"] >= 3
        and row["F_score"] <= 2
    ):
        return "Potential Loyalists"

    elif (
        row["R_score"] <= 2
        and row["F_score"] >= 2
    ):
        return "At Risk"

    elif (
        row["R_score"] <= 2
        and row["F_score"] == 1
    ):
        return "Lost / Inactive"

    else:
        return "Other"


rfm["segment"] = rfm.apply(
    segment_customer,
    axis=1
)


# ==========================================
# 7. SEGMENT SUMMARY
# ==========================================

segment_summary = (
    rfm
    .groupby("segment")
    .agg(
        customers=("customer_unique_id", "count"),
        revenue=("monetary", "sum"),
        avg_revenue=("monetary", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_recency=("recency", "mean")
    )
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)


# ==========================================
# 8. PRINT RESULTS
# ==========================================

print("\n")
print("=" * 70)
print("CUSTOMER SEGMENTATION")
print("=" * 70)

print(
    segment_summary.to_string(index=False)
)


print("\n")
print("=" * 70)
print("CUSTOMER SEGMENT PERCENTAGE")
print("=" * 70)

segment_summary["customer_percentage"] = (
    segment_summary["customers"]
    / len(rfm)
    * 100
)

print(
    segment_summary[
        ["segment", "customers", "customer_percentage"]
    ].to_string(index=False)
)


# ==========================================
# 9. SAVE RESULTS
# ==========================================

rfm.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n")
print("=" * 70)
print("RFM ANALYSIS COMPLETED")
print("=" * 70)

print(f"\nFile created:")
print("customer_segments.csv")