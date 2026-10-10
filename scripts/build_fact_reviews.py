from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

SILVER_DIR = BASE_DIR / "data" / "silver"
GOLD_DIM_DIR = BASE_DIR / "data" / "gold" / "dimensions"
OUTPUT_DIR = BASE_DIR / "data" / "gold" / "facts" / "fact_reviews"


print("Reading Silver order_reviews...")
reviews = pd.read_parquet(
    SILVER_DIR / "order_reviews" / "data.parquet"
)

print("Reading Silver orders...")
orders = pd.read_parquet(
    SILVER_DIR / "orders" / "data.parquet"
)

print("Reading customer dimension...")
dim_customer = pd.read_parquet(
    GOLD_DIM_DIR / "dim_customer" / "data.parquet"
)


# ---------------------------------------------------------
# Step 1: Join reviews with orders
# ---------------------------------------------------------

print("\nJoining reviews with orders...")

fact = reviews.merge(
    orders[
        [
            "order_id",
            "customer_id",
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
# Step 3: Convert review dates
# ---------------------------------------------------------

fact["review_creation_date"] = pd.to_datetime(
    fact["review_creation_date"],
    errors="coerce",
)

fact["review_answer_timestamp"] = pd.to_datetime(
    fact["review_answer_timestamp"],
    errors="coerce",
)


# ---------------------------------------------------------
# Step 4: Create review key
# ---------------------------------------------------------

fact = fact.sort_values(
    ["review_id", "order_id"]
).reset_index(drop=True)

fact.insert(
    0,
    "review_key",
    range(1, len(fact) + 1),
)


# ---------------------------------------------------------
# Step 5: Select final columns
# ---------------------------------------------------------

fact = fact[
    [
        "review_key",
        "review_id",
        "order_id",
        "customer_key",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ]
]


# ---------------------------------------------------------
# Step 6: Save
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
# Step 7: Display summary
# ---------------------------------------------------------

print("\nFact Reviews Created Successfully")
print("----------------------------------")
print(f"Rows: {len(fact):,}")
print(f"Columns: {len(fact.columns)}")
print(f"Output: {output_path}")

print("\nSample:")
print(fact.head(10).to_string(index=False))