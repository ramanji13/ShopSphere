from pathlib import Path
import pandas as pd


SILVER_SELLERS = Path("data/silver/sellers/data.parquet")

OUTPUT_DIR = Path("data/gold/dimensions/dim_seller")
OUTPUT_FILE = OUTPUT_DIR / "data.parquet"


def main():
    print("Reading Silver sellers...")
    sellers = pd.read_parquet(SILVER_SELLERS)

    print(f"Source seller rows: {len(sellers):,}")

    # Select columns required for the seller dimension
    sellers = sellers[
        [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ]
    ].copy()

    # Sort by the original seller ID
    sellers = sellers.sort_values("seller_id").reset_index(drop=True)

    # Create warehouse surrogate key
    sellers.insert(
        0,
        "seller_key",
        range(1, len(sellers) + 1),
    )

    # Rename columns for the Gold layer
    sellers = sellers.rename(
        columns={
            "seller_zip_code_prefix": "seller_zip_code",
        }
    )

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write Gold dimension
    sellers.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
    )

    print("\nDIM_SELLER CREATED")
    print(f"Rows: {len(sellers):,}")
    print(f"Columns: {len(sellers.columns)}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nSample rows:")
    print(sellers.head(10).to_string(index=False))


if __name__ == "__main__":
    main()