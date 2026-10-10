from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

SILVER_DIR = BASE_DIR / "data" / "silver"
GOLD_DIM_DIR = BASE_DIR / "data" / "gold" / "dimensions"
OUTPUT_DIR = BASE_DIR / "data" / "gold" / "facts" / "fact_payments"


print("Reading Silver order_payments...")
payments = pd.read_parquet(
    SILVER_DIR / "order_payments" / "data.parquet"
)

print("Reading Silver orders...")
orders = pd.read_parquet(
    SILVER_DIR / "orders" / "data.parquet"
)

print("Reading dimensions...")
dim_customer = pd.read_parquet(
    GOLD_DIM_DIR / "dim_customer" / "data.parquet"
)

dim_date = pd.read_parquet(
    GOLD_DIM_DIR / "dim_date" / "data.parquet"
)


# ---------------------------------------------------------
# Step 1: Join payments with orders
# ---------------------------------------------------------

print("\nJoining payments with orders...")

fact = payments.merge(
    orders[
        [
            "order_id",
            "customer_id",
            "order_purchase_timestamp",
            "order_status",
        ]
    ],
    on="order_id",
    how="left",
    validate="many_to_one",
)

print(f"Rows after order join: {len(fact):,}")


# ---------------------------------------------------------
# Step 2: Join customer dimension
# ---------------------------------------------------------

print("Joining customer dimension...")

fact = fact.merge(
    dim_customer[
        [
            "customer_key",
            "customer_id",
        ]
    ],
    on="customer_id",
    how="left",
    validate="many_to_one",
)


# ---------------------------------------------------------
# Step 3: Create purchase date
# ---------------------------------------------------------

fact["purchase_date"] = (
    pd.to_datetime(fact["order_purchase_timestamp"])
    .dt.normalize()
)


# ---------------------------------------------------------
# Step 4: Join date dimension
# ---------------------------------------------------------

print("Joining date dimension...")

dim_date_join = dim_date[
    [
        "date_key",
        "full_date",
    ]
].copy()

dim_date_join["full_date"] = pd.to_datetime(
    dim_date_join["full_date"]
).dt.normalize()

fact = fact.merge(
    dim_date_join,
    left_on="purchase_date",
    right_on="full_date",
    how="left",
    validate="many_to_one",
)


# ---------------------------------------------------------
# Step 5: Create payment key
# ---------------------------------------------------------

fact = fact.sort_values(
    ["order_id", "payment_sequential"]
).reset_index(drop=True)

fact.insert(
    0,
    "payment_key",
    range(1, len(fact) + 1),
)


# ---------------------------------------------------------
# Step 6: Select final columns
# ---------------------------------------------------------

fact = fact[
    [
        "payment_key",
        "order_id",
        "payment_sequential",
        "customer_key",
        "date_key",
        "order_status",
        "payment_type",
        "payment_installments",
        "payment_value",
        "order_purchase_timestamp",
    ]
]


# ---------------------------------------------------------
# Step 7: Save
# ---------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_path = OUTPUT_DIR / "data.parquet"

fact.to_parquet(
    output_path,
    index=False
)


# ---------------------------------------------------------
# Step 8: Display summary
# ---------------------------------------------------------

print("\nFact Payments Created Successfully")
print("-----------------------------------")
print(f"Rows: {len(fact):,}")
print(f"Columns: {len(fact.columns)}")
print(f"Output: {output_path}")

print("\nSample:")
print(fact.head(10).to_string(index=False))