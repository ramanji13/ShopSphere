from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_DIR = PROJECT_ROOT / "data" / "silver"
REPORT_DIR = PROJECT_ROOT / "reports" / "silver_quality"


def load_orders():
    file_path = SILVER_DIR / "orders" / "data.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_parquet(file_path)


def investigate():

    print("=" * 70)
    print("ShopSphere - Silver Anomaly Investigation")
    print("=" * 70)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    orders = load_orders()

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # Anomaly 1
    # Approved timestamp > Carrier handover timestamp
    # ---------------------------------------------------------

    anomaly_1 = orders[
        orders["order_approved_at"].notna()
        & orders["order_delivered_carrier_date"].notna()
        & (
            orders["order_delivered_carrier_date"]
            < orders["order_approved_at"]
        )
    ].copy()

    anomaly_1["difference_hours"] = (
        anomaly_1["order_delivered_carrier_date"]
        - anomaly_1["order_approved_at"]
    ).dt.total_seconds() / 3600

    # ---------------------------------------------------------
    # Anomaly 2
    # Carrier handover timestamp > Customer delivery timestamp
    # ---------------------------------------------------------

    anomaly_2 = orders[
        orders["order_delivered_carrier_date"].notna()
        & orders["order_delivered_customer_date"].notna()
        & (
            orders["order_delivered_customer_date"]
            < orders["order_delivered_carrier_date"]
        )
    ].copy()

    anomaly_2["difference_hours"] = (
        anomaly_2["order_delivered_customer_date"]
        - anomaly_2["order_delivered_carrier_date"]
    ).dt.total_seconds() / 3600

    # ---------------------------------------------------------
    # Save reports
    # ---------------------------------------------------------

    report_1 = REPORT_DIR / "orders_approved_before_carrier_anomalies.csv"
    report_2 = REPORT_DIR / "orders_carrier_before_customer_anomalies.csv"

    anomaly_1.to_csv(
        report_1,
        index=False
    )

    anomaly_2.to_csv(
        report_2,
        index=False
    )

    # ---------------------------------------------------------
    # Print summary
    # ---------------------------------------------------------

    print("\nAnomaly Type 1")
    print("-" * 70)
    print(
        "Approved timestamp > Carrier handover timestamp"
    )
    print(f"Records found: {len(anomaly_1):,}")

    if len(anomaly_1) > 0:
        print("\nDifference in hours:")
        print(anomaly_1["difference_hours"].describe())

        print("\nSample records:")
        print(
            anomaly_1[
                [
                    "order_id",
                    "order_purchase_timestamp",
                    "order_approved_at",
                    "order_delivered_carrier_date",
                    "difference_hours",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

    print("\n\nAnomaly Type 2")
    print("-" * 70)
    print(
        "Carrier handover timestamp > Customer delivery timestamp"
    )
    print(f"Records found: {len(anomaly_2):,}")

    if len(anomaly_2) > 0:
        print("\nDifference in hours:")
        print(anomaly_2["difference_hours"].describe())

        print("\nSample records:")
        print(
            anomaly_2[
                [
                    "order_id",
                    "order_purchase_timestamp",
                    "order_approved_at",
                    "order_delivered_carrier_date",
                    "order_delivered_customer_date",
                    "difference_hours",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

    print("\n\nReports saved:")
    print(report_1)
    print(report_2)

    print("\n" + "=" * 70)
    print("Anomaly investigation extraction completed.")
    print("=" * 70)


if __name__ == "__main__":
    investigate()