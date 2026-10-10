from pathlib import Path
import pandas as pd


SILVER_ORDERS = Path("data/silver/orders/data.parquet")
SILVER_ORDER_ITEMS = Path("data/silver/order_items/data.parquet")

DIM_CUSTOMER = Path("data/gold/dimensions/dim_customer/data.parquet")
DIM_PRODUCT = Path("data/gold/dimensions/dim_product/data.parquet")
DIM_SELLER = Path("data/gold/dimensions/dim_seller/data.parquet")
DIM_DATE = Path("data/gold/dimensions/dim_date/data.parquet")

OUTPUT_DIR = Path("data/gold/facts/fact_sales")
OUTPUT_FILE = OUTPUT_DIR / "data.parquet"


def main():
    print("Reading Silver orders...")
    orders = pd.read_parquet(
        SILVER_ORDERS,
        columns=[
            "order_id",
            "customer_id",
            "order_purchase_timestamp",
            "order_status",
        ],
    )

    print("Reading Silver order items...")
    order_items = pd.read_parquet(
        SILVER_ORDER_ITEMS,
        columns=[
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
    )

    print("Reading Gold dimensions...")
    dim_customer = pd.read_parquet(
        DIM_CUSTOMER,
        columns=[
            "customer_key",
            "customer_id",
        ],
    )

    dim_product = pd.read_parquet(
        DIM_PRODUCT,
        columns=[
            "product_key",
            "product_id",
        ],
    )

    dim_seller = pd.read_parquet(
        DIM_SELLER,
        columns=[
            "seller_key",
            "seller_id",
        ],
    )

    dim_date = pd.read_parquet(
        DIM_DATE,
        columns=[
            "date_key",
            "full_date",
        ],
    )

    print("\nJoining orders with order items...")

    fact_sales = order_items.merge(
        orders,
        how="left",
        on="order_id",
        validate="many_to_one",
    )

    print(f"Rows after orders join: {len(fact_sales):,}")

    print("Joining customer dimension...")

    fact_sales = fact_sales.merge(
        dim_customer,
        how="left",
        on="customer_id",
        validate="many_to_one",
    )

    print("Joining product dimension...")

    fact_sales = fact_sales.merge(
        dim_product,
        how="left",
        on="product_id",
        validate="many_to_one",
    )

    print("Joining seller dimension...")

    fact_sales = fact_sales.merge(
        dim_seller,
        how="left",
        on="seller_id",
        validate="many_to_one",
    )

    # Convert purchase timestamp to date
    fact_sales["order_purchase_timestamp"] = pd.to_datetime(
        fact_sales["order_purchase_timestamp"],
        errors="coerce",
    )

    fact_sales["purchase_date"] = (
        fact_sales["order_purchase_timestamp"].dt.normalize()
    )

    print("Joining date dimension...")

    fact_sales = fact_sales.merge(
        dim_date,
        how="left",
        left_on="purchase_date",
        right_on="full_date",
        validate="many_to_one",
    )

    # Calculate sales measures
    fact_sales["total_item_value"] = (
        fact_sales["price"] + fact_sales["freight_value"]
    )

    # Create a warehouse fact key
    fact_sales = fact_sales.sort_values(
        ["order_id", "order_item_id"]
    ).reset_index(drop=True)

    fact_sales.insert(
        0,
        "sales_key",
        range(1, len(fact_sales) + 1),
    )

    # Select final fact columns
    fact_sales = fact_sales[
        [
            "sales_key",
            "order_id",
            "order_item_id",
            "customer_key",
            "product_key",
            "seller_key",
            "date_key",
            "order_status",
            "shipping_limit_date",
            "order_purchase_timestamp",
            "price",
            "freight_value",
            "total_item_value",
        ]
    ]

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write fact table
    fact_sales.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
    )

    print("\nFACT_SALES CREATED")
    print(f"Rows: {len(fact_sales):,}")
    print(f"Columns: {len(fact_sales.columns)}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nNull foreign-key counts:")

    print(
        f"customer_key: {fact_sales['customer_key'].isna().sum():,}"
    )

    print(
        f"product_key:  {fact_sales['product_key'].isna().sum():,}"
    )

    print(
        f"seller_key:   {fact_sales['seller_key'].isna().sum():,}"
    )

    print(
        f"date_key:     {fact_sales['date_key'].isna().sum():,}"
    )

    print("\nSample rows:")
    print(
        fact_sales.head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()