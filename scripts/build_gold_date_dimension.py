from pathlib import Path
import pandas as pd


SILVER_ORDERS = Path("data/silver/orders/data.parquet")

OUTPUT_DIR = Path("data/gold/dimensions/dim_date")
OUTPUT_FILE = OUTPUT_DIR / "data.parquet"


def main():
    print("Reading Silver orders...")

    orders = pd.read_parquet(
        SILVER_ORDERS,
        columns=["order_purchase_timestamp"]
    )

    # Make sure the order timestamp is datetime
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce"
    )

    # Extract only the date
    order_dates = orders["order_purchase_timestamp"].dt.normalize()

    # Find the date range
    start_date = order_dates.min()
    end_date = order_dates.max()

    print(f"Start date: {start_date.date()}")
    print(f"End date:   {end_date.date()}")

    # Generate every calendar date in the range
    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )

    dim_date = pd.DataFrame(
        {
            "full_date": dates
        }
    )

    # Create date attributes
    dim_date["date_key"] = (
        dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    )

    dim_date["year"] = dim_date["full_date"].dt.year

    dim_date["quarter"] = (
        "Q" + dim_date["full_date"].dt.quarter.astype(str)
    )

    dim_date["month"] = dim_date["full_date"].dt.month

    dim_date["month_name"] = dim_date["full_date"].dt.month_name()

    dim_date["day"] = dim_date["full_date"].dt.day

    dim_date["day_name"] = dim_date["full_date"].dt.day_name()

    dim_date["day_of_week"] = (
        dim_date["full_date"].dt.dayofweek + 1
    )

    dim_date["week_of_year"] = (
        dim_date["full_date"].dt.isocalendar().week.astype(int)
    )

    # Reorder columns
    dim_date = dim_date[
        [
            "date_key",
            "full_date",
            "year",
            "quarter",
            "month",
            "month_name",
            "day",
            "day_name",
            "day_of_week",
            "week_of_year",
        ]
    ]

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write Parquet
    dim_date.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    print("\nDIM_DATE CREATED")
    print(f"Rows: {len(dim_date):,}")
    print(f"Columns: {len(dim_date.columns)}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nFirst 5 rows:")
    print(dim_date.head().to_string(index=False))

    print("\nLast 5 rows:")
    print(dim_date.tail().to_string(index=False))


if __name__ == "__main__":
    main()