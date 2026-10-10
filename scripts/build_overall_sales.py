import pandas as pd
from pathlib import Path


FACT_SALES_PATH = Path(
    "data/gold/facts/fact_sales/data.parquet"
)

OUTPUT_DIR = Path(
    "data/gold/analytics/sales_analytics/overall_sales"
)

OUTPUT_PATH = OUTPUT_DIR / "data.parquet"


def main():

    # ---------------------------------------------------------
    # Read fact_sales
    # ---------------------------------------------------------

    sales = pd.read_parquet(FACT_SALES_PATH)

    # ---------------------------------------------------------
    # Calculate overall business metrics
    # ---------------------------------------------------------

    total_orders = sales["order_id"].nunique()

    total_items = sales["order_item_id"].count()

    total_revenue = sales["price"].sum()

    total_freight = sales["freight_value"].sum()

    total_sales_value = sales["total_item_value"].sum()

    average_order_value = (
        total_sales_value / total_orders
        if total_orders > 0
        else 0
    )

    average_item_value = (
        total_sales_value / total_items
        if total_items > 0
        else 0
    )

    # ---------------------------------------------------------
    # Create one-row analytics table
    # ---------------------------------------------------------

    overall_sales = pd.DataFrame({
        "total_orders": [total_orders],
        "total_items": [total_items],
        "total_revenue": [total_revenue],
        "total_freight": [total_freight],
        "total_sales_value": [total_sales_value],
        "average_order_value": [average_order_value],
        "average_item_value": [average_item_value]
    })

    # ---------------------------------------------------------
    # Round financial metrics
    # ---------------------------------------------------------

    money_columns = [
        "total_revenue",
        "total_freight",
        "total_sales_value",
        "average_order_value",
        "average_item_value"
    ]

    overall_sales[money_columns] = (
        overall_sales[money_columns].round(2)
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    overall_sales.to_parquet(
        OUTPUT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # Print results
    # ---------------------------------------------------------

    print("=" * 60)
    print("OVERALL SALES ANALYTICS")
    print("=" * 60)

    print(f"Total orders       : {total_orders}")
    print(f"Total items        : {total_items}")
    print(f"Total revenue      : {total_revenue:.2f}")
    print(f"Total freight      : {total_freight:.2f}")
    print(f"Total sales value  : {total_sales_value:.2f}")
    print(f"Average order value: {average_order_value:.2f}")
    print(f"Average item value : {average_item_value:.2f}")

    print("\nOutput saved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()