import pandas as pd
from pathlib import Path


CUSTOMER_360_PATH = Path("data/gold/analytics/customer_360/data.parquet")
DIM_CUSTOMER_PATH = Path("data/gold/dimensions/dim_customer/data.parquet")

REPORT_DIR = Path("reports/gold_quality")
REPORT_PATH = REPORT_DIR / "customer_360_validation_report.csv"


def add_check(results, check_name, passed, details):
    results.append({
        "check_name": check_name,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })


def main():

    customer_360 = pd.read_parquet(CUSTOMER_360_PATH)
    dim_customer = pd.read_parquet(DIM_CUSTOMER_PATH)

    results = []

    # ---------------------------------------------------------
    # 1. Row count
    # ---------------------------------------------------------

    expected_count = len(dim_customer)
    actual_count = len(customer_360)

    add_check(
        results,
        "Customer count matches dimension",
        actual_count == expected_count,
        f"customer_360={actual_count}, dim_customer={expected_count}"
    )

    # ---------------------------------------------------------
    # 2. One row per customer
    # ---------------------------------------------------------

    duplicate_customers = customer_360["customer_id"].duplicated().sum()

    add_check(
        results,
        "One row per customer",
        duplicate_customers == 0,
        f"duplicate_customer_ids={duplicate_customers}"
    )

    # ---------------------------------------------------------
    # 3. customer_key uniqueness
    # ---------------------------------------------------------

    duplicate_keys = customer_360["customer_key"].duplicated().sum()

    add_check(
        results,
        "customer_key is unique",
        duplicate_keys == 0,
        f"duplicate_customer_keys={duplicate_keys}"
    )

    # ---------------------------------------------------------
    # 4. Spending cannot be negative
    # ---------------------------------------------------------

    negative_spending = (customer_360["total_spending"] < 0).sum()

    add_check(
        results,
        "Total spending is non-negative",
        negative_spending == 0,
        f"negative_rows={negative_spending}"
    )

    # ---------------------------------------------------------
    # 5. Orders cannot be negative
    # ---------------------------------------------------------

    negative_orders = (customer_360["total_orders"] < 0).sum()

    add_check(
        results,
        "Total orders is non-negative",
        negative_orders == 0,
        f"negative_rows={negative_orders}"
    )

    # ---------------------------------------------------------
    # 6. Items cannot be negative
    # ---------------------------------------------------------

    negative_items = (customer_360["total_items"] < 0).sum()

    add_check(
        results,
        "Total items is non-negative",
        negative_items == 0,
        f"negative_rows={negative_items}"
    )

    # ---------------------------------------------------------
    # 7. Average order value calculation
    # ---------------------------------------------------------

    expected_aov = (
        customer_360["total_spending"]
        / customer_360["total_orders"]
    )

    aov_difference = (
        customer_360["average_order_value"]
        - expected_aov
    ).abs()

    invalid_aov = (
        aov_difference > 0.01
    ).sum()

    add_check(
        results,
        "Average order value is mathematically correct",
        invalid_aov == 0,
        f"invalid_rows={invalid_aov}"
    )

    # ---------------------------------------------------------
    # 8. First purchase <= last purchase
    # ---------------------------------------------------------

    invalid_purchase_dates = (
        customer_360["first_purchase_date"]
        > customer_360["last_purchase_date"]
    ).sum()

    add_check(
        results,
        "First purchase is not after last purchase",
        invalid_purchase_dates == 0,
        f"invalid_rows={invalid_purchase_dates}"
    )

    # ---------------------------------------------------------
    # 9. Customer lifetime cannot be negative
    # ---------------------------------------------------------

    negative_lifetime = (
        customer_360["customer_lifetime_days"] < 0
    ).sum()

    add_check(
        results,
        "Customer lifetime is non-negative",
        negative_lifetime == 0,
        f"negative_rows={negative_lifetime}"
    )

    # ---------------------------------------------------------
    # 10. Review score range
    # ---------------------------------------------------------

    invalid_review_scores = customer_360[
        customer_360["average_review_score"].notna()
        & (
            (customer_360["average_review_score"] < 1)
            | (customer_360["average_review_score"] > 5)
        )
    ].shape[0]

    add_check(
        results,
        "Average review score is between 1 and 5",
        invalid_review_scores == 0,
        f"invalid_rows={invalid_review_scores}"
    )

    # ---------------------------------------------------------
    # 11. Payment value cannot be negative
    # ---------------------------------------------------------

    negative_payments = (
        customer_360["total_payment_value"] < 0
    ).sum()

    add_check(
        results,
        "Total payment value is non-negative",
        negative_payments == 0,
        f"negative_rows={negative_payments}"
    )

    # ---------------------------------------------------------
    # 12. All customer keys exist in dimension
    # ---------------------------------------------------------

    valid_customer_keys = set(
        dim_customer["customer_key"]
    )

    missing_customer_keys = (
        ~customer_360["customer_key"].isin(valid_customer_keys)
    ).sum()

    add_check(
        results,
        "All customer keys exist in dim_customer",
        missing_customer_keys == 0,
        f"missing_keys={missing_customer_keys}"
    )

    # ---------------------------------------------------------
    # Save report
    # ---------------------------------------------------------

    report = pd.DataFrame(results)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report.to_csv(
        REPORT_PATH,
        index=False
    )

    # ---------------------------------------------------------
    # Print summary
    # ---------------------------------------------------------

    passed = (report["status"] == "PASS").sum()
    failed = (report["status"] == "FAIL").sum()

    print("=" * 60)
    print("CUSTOMER 360 VALIDATION")
    print("=" * 60)

    print(f"Total checks : {len(report)}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {failed}")

    print("\nValidation Results:")
    print(report.to_string(index=False))

    print("\nReport saved to:")
    print(REPORT_PATH)

    if failed > 0:
        print("\nWARNING: Some validation checks failed.")
    else:
        print("\nAll customer_360 validation checks passed.")


if __name__ == "__main__":
    main()