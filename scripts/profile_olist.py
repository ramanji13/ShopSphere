import os
import zipfile
import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZIP_FILE = os.path.join(PROJECT_ROOT, "archive.zip")

EXTRACT_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports", "data_profiling")


# ============================================================
# 2. EXPECTED OLIST FILES
# ============================================================

EXPECTED_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
]


# ============================================================
# 3. CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(EXTRACT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ============================================================
# 4. EXTRACT ZIP FILE
# ============================================================

print("=" * 80)
print("SHOPSPHERE - OLIST DATASET PROFILING")
print("=" * 80)

print("\n[1] Checking ZIP file...")

if not os.path.exists(ZIP_FILE):
    print(f"ERROR: ZIP file not found:")
    print(ZIP_FILE)
    print("\nPlace archive.zip in the ShopSphere_Project folder.")
    exit()

print("ZIP file found.")


print("\n[2] Extracting dataset...")

with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
    zip_ref.extractall(EXTRACT_DIR)

print("Dataset extracted successfully.")


# ============================================================
# 5. CHECK AVAILABLE FILES
# ============================================================

print("\n[3] Checking CSV files...")

available_files = [
    file_name
    for file_name in os.listdir(EXTRACT_DIR)
    if file_name.lower().endswith(".csv")
]

print(f"\nCSV files found: {len(available_files)}")

for file_name in sorted(available_files):
    print(" -", file_name)


missing_files = [
    file_name
    for file_name in EXPECTED_FILES
    if file_name not in available_files
]

if missing_files:
    print("\nWARNING: Expected files missing:")

    for file_name in missing_files:
        print(" -", file_name)

else:
    print("\nAll expected Olist CSV files are present.")


# ============================================================
# 6. LOAD ALL CSV FILES
# ============================================================

print("\n[4] Loading CSV files...")

dataframes = {}

for file_name in EXPECTED_FILES:

    file_path = os.path.join(EXTRACT_DIR, file_name)

    if not os.path.exists(file_path):
        continue

    try:
        df = pd.read_csv(file_path)

        dataframes[file_name] = df

        print(
            f"Loaded: {file_name:<45} "
            f"Rows: {len(df):>9,} "
            f"Columns: {len(df.columns):>3}"
        )

    except Exception as error:
        print(f"ERROR loading {file_name}: {error}")


# ============================================================
# 7. BASIC TABLE-BY-TABLE PROFILING
# ============================================================

print("\n\n")
print("=" * 80)
print("TABLE-BY-TABLE DATA PROFILING")
print("=" * 80)


summary_records = []


for file_name, df in dataframes.items():

    print("\n")
    print("=" * 80)
    print(f"TABLE: {file_name}")
    print("=" * 80)

    # --------------------------------------------------------
    # TABLE SIZE
    # --------------------------------------------------------

    row_count = len(df)
    column_count = len(df.columns)

    print("\n1. TABLE SIZE")
    print("-" * 40)

    print("Rows    :", f"{row_count:,}")
    print("Columns :", column_count)

    # --------------------------------------------------------
    # COLUMN NAMES
    # --------------------------------------------------------

    print("\n2. COLUMN NAMES")
    print("-" * 40)

    for index, column in enumerate(df.columns, start=1):
        print(f"{index:>2}. {column}")

    # --------------------------------------------------------
    # DATA TYPES
    # --------------------------------------------------------

    print("\n3. DATA TYPES")
    print("-" * 40)

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    print("\n4. MISSING VALUES")
    print("-" * 40)

    null_counts = df.isnull().sum()

    null_percentages = (
        df.isnull().mean() * 100
    ).round(2)

    null_report = pd.DataFrame({
        "column": df.columns,
        "missing_count": null_counts.values,
        "missing_percentage": null_percentages.values
    })

    null_report = null_report[
        null_report["missing_count"] > 0
    ]

    if null_report.empty:

        print("No missing values found.")

    else:

        print(
            null_report.to_string(index=False)
        )

    # --------------------------------------------------------
    # DUPLICATE ROWS
    # --------------------------------------------------------

    print("\n5. DUPLICATE ROWS")
    print("-" * 40)

    duplicate_count = df.duplicated().sum()

    print("Completely duplicated rows:",
          f"{duplicate_count:,}")

    # --------------------------------------------------------
    # UNIQUE VALUES
    # --------------------------------------------------------

    print("\n6. UNIQUE VALUES")
    print("-" * 40)

    unique_report = []

    for column in df.columns:

        unique_count = df[column].nunique(
            dropna=True
        )

        unique_report.append({
            "column": column,
            "unique_values": unique_count,
            "total_rows": row_count
        })

    unique_df = pd.DataFrame(unique_report)

    print(unique_df.to_string(index=False))

    # --------------------------------------------------------
    # SAMPLE RECORDS
    # --------------------------------------------------------

    print("\n7. FIRST FIVE RECORDS")
    print("-" * 40)

    print(df.head().to_string())

    # --------------------------------------------------------
    # NUMERIC STATISTICS
    # --------------------------------------------------------

    print("\n8. NUMERIC COLUMN STATISTICS")
    print("-" * 40)

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) == 0:

        print("No numeric columns.")

    else:

        print(
            df[numeric_columns]
            .describe()
            .round(2)
            .to_string()
        )

    # --------------------------------------------------------
    # DATE/TIME CANDIDATE COLUMNS
    # --------------------------------------------------------

    print("\n9. DATE/TIME CANDIDATE COLUMNS")
    print("-" * 40)

    date_columns = [
        column
        for column in df.columns
        if (
            "date" in column.lower()
            or "time" in column.lower()
            or "timestamp" in column.lower()
        )
    ]

    if date_columns:

        for column in date_columns:
            print("-", column)

    else:

        print("No obvious date/time columns detected.")

    # --------------------------------------------------------
    # SAVE NULL REPORT
    # --------------------------------------------------------

    table_name = file_name.replace(
        ".csv", ""
    )

    null_output = os.path.join(
        REPORT_DIR,
        f"{table_name}_null_report.csv"
    )

    null_report.to_csv(
        null_output,
        index=False
    )

    # --------------------------------------------------------
    # SAVE UNIQUE REPORT
    # --------------------------------------------------------

    unique_output = os.path.join(
        REPORT_DIR,
        f"{table_name}_unique_report.csv"
    )

    unique_df.to_csv(
        unique_output,
        index=False
    )

    # --------------------------------------------------------
    # SUMMARY RECORD
    # --------------------------------------------------------

    summary_records.append({
        "file_name": file_name,
        "rows": row_count,
        "columns": column_count,
        "duplicate_rows": duplicate_count,
        "columns_with_missing_values":
            int((df.isnull().sum() > 0).sum())
    })


# ============================================================
# 8. PRIMARY KEY / CANDIDATE KEY ANALYSIS
# ============================================================

print("\n\n")
print("=" * 80)
print("PRIMARY KEY / CANDIDATE KEY ANALYSIS")
print("=" * 80)


candidate_keys = {
    "olist_customers_dataset.csv": [
        "customer_id",
        "customer_unique_id"
    ],

    "olist_orders_dataset.csv": [
        "order_id"
    ],

    "olist_order_items_dataset.csv": [
        "order_id",
        "order_item_id"
    ],

    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_sequential"
    ],

    "olist_order_reviews_dataset.csv": [
        "review_id"
    ],

    "olist_products_dataset.csv": [
        "product_id"
    ],

    "olist_sellers_dataset.csv": [
        "seller_id"
    ],

    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix"
    ],

    "product_category_name_translation.csv": [
        "product_category_name"
    ]
}


key_results = []


for file_name, columns in candidate_keys.items():

    if file_name not in dataframes:
        continue

    df = dataframes[file_name]

    print("\n")
    print("-" * 80)
    print(file_name)
    print("-" * 80)

    for column in columns:

        if column not in df.columns:

            print(
                f"{column}: COLUMN NOT FOUND"
            )

            continue

        total_rows = len(df)

        unique_values = df[column].nunique(
            dropna=True
        )

        null_values = df[column].isnull().sum()

        duplicate_values = df[column].duplicated(
            keep=False
        ).sum()

        is_unique = (
            unique_values == total_rows
            and null_values == 0
        )

        print(f"\nColumn: {column}")
        print("Total rows       :", f"{total_rows:,}")
        print("Unique values    :", f"{unique_values:,}")
        print("Null values      :", f"{null_values:,}")
        print(
            "Rows involved in duplicate values:",
            f"{duplicate_values:,}"
        )

        if is_unique:
            print("Result           : UNIQUE CANDIDATE KEY")
        else:
            print("Result           : NOT UNIQUE")

        key_results.append({
            "file_name": file_name,
            "key_column": column,
            "total_rows": total_rows,
            "unique_values": unique_values,
            "null_values": null_values,
            "duplicate_rows": duplicate_values,
            "unique_candidate_key": is_unique
        })


# ============================================================
# 9. COMPOSITE KEY ANALYSIS
# ============================================================

print("\n\n")
print("=" * 80)
print("COMPOSITE KEY ANALYSIS")
print("=" * 80)


composite_keys = {
    "olist_order_items_dataset.csv": [
        "order_id",
        "order_item_id"
    ],

    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_sequential"
    ]
}


for file_name, columns in composite_keys.items():

    if file_name not in dataframes:
        continue

    df = dataframes[file_name]

    print("\n")
    print(file_name)

    duplicate_count = df.duplicated(
        subset=columns
    ).sum()

    null_count = df[columns].isnull().any(
        axis=1
    ).sum()

    print("Columns:",
          ", ".join(columns))

    print(
        "Duplicate combinations:",
        f"{duplicate_count:,}"
    )

    print(
        "Rows with null key values:",
        f"{null_count:,}"
    )

    if duplicate_count == 0 and null_count == 0:
        print(
            "Result: VALID CANDIDATE COMPOSITE KEY"
        )
    else:
        print(
            "Result: NEEDS INVESTIGATION"
        )


# ============================================================
# 10. FOREIGN KEY RELATIONSHIP ANALYSIS
# ============================================================

print("\n\n")
print("=" * 80)
print("FOREIGN KEY RELATIONSHIP ANALYSIS")
print("=" * 80)


relationships = [

    {
        "child_file":
            "olist_orders_dataset.csv",

        "child_column":
            "customer_id",

        "parent_file":
            "olist_customers_dataset.csv",

        "parent_column":
            "customer_id"
    },

    {
        "child_file":
            "olist_order_items_dataset.csv",

        "child_column":
            "order_id",

        "parent_file":
            "olist_orders_dataset.csv",

        "parent_column":
            "order_id"
    },

    {
        "child_file":
            "olist_order_items_dataset.csv",

        "child_column":
            "product_id",

        "parent_file":
            "olist_products_dataset.csv",

        "parent_column":
            "product_id"
    },

    {
        "child_file":
            "olist_order_items_dataset.csv",

        "child_column":
            "seller_id",

        "parent_file":
            "olist_sellers_dataset.csv",

        "parent_column":
            "seller_id"
    },

    {
        "child_file":
            "olist_order_payments_dataset.csv",

        "child_column":
            "order_id",

        "parent_file":
            "olist_orders_dataset.csv",

        "parent_column":
            "order_id"
    },

    {
        "child_file":
            "olist_order_reviews_dataset.csv",

        "child_column":
            "order_id",

        "parent_file":
            "olist_orders_dataset.csv",

        "parent_column":
            "order_id"
    }
]


relationship_results = []


for relationship in relationships:

    child_file = relationship["child_file"]
    child_column = relationship["child_column"]

    parent_file = relationship["parent_file"]
    parent_column = relationship["parent_column"]

    child_df = dataframes[child_file]
    parent_df = dataframes[parent_file]

    child_values = child_df[
        child_column
    ].dropna().unique()

    parent_values = set(
        parent_df[parent_column]
        .dropna()
        .unique()
    )

    unmatched_values = [
        value
        for value in child_values
        if value not in parent_values
    ]

    unmatched_count = len(unmatched_values)

    print("\n")
    print(
        f"{child_file}.{child_column}"
    )

    print(
        "        ↓ references"
    )

    print(
        f"{parent_file}.{parent_column}"
    )

    print(
        "Unmatched references:",
        f"{unmatched_count:,}"
    )

    if unmatched_count == 0:

        print(
            "Result: FOREIGN KEY RELATIONSHIP VALID"
        )

    else:

        print(
            "Result: REFERENTIAL INTEGRITY ISSUE"
        )

    relationship_results.append({
        "child_file": child_file,
        "child_column": child_column,
        "parent_file": parent_file,
        "parent_column": parent_column,
        "unmatched_references": unmatched_count
    })


# ============================================================
# 11. CUSTOMER ORDER RELATIONSHIP
# ============================================================

print("\n\n")
print("=" * 80)
print("CUSTOMER ORDER CARDINALITY")
print("=" * 80)


customers = dataframes[
    "olist_customers_dataset.csv"
]

orders = dataframes[
    "olist_orders_dataset.csv"
]


orders_per_customer = (
    orders
    .groupby("customer_id")
    .size()
)


print(
    "Customers with at least one order:",
    f"{orders_per_customer.shape[0]:,}"
)

print(
    "Maximum orders for one customer record:",
    orders_per_customer.max()
)

print(
    "Average orders per customer record:",
    round(
        orders_per_customer.mean(),
        2
    )
)


# ============================================================
# 12. ORDER ITEM CARDINALITY
# ============================================================

print("\n\n")
print("=" * 80)
print("ORDER ITEM CARDINALITY")
print("=" * 80)


order_items = dataframes[
    "olist_order_items_dataset.csv"
]


items_per_order = (
    order_items
    .groupby("order_id")
    .size()
)


print(
    "Orders containing items:",
    f"{items_per_order.shape[0]:,}"
)

print(
    "Maximum items in one order:",
    items_per_order.max()
)

print(
    "Average items per order:",
    round(
        items_per_order.mean(),
        2
    )
)


# ============================================================
# 13. PAYMENT CARDINALITY
# ============================================================

print("\n\n")
print("=" * 80)
print("PAYMENT CARDINALITY")
print("=" * 80)


payments = dataframes[
    "olist_order_payments_dataset.csv"
]


payments_per_order = (
    payments
    .groupby("order_id")
    .size()
)


print(
    "Orders with payment records:",
    f"{payments_per_order.shape[0]:,}"
)

print(
    "Maximum payment records for one order:",
    payments_per_order.max()
)

print(
    "Average payment records per order:",
    round(
        payments_per_order.mean(),
        2
    )
)


# ============================================================
# 14. PRODUCT CATEGORY ANALYSIS
# ============================================================

print("\n\n")
print("=" * 80)
print("PRODUCT CATEGORY ANALYSIS")
print("=" * 80)


products = dataframes[
    "olist_products_dataset.csv"
]

translation = dataframes[
    "product_category_name_translation.csv"
]


product_categories = set(
    products[
        "product_category_name"
    ]
    .dropna()
    .unique()
)

translated_categories = set(
    translation[
        "product_category_name"
    ]
    .dropna()
    .unique()
)


untranslated_categories = (
    product_categories
    - translated_categories
)


print(
    "Distinct product categories:",
    f"{len(product_categories):,}"
)

print(
    "Categories with English translation:",
    f"{len(product_categories & translated_categories):,}"
)

print(
    "Categories without translation:",
    f"{len(untranslated_categories):,}"
)

if untranslated_categories:

    print("\nCategories without translation:")

    for category in sorted(
        untranslated_categories
    ):

        print("-", category)


# ============================================================
# 15. DATA QUALITY SUMMARY
# ============================================================

print("\n\n")
print("=" * 80)
print("DATA QUALITY SUMMARY")
print("=" * 80)


summary_df = pd.DataFrame(
    summary_records
)

print(
    summary_df.to_string(
        index=False
    )
)


# ============================================================
# 16. SAVE MAIN REPORTS
# ============================================================

summary_path = os.path.join(
    REPORT_DIR,
    "dataset_summary.csv"
)

keys_path = os.path.join(
    REPORT_DIR,
    "key_analysis.csv"
)

relationships_path = os.path.join(
    REPORT_DIR,
    "relationship_analysis.csv"
)


summary_df.to_csv(
    summary_path,
    index=False
)

pd.DataFrame(
    key_results
).to_csv(
    keys_path,
    index=False
)

pd.DataFrame(
    relationship_results
).to_csv(
    relationships_path,
    index=False
)


# ============================================================
# 17. FINAL MESSAGE
# ============================================================

print("\n\n")
print("=" * 80)
print("PROFILING COMPLETED")
print("=" * 80)

print("\nReports generated in:")

print(REPORT_DIR)

print("\nGenerated files:")

for file_name in sorted(
    os.listdir(REPORT_DIR)
):

    print(" -", file_name)

print("\nShopSphere Step 3 analysis completed.")