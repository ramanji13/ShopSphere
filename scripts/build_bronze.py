from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


DATASETS = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def build_bronze_layer():

    print("=" * 70)
    print("ShopSphere - Bronze Layer Build")
    print("=" * 70)

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    total_rows = 0

    for table_name, file_name in DATASETS.items():

        source_file = RAW_DIR / file_name
        output_dir = BRONZE_DIR / table_name
        output_file = output_dir / "data.parquet"

        print(f"\nProcessing: {table_name}")
        print(f"Source: {source_file.name}")

        if not source_file.exists():
            print(f"ERROR: Source file not found: {source_file}")
            continue

        output_dir.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(source_file)

        df.to_parquet(
            output_file,
            index=False,
            engine="pyarrow"
        )

        rows = len(df)
        columns = len(df.columns)

        total_rows += rows

        print(f"Rows: {rows:,}")
        print(f"Columns: {columns}")
        print(f"Output: {output_file}")

    print("\n" + "=" * 70)
    print("Bronze layer build completed.")
    print(f"Total rows processed: {total_rows:,}")
    print(f"Bronze location: {BRONZE_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    build_bronze_layer()