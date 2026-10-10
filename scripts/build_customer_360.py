from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

GOLD_DIR = BASE_DIR / "data" / "gold"

DIM_CUSTOMER_PATH = (
    GOLD_DIR
    / "dimensions"
    / "dim_customer"
    / "data.parquet"
)

FACT_SALES_PATH = (
    GOLD_DIR
    / "facts"
    / "fact_sales"
    / "data.parquet"
)

FACT_PAYMENTS_PATH = (
    GOLD_DIR
    / "facts"
    / "fact_payments"
    / "data.parquet"
)

FACT_REVIEWS_PATH = (
    GOLD_DIR
    / "facts"
    / "fact_reviews"
    / "data.parquet"
)

OUTPUT_DIR = (
    GOLD_DIR
    / "analytics"
    / "customer_360"
)


print("Reading dim_customer...")
customers = pd.read_parquet(DIM_CUSTOMER_PATH)

print("Reading fact_sales...")
sales = pd.read_parquet(FACT_SALES_PATH)

print("Reading fact_payments...")
payments = pd.read_parquet(FACT_PAYMENTS_PATH)

print("Reading fact_reviews...")
reviews = pd.read_parquet(FACT_REVIEWS_PATH)


# =========================================================
# 1. SALES SUMMARY
# =========================================================

print("\nBuilding sales summary...")

sales_summary = (
    sales.groupby("customer_key")
    .agg(
        total_orders=("order_id", "nunique"),
        total_items=("order_item_id", "count"),
        total_spending=("total_item_value", "sum"),
        first_purchase_date=("order_purchase_timestamp", "min"),
        last_purchase_date=("order_purchase_timestamp", "max"),
    )
    .reset_index()
)

sales_summary["average_order_value"] = (
    sales_summary["total_spending"]
    / sales_summary["total_orders"]
)


# =========================================================
# 2. PAYMENT SUMMARY
# =========================================================

print("Building payment summary...")

payment_summary = (
    payments.groupby("customer_key")
    .agg(
        total_payment_value=("payment_value", "sum"),
        payment_transactions=("payment_key", "count"),
    )
    .reset_index()
)


# =========================================================
# 3. PREFERRED PAYMENT TYPE
# =========================================================

print("Finding preferred payment type...")

payment_type_counts = (
    payments.groupby(
        ["customer_key", "payment_type"]
    )
    .size()
    .reset_index(name="transaction_count")
)

payment_type_counts = payment_type_counts.sort_values(
    [
        "customer_key",
        "transaction_count",
        "payment_type",
    ],
    ascending=[True, False, True],
)

preferred_payment = (
    payment_type_counts
    .drop_duplicates("customer_key")
    [
        [
            "customer_key",
            "payment_type",
        ]
    ]
    .rename(
        columns={
            "payment_type": "preferred_payment_type"
        }
    )
)


# =========================================================
# 4. REVIEW SUMMARY
# =========================================================

print("Building review summary...")

review_summary = (
    reviews.groupby("customer_key")
    .agg(
        average_review_score=("review_score", "mean"),
        total_reviews=("review_key", "count"),
    )
    .reset_index()
)


# =========================================================
# 5. COMBINE CUSTOMER SUMMARIES
# =========================================================

print("Combining customer summaries...")

customer_360 = customers[
    [
        "customer_key",
        "customer_id",
        "customer_city",
        "customer_state",
    ]
].copy()


customer_360 = customer_360.merge(
    sales_summary,
    on="customer_key",
    how="left",
    validate="one_to_one",
)

customer_360 = customer_360.merge(
    payment_summary,
    on="customer_key",
    how="left",
    validate="one_to_one",
)

customer_360 = customer_360.merge(
    preferred_payment,
    on="customer_key",
    how="left",
    validate="one_to_one",
)

customer_360 = customer_360.merge(
    review_summary,
    on="customer_key",
    how="left",
    validate="one_to_one",
)


# =========================================================
# 6. CUSTOMER LIFETIME
# =========================================================

print("Calculating customer lifetime...")

customer_360["customer_lifetime_days"] = (
    customer_360["last_purchase_date"]
    - customer_360["first_purchase_date"]
).dt.days


# =========================================================
# 7. ROUND ANALYTICAL MEASURES
# =========================================================

customer_360["total_spending"] = (
    customer_360["total_spending"].round(2)
)

customer_360["average_order_value"] = (
    customer_360["average_order_value"].round(2)
)

customer_360["total_payment_value"] = (
    customer_360["total_payment_value"].round(2)
)

customer_360["average_review_score"] = (
    customer_360["average_review_score"].round(2)
)


# =========================================================
# 8. HANDLE CUSTOMERS WITHOUT REVIEWS
# =========================================================

customer_360["total_reviews"] = (
    customer_360["total_reviews"]
    .fillna(0)
    .astype(int)
)


# =========================================================
# 9. FINAL COLUMN ORDER
# =========================================================

customer_360 = customer_360[
    [
        "customer_key",
        "customer_id",
        "customer_city",
        "customer_state",
        "total_orders",
        "total_items",
        "total_spending",
        "average_order_value",
        "first_purchase_date",
        "last_purchase_date",
        "customer_lifetime_days",
        "average_review_score",
        "total_reviews",
        "total_payment_value",
        "payment_transactions",
        "preferred_payment_type",
    ]
]


# =========================================================
# 10. SAVE
# =========================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_path = OUTPUT_DIR / "data.parquet"

customer_360.to_parquet(
    output_path,
    index=False
)


# =========================================================
# 11. SUMMARY
# =========================================================

print("\nCustomer 360 Created Successfully")
print("----------------------------------")
print(f"Customers: {len(customer_360):,}")
print(f"Columns: {len(customer_360.columns)}")
print(f"Output: {output_path}")

print("\nSample:")
print(
    customer_360.head(10).to_string(
        index=False
    )
)