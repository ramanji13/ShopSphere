from pathlib import Path
import pandas as pd


# ============================================================
# Project Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"
REPORT_DIR = BASE_DIR / "reports" / "silver_quality"

SILVER_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Table Configuration
# ============================================================

TABLES = {
    "customers": "customers",
    "geolocation": "geolocation",
    "orders": "orders",
    "order_items": "order_items",
    "order_payments": "order_payments",
    "order_reviews": "order_reviews",
    "products": "products",
    "sellers": "sellers",
    "category_translation": "category_translation",
}


# ============================================================
# Helper Functions
# ============================================================

def read_bronze(table_name):
    path = BRONZE_DIR / table_name / "data.parquet"

    if not path.exists():
        raise FileNotFoundError(
            f"Bronze file not found: {path}"
        )

    return pd.read_parquet(path)


def standardize_text_columns(df):
    """
    Remove unnecessary spaces from text columns.
    Empty strings are converted to missing values.
    """

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    return df


def remove_exact_duplicates(df):
    """
    Remove only completely identical rows.
    """

    return df.drop_duplicates().copy()


def convert_datetime_columns(df, columns):
    """
    Convert specified columns to datetime.
    Invalid values become NaT.
    """

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


def convert_numeric_columns(df, columns):
    """
    Convert specified columns to numeric.
    Invalid values become NaN.
    """

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def add_order_quality_flags(df):
    """
    Add data-quality flags for order timestamp relationships.

    These flags do NOT remove affected orders.
    They identify records whose timestamps have
    unexpected chronological relationships.
    """

    df["approved_carrier_anomaly"] = (
        df["order_approved_at"].notna()
        & df["order_delivered_carrier_date"].notna()
        & (
            df["order_approved_at"]
            > df["order_delivered_carrier_date"]
        )
    )

    df["carrier_customer_anomaly"] = (
        df["order_delivered_carrier_date"].notna()
        & df["order_delivered_customer_date"].notna()
        & (
            df["order_delivered_carrier_date"]
            > df["order_delivered_customer_date"]
        )
    )

    df["date_sequence_valid"] = ~(
        df["approved_carrier_anomaly"]
        | df["carrier_customer_anomaly"]
    )

    return df


# ============================================================
# Table Cleaning Functions
# ============================================================

def clean_customers(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "customer_id",
        "customer_unique_id",
    ]

    df = df.dropna(subset=required_columns)

    return df


def clean_geolocation(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    return df


def clean_orders(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "order_id",
        "customer_id",
    ]

    df = df.dropna(subset=required_columns)

    datetime_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    df = convert_datetime_columns(
        df,
        datetime_columns
    )

    # --------------------------------------------------------
    # Add order date-quality flags
    # --------------------------------------------------------

    df = add_order_quality_flags(df)

    return df


def clean_order_items(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
    ]

    df = df.dropna(subset=required_columns)

    df = convert_numeric_columns(
        df,
        [
            "order_item_id",
            "price",
            "freight_value",
        ]
    )

    return df


def clean_order_payments(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "order_id",
        "payment_sequential",
        "payment_type",
    ]

    df = df.dropna(subset=required_columns)

    df = convert_numeric_columns(
        df,
        [
            "payment_sequential",
            "payment_installments",
            "payment_value",
        ]
    )

    return df


def clean_order_reviews(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "review_id",
        "order_id",
        "review_score",
    ]

    df = df.dropna(subset=required_columns)

    df = convert_numeric_columns(
        df,
        [
            "review_score",
        ]
    )

    df = convert_datetime_columns(
        df,
        [
            "review_creation_date",
            "review_answer_timestamp",
        ]
    )

    return df


def clean_products(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "product_id",
    ]

    df = df.dropna(subset=required_columns)

    df = convert_numeric_columns(
        df,
        [
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    )

    return df


def clean_sellers(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    required_columns = [
        "seller_id",
    ]

    df = df.dropna(subset=required_columns)

    return df


def clean_category_translation(df):

    df = standardize_text_columns(df)

    df = remove_exact_duplicates(df)

    return df


# ============================================================
# Cleaning Function Mapping
# ============================================================

CLEANING_FUNCTIONS = {
    "customers": clean_customers,
    "geolocation": clean_geolocation,
    "orders": clean_orders,
    "order_items": clean_order_items,
    "order_payments": clean_order_payments,
    "order_reviews": clean_order_reviews,
    "products": clean_products,
    "sellers": clean_sellers,
    "category_translation": clean_category_translation,
}


# ============================================================
# Quality Report
# ============================================================

def create_quality_record(
    table_name,
    rows_before,
    rows_after,
    df
):

    return {
        "table_name": table_name,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns": len(df.columns),
    }


# ============================================================
# Main Silver Build
# ============================================================

def main():

    print("=" * 70)
    print("ShopSphere - Building Silver Layer")
    print("=" * 70)

    quality_records = []

    for table_name in TABLES:

        print(f"\nProcessing: {table_name}")

        # ----------------------------------------------------
        # Read Bronze
        # ----------------------------------------------------

        df = read_bronze(table_name)

        rows_before = len(df)

        print(f"Rows before cleaning: {rows_before}")

        # ----------------------------------------------------
        # Clean table
        # ----------------------------------------------------

        cleaning_function = CLEANING_FUNCTIONS[table_name]

        df = cleaning_function(df)

        rows_after = len(df)

        print(f"Rows after cleaning:  {rows_after}")

        # ----------------------------------------------------
        # Write Silver
        # ----------------------------------------------------

        output_dir = SILVER_DIR / table_name

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = output_dir / "data.parquet"

        df.to_parquet(
            output_path,
            index=False,
            engine="pyarrow"
        )

        print(f"Silver output: {output_path}")

        # ----------------------------------------------------
        # Quality report
        # ----------------------------------------------------

        quality_records.append(
            create_quality_record(
                table_name,
                rows_before,
                rows_after,
                df
            )
        )

        # ----------------------------------------------------
        # Order quality statistics
        # ----------------------------------------------------

        if table_name == "orders":

            approved_carrier_count = int(
                df["approved_carrier_anomaly"].sum()
            )

            carrier_customer_count = int(
                df["carrier_customer_anomaly"].sum()
            )

            date_valid_count = int(
                df["date_sequence_valid"].sum()
            )

            print(
                f"Approved to Carrier anomalies: "
                f"{approved_carrier_count}"
            )

            print(
                f"Carrier to Customer anomalies: "
                f"{carrier_customer_count}"
            )

            print(
                f"Valid date sequences: "
                f"{date_valid_count}"
            )

    # ========================================================
    # Save Silver Quality Report
    # ========================================================

    quality_report = pd.DataFrame(
        quality_records
    )

    quality_report_path = (
        REPORT_DIR / "silver_quality_report.csv"
    )

    quality_report.to_csv(
        quality_report_path,
        index=False
    )

    print("\n" + "=" * 70)
    print("Silver layer build completed successfully.")
    print("=" * 70)

    print(
        f"\nQuality report saved to:\n"
        f"{quality_report_path}"
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()