from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_DIR = PROJECT_ROOT / "data" / "silver"
REPORT_DIR = PROJECT_ROOT / "reports" / "silver_quality"


def load_table(table_name):
    file_path = SILVER_DIR / table_name / "data.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"Silver file not found: {file_path}")

    return pd.read_parquet(file_path)


def check_primary_key(df, column):
    if column not in df.columns:
        return {
            "check": f"Primary key: {column}",
            "status": "FAIL",
            "details": "Column not found"
        }

    null_count = int(df[column].isna().sum())
    duplicate_count = int(df[column].duplicated().sum())

    if null_count == 0 and duplicate_count == 0:
        status = "PASS"
        details = "No null or duplicate primary keys"
    else:
        status = "FAIL"
        details = (
            f"nulls={null_count}, "
            f"duplicates={duplicate_count}"
        )

    return {
        "check": f"Primary key: {column}",
        "status": status,
        "details": details
    }


def check_composite_key(df, columns):

    missing_columns = [
        column for column in columns
        if column not in df.columns
    ]

    if missing_columns:
        return {
            "check": f"Composite key: {columns}",
            "status": "FAIL",
            "details": f"Missing columns={missing_columns}"
        }

    null_count = int(
        df[list(columns)].isna().any(axis=1).sum()
    )

    duplicate_count = int(
        df.duplicated(subset=list(columns)).sum()
    )

    if null_count == 0 and duplicate_count == 0:
        status = "PASS"
        details = "No null or duplicate composite keys"
    else:
        status = "FAIL"
        details = (
            f"null_key_rows={null_count}, "
            f"duplicate_keys={duplicate_count}"
        )

    return {
        "check": f"Composite key: {columns}",
        "status": status,
        "details": details
    }


def check_required_columns(df, columns):

    results = []

    for column in columns:

        if column not in df.columns:
            results.append({
                "check": f"Required column: {column}",
                "status": "FAIL",
                "details": "Column not found"
            })
            continue

        null_count = int(
            df[column].isna().sum()
        )

        results.append({
            "check": f"Required column: {column}",
            "status": "PASS" if null_count == 0 else "FAIL",
            "details": f"nulls={null_count}"
        })

    return results


def check_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column
):

    child_values = set(
        child_df[child_column].dropna()
    )

    parent_values = set(
        parent_df[parent_column].dropna()
    )

    invalid_values = child_values - parent_values

    if len(invalid_values) == 0:
        status = "PASS"
        details = "All references exist"
    else:
        status = "FAIL"
        details = f"Invalid references={len(invalid_values)}"

    return {
        "check": (
            f"Foreign key: "
            f"{child_column} → {parent_column}"
        ),
        "status": status,
        "details": details
    }


def check_numeric_range(
    df,
    column,
    minimum=None,
    maximum=None
):

    if column not in df.columns:
        return {
            "check": f"Range: {column}",
            "status": "FAIL",
            "details": "Column not found"
        }

    series = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid = series.isna()

    if minimum is not None:
        invalid |= series < minimum

    if maximum is not None:
        invalid |= series > maximum

    invalid_count = int(
        invalid.sum()
    )

    if invalid_count == 0:
        status = "PASS"
        details = "All values within expected range"
    else:
        status = "FAIL"
        details = f"invalid_values={invalid_count}"

    return {
        "check": f"Range: {column}",
        "status": status,
        "details": details
    }


def check_date_order(
    df,
    earlier_column,
    later_column
):

    earlier = pd.to_datetime(
        df[earlier_column],
        errors="coerce"
    )

    later = pd.to_datetime(
        df[later_column],
        errors="coerce"
    )

    invalid = (
        earlier.notna()
        & later.notna()
        & (later < earlier)
    )

    invalid_count = int(
        invalid.sum()
    )

    if invalid_count == 0:
        status = "PASS"
        details = "No chronological violations"
    else:
        status = "FAIL"
        details = f"invalid_records={invalid_count}"

    return {
        "check": (
            f"Date order: "
            f"{earlier_column} <= {later_column}"
        ),
        "status": status,
        "details": details
    }


def add_order_quality_flags(orders):

    orders = orders.copy()

    orders["date_sequence_valid"] = True

    approved_before_carrier = (
        orders["order_approved_at"].notna()
        & orders["order_delivered_carrier_date"].notna()
        & (
            orders["order_delivered_carrier_date"]
            < orders["order_approved_at"]
        )
    )

    carrier_before_customer = (
        orders["order_delivered_carrier_date"].notna()
        & orders["order_delivered_customer_date"].notna()
        & (
            orders["order_delivered_customer_date"]
            < orders["order_delivered_carrier_date"]
        )
    )

    orders.loc[
        approved_before_carrier,
        "date_sequence_valid"
    ] = False

    orders.loc[
        carrier_before_customer,
        "date_sequence_valid"
    ] = False

    orders["approved_carrier_anomaly"] = (
        approved_before_carrier
    )

    orders["carrier_customer_anomaly"] = (
        carrier_before_customer
    )

    return orders


def run_validation():

    print("=" * 70)
    print("ShopSphere - Silver Data Quality Validation")
    print("=" * 70)

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = []

    customers = load_table("customers")
    orders = load_table("orders")
    order_items = load_table("order_items")
    payments = load_table("order_payments")
    reviews = load_table("order_reviews")
    products = load_table("products")
    sellers = load_table("sellers")

    # ---------------------------------------------------------
    # Convert order timestamps
    # ---------------------------------------------------------

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # 1. Primary Key Validation
    # ---------------------------------------------------------

    print("\n1. Primary Key Validation")

    primary_keys = {
        "customers": (customers, "customer_id"),
        "orders": (orders, "order_id"),
        "products": (products, "product_id"),
        "sellers": (sellers, "seller_id")
    }

    for table_name, (df, column) in primary_keys.items():

        result = check_primary_key(
            df,
            column
        )

        result["table"] = table_name
        results.append(result)

        print(
            f"{table_name}: "
            f"{result['status']} - "
            f"{result['details']}"
        )

    # ---------------------------------------------------------
    # 2. Composite Key Validation
    # ---------------------------------------------------------

    print("\n2. Composite Key Validation")

    result = check_composite_key(
        order_items,
        [
            "order_id",
            "order_item_id"
        ]
    )

    result["table"] = "order_items"
    results.append(result)

    print(
        f"order_items: "
        f"{result['status']} - "
        f"{result['details']}"
    )

    result = check_composite_key(
        payments,
        [
            "order_id",
            "payment_sequential"
        ]
    )

    result["table"] = "order_payments"
    results.append(result)

    print(
        f"order_payments: "
        f"{result['status']} - "
        f"{result['details']}"
    )

    # ---------------------------------------------------------
    # 3. Required Columns
    # ---------------------------------------------------------

    print("\n3. Required Column Validation")

    required_columns = {
        "customers": [
            "customer_id",
            "customer_unique_id"
        ],
        "orders": [
            "order_id",
            "customer_id"
        ],
        "order_items": [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id"
        ],
        "order_payments": [
            "order_id",
            "payment_sequential",
            "payment_type"
        ],
        "order_reviews": [
            "review_id",
            "order_id",
            "review_score"
        ],
        "products": [
            "product_id"
        ],
        "sellers": [
            "seller_id"
        ]
    }

    for table_name, columns in required_columns.items():

        df = load_table(table_name)

        table_results = check_required_columns(
            df,
            columns
        )

        for result in table_results:

            result["table"] = table_name
            results.append(result)

            print(
                f"{table_name}: "
                f"{result['check']} - "
                f"{result['status']} - "
                f"{result['details']}"
            )

    # ---------------------------------------------------------
    # 4. Foreign Key Validation
    # ---------------------------------------------------------

    print("\n4. Foreign Key Validation")

    foreign_keys = [
        (
            "orders",
            orders,
            "customer_id",
            "customers",
            customers,
            "customer_id"
        ),
        (
            "order_items",
            order_items,
            "order_id",
            "orders",
            orders,
            "order_id"
        ),
        (
            "order_items",
            order_items,
            "product_id",
            "products",
            products,
            "product_id"
        ),
        (
            "order_items",
            order_items,
            "seller_id",
            "sellers",
            sellers,
            "seller_id"
        ),
        (
            "order_payments",
            payments,
            "order_id",
            "orders",
            orders,
            "order_id"
        ),
        (
            "order_reviews",
            reviews,
            "order_id",
            "orders",
            orders,
            "order_id"
        )
    ]

    for (
        child_table,
        child_df,
        child_column,
        parent_table,
        parent_df,
        parent_column
    ) in foreign_keys:

        result = check_foreign_key(
            child_df,
            child_column,
            parent_df,
            parent_column
        )

        result["table"] = child_table
        results.append(result)

        print(
            f"{child_table}: "
            f"{result['status']} - "
            f"{result['details']}"
        )

    # ---------------------------------------------------------
    # 5. Numeric Range Validation
    # ---------------------------------------------------------

    print("\n5. Numeric Range Validation")

    numeric_checks = [
        (
            "order_items",
            order_items,
            "price",
            0,
            None
        ),
        (
            "order_items",
            order_items,
            "freight_value",
            0,
            None
        ),
        (
            "order_payments",
            payments,
            "payment_value",
            0,
            None
        ),
        (
            "order_payments",
            payments,
            "payment_installments",
            0,
            None
        ),
        (
            "order_reviews",
            reviews,
            "review_score",
            1,
            5
        )
    ]

    for (
        table_name,
        df,
        column,
        minimum,
        maximum
    ) in numeric_checks:

        result = check_numeric_range(
            df,
            column,
            minimum,
            maximum
        )

        result["table"] = table_name
        results.append(result)

        print(
            f"{table_name}.{column}: "
            f"{result['status']} - "
            f"{result['details']}"
        )

    # ---------------------------------------------------------
    # 6. Date Consistency Validation
    # ---------------------------------------------------------

    print("\n6. Date Consistency Validation")

    date_checks = [
        (
            "orders",
            orders,
            "order_purchase_timestamp",
            "order_approved_at"
        ),
        (
            "orders",
            orders,
            "order_approved_at",
            "order_delivered_carrier_date"
        ),
        (
            "orders",
            orders,
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ),
        (
            "orders",
            orders,
            "order_purchase_timestamp",
            "order_estimated_delivery_date"
        )
    ]

    for (
        table_name,
        df,
        earlier,
        later
    ) in date_checks:

        result = check_date_order(
            df,
            earlier,
            later
        )

        result["table"] = table_name
        results.append(result)

        print(
            f"{table_name}: "
            f"{result['status']} - "
            f"{result['details']}"
        )

    # ---------------------------------------------------------
    # 7. Create Quality Flags
    # ---------------------------------------------------------

    print("\n7. Order Quality Flags")

    flagged_orders = add_order_quality_flags(
        orders
    )

    total_anomalies = int(
        (~flagged_orders["date_sequence_valid"]).sum()
    )

    approved_carrier_anomalies = int(
        flagged_orders["approved_carrier_anomaly"].sum()
    )

    carrier_customer_anomalies = int(
        flagged_orders["carrier_customer_anomaly"].sum()
    )

    print(
        f"Orders with any date anomaly: "
        f"{total_anomalies:,}"
    )

    print(
    f"Approved to Carrier anomalies: "
    f"{approved_carrier_anomalies:,}"
    )
    print(
        f"Carrier to Customer anomalies: "
        f"{carrier_customer_anomalies:,}"
    )

    anomaly_report = flagged_orders[
        ~flagged_orders["date_sequence_valid"]
    ].copy()

    anomaly_file = (
        REPORT_DIR
        / "order_date_quality_flags.csv"
    )

    anomaly_report.to_csv(
        anomaly_file,
        index=False
    )

    # ---------------------------------------------------------
    # Final Report
    # ---------------------------------------------------------

    results_df = pd.DataFrame(results)

    report_file = (
        REPORT_DIR
        / "silver_validation_report.csv"
    )

    results_df.to_csv(
        report_file,
        index=False
    )

    passed = int(
        (results_df["status"] == "PASS").sum()
    )

    failed = int(
        (results_df["status"] == "FAIL").sum()
    )

    print("\n" + "=" * 70)
    print("Validation Summary")
    print("=" * 70)

    print(
        f"Total checks : {len(results_df)}"
    )

    print(
        f"Passed       : {passed}"
    )

    print(
        f"Failed       : {failed}"
    )

    print("\nReports saved:")
    print(report_file)
    print(anomaly_file)

    print("=" * 70)


if __name__ == "__main__":
    run_validation()