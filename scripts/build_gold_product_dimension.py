from pathlib import Path
import pandas as pd


SILVER_PRODUCTS = Path("data/silver/products/data.parquet")
GOLD_CATEGORY = Path("data/gold/dimensions/dim_category/data.parquet")

OUTPUT_DIR = Path("data/gold/dimensions/dim_product")
OUTPUT_FILE = OUTPUT_DIR / "data.parquet"


def main():
    print("Reading Silver products...")
    products = pd.read_parquet(SILVER_PRODUCTS)

    print("Reading Gold category dimension...")
    categories = pd.read_parquet(GOLD_CATEGORY)

    products = products[
        [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    ].copy()

    categories = categories[
        [
            "category_key",
            "category_name_original",
            "category_name",
        ]
    ].copy()

    products = products.merge(
        categories,
        how="left",
        left_on="product_category_name",
        right_on="category_name_original",
    )

    unmatched = products["category_key"].isna().sum()

    print(f"Products without a matched category: {unmatched}")

    products = products.sort_values("product_id").reset_index(drop=True)

    products.insert(
        0,
        "product_key",
        range(1, len(products) + 1),
    )

    products = products.rename(
        columns={
            "product_category_name": "product_category_name_original",
            "category_name_original": "category_name_original",
            "category_name": "category_name_english",
            "product_name_lenght": "product_name_length",
            "product_description_lenght": "product_description_length",
        }
    )

    products = products[
        [
            "product_key",
            "product_id",
            "category_key",
            "product_category_name_original",
            "category_name_english",
            "product_name_length",
            "product_description_length",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    products.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
    )

    print("\nDIM_PRODUCT CREATED")
    print(f"Rows: {len(products):,}")
    print(f"Columns: {len(products.columns)}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nSample rows:")
    print(products.head(10).to_string(index=False))


if __name__ == "__main__":
    main()