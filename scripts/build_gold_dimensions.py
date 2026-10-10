from pathlib import Path
import pandas as pd


SILVER_DIR = Path("data/silver")
GOLD_DIR = Path("data/gold/dimensions")


def build_dim_customer():
    input_path = SILVER_DIR / "customers" / "data.parquet"
    output_dir = GOLD_DIR / "dim_customer"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(input_path)

    df = df[
        [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ]
    ].copy()

    df = df.sort_values("customer_id").reset_index(drop=True)

    df.insert(
        0,
        "customer_key",
        range(1, len(df) + 1)
    )

    df = df.rename(
        columns={
            "customer_zip_code_prefix": "customer_zip_code"
        }
    )

    output_path = output_dir / "data.parquet"
    df.to_parquet(output_path, index=False)

    print(f"dim_customer rows: {len(df):,}")
    print(f"Saved: {output_path}")


def build_dim_category():
    input_path = SILVER_DIR / "category_translation" / "data.parquet"
    output_dir = GOLD_DIR / "dim_category"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(input_path)

    df = df[
        [
            "product_category_name",
            "product_category_name_english",
        ]
    ].copy()

    df = df.sort_values(
        "product_category_name"
    ).reset_index(drop=True)

    df.insert(
        0,
        "category_key",
        range(1, len(df) + 1)
    )

    df = df.rename(
        columns={
            "product_category_name": "category_name_original",
            "product_category_name_english": "category_name",
        }
    )

    output_path = output_dir / "data.parquet"
    df.to_parquet(output_path, index=False)

    print(f"dim_category rows: {len(df):,}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    build_dim_customer()
    build_dim_category()

    print("\nGold dimension build completed successfully.")