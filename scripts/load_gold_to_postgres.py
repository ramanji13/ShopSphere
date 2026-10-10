from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parents[1]

DATABASE_URL = (
    "postgresql+psycopg2://shopsphere:shopsphere123"
    "@localhost:5433/shopsphere_dw"
)

engine = create_engine(DATABASE_URL)


TABLES = {
    "dim_customer": BASE_DIR / "data/gold/dimensions/dim_customer/data.parquet",
    "dim_category": BASE_DIR / "data/gold/dimensions/dim_category/data.parquet",
    "dim_product": BASE_DIR / "data/gold/dimensions/dim_product/data.parquet",
    "dim_seller": BASE_DIR / "data/gold/dimensions/dim_seller/data.parquet",
    "dim_date": BASE_DIR / "data/gold/dimensions/dim_date/data.parquet",
    "fact_sales": BASE_DIR / "data/gold/facts/fact_sales/data.parquet",
    "fact_payments": BASE_DIR / "data/gold/facts/fact_payments/data.parquet",
    "fact_reviews": BASE_DIR / "data/gold/facts/fact_reviews/data.parquet",
    "customer_360": BASE_DIR / "data/gold/analytics/customer_360/data.parquet",
}


def load_table(table_name, parquet_path):
    print(f"\nLoading {table_name}...")

    df = pd.read_parquet(parquet_path)

    print(f"Gold rows: {len(df):,}")

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
        method="multi"
    )

    with engine.connect() as connection:
        count = connection.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()

    print(f"PostgreSQL rows: {count:,}")

    if count == len(df):
        print("Status: PASS")
    else:
        print("Status: FAIL")


def main():
    print("==========================================")
    print("ShopSphere Gold → PostgreSQL Load")
    print("==========================================")

    for table_name, parquet_path in TABLES.items():
        load_table(table_name, parquet_path)

    print("\n==========================================")
    print("Loading completed.")
    print("==========================================")


if __name__ == "__main__":
    main()