from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

FACT_PATH = (
    BASE_DIR
    / "data"
    / "gold"
    / "facts"
    / "fact_reviews"
    / "data.parquet"
)

REVIEWS_PATH = (
    BASE_DIR
    / "data"
    / "silver"
    / "order_reviews"
    / "data.parquet"
)

ORDERS_PATH = (
    BASE_DIR
    / "data"
    / "silver"
    / "orders"
    / "data.parquet"
)

REPORT_DIR = BASE_DIR / "reports" / "gold_quality"


print("Reading fact_reviews...")
fact = pd.read_parquet(FACT_PATH)

print("Reading Silver order_reviews...")
reviews = pd.read_parquet(REVIEWS_PATH)

print("Reading Silver orders...")
orders = pd.read_parquet(ORDERS_PATH)


results = []


def add_result(check, passed, details):
    results.append(
        {
            "check": check,
            "status": "PASS" if passed else "FAIL",
            "details": details,
        }
    )


# ---------------------------------------------------------
# 1. Row Count Validation
# ---------------------------------------------------------

print("\n1. Row Count Validation")

fact_count = len(fact)
review_count = len(reviews)

passed = fact_count == review_count

add_result(
    "Fact row count matches order_reviews",
    passed,
    f"fact_reviews={fact_count:,}, order_reviews={review_count:,}",
)

print(
    f"Fact row count matches order_reviews: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  fact_reviews={fact_count:,}, "
    f"order_reviews={review_count:,}"
)


# ---------------------------------------------------------
# 2. Review Grain Validation
# ---------------------------------------------------------

print("\n2. Review Grain Validation")

duplicate_grain = fact.duplicated(
    subset=["review_id", "order_id"]
).sum()

passed = duplicate_grain == 0

add_result(
    "Review grain is unique",
    passed,
    f"duplicate_grain_rows={duplicate_grain}",
)

print(
    f"Review grain is unique: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  duplicate_grain_rows={duplicate_grain}")


# ---------------------------------------------------------
# 3. Review Key Validation
# ---------------------------------------------------------

print("\n3. Review Key Validation")

duplicate_keys = fact["review_key"].duplicated().sum()

passed = duplicate_keys == 0

add_result(
    "review_key is unique",
    passed,
    f"duplicate_review_keys={duplicate_keys}",
)

print(
    f"review_key is unique: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  duplicate_review_keys={duplicate_keys}")


# ---------------------------------------------------------
# 4. Customer Foreign Key Validation
# ---------------------------------------------------------

print("\n4. Customer Foreign Key Validation")

null_customer_keys = fact["customer_key"].isna().sum()

passed = null_customer_keys == 0

add_result(
    "customer_key has no null values",
    passed,
    f"nulls={null_customer_keys}",
)

print(
    f"customer_key has no null values: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  nulls={null_customer_keys}")


# ---------------------------------------------------------
# 5. Order Referential Integrity
# ---------------------------------------------------------

print("\n5. Order Referential Integrity")

valid_order_ids = set(orders["order_id"])

missing_orders = (
    ~fact["order_id"].isin(valid_order_ids)
).sum()

passed = missing_orders == 0

add_result(
    "All review orders exist in Silver orders",
    passed,
    f"missing_orders={missing_orders}",
)

print(
    f"All review orders exist in Silver orders: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  missing_orders={missing_orders}")


# ---------------------------------------------------------
# 6. Review Score Validation
# ---------------------------------------------------------

print("\n6. Review Score Validation")

invalid_scores = (
    fact["review_score"].isna()
    | (fact["review_score"] < 1)
    | (fact["review_score"] > 5)
).sum()

passed = invalid_scores == 0

add_result(
    "Review scores are between 1 and 5",
    passed,
    f"invalid_score_rows={invalid_scores}",
)

print(
    f"Review scores are between 1 and 5: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  invalid_score_rows={invalid_scores}")


# ---------------------------------------------------------
# 7. Review Creation Date Validation
# ---------------------------------------------------------

print("\n7. Review Creation Date Validation")

invalid_creation_dates = (
    fact["review_creation_date"].isna()
).sum()

passed = invalid_creation_dates == 0

add_result(
    "Review creation date is populated",
    passed,
    f"invalid_creation_date_rows={invalid_creation_dates}",
)

print(
    f"Review creation date is populated: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  invalid_creation_date_rows="
    f"{invalid_creation_dates}"
)


# ---------------------------------------------------------
# 8. Review Answer Timestamp Validation
# ---------------------------------------------------------

print("\n8. Review Answer Timestamp Validation")

invalid_answer_dates = (
    fact["review_answer_timestamp"].notna()
    & (
        fact["review_answer_timestamp"]
        < fact["review_creation_date"]
    )
).sum()

passed = invalid_answer_dates == 0

add_result(
    "Review answer is not before review creation",
    passed,
    f"invalid_answer_timestamp_rows={invalid_answer_dates}",
)

print(
    f"Review answer is not before review creation: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  invalid_answer_timestamp_rows="
    f"{invalid_answer_dates}"
)


# ---------------------------------------------------------
# 9. Review ID Validation
# ---------------------------------------------------------

print("\n9. Review ID Validation")

null_review_ids = fact["review_id"].isna().sum()

passed = null_review_ids == 0

add_result(
    "review_id is populated",
    passed,
    f"null_review_ids={null_review_ids}",
)

print(
    f"review_id is populated: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  null_review_ids={null_review_ids}")


# ---------------------------------------------------------
# 10. Order ID Validation
# ---------------------------------------------------------

print("\n10. Order ID Validation")

null_order_ids = fact["order_id"].isna().sum()

passed = null_order_ids == 0

add_result(
    "order_id is populated",
    passed,
    f"null_order_ids={null_order_ids}",
)

print(
    f"order_id is populated: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  null_order_ids={null_order_ids}")


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

report = pd.DataFrame(results)

total_checks = len(report)
passed_checks = (report["status"] == "PASS").sum()
failed_checks = (report["status"] == "FAIL").sum()


print("\nValidation Summary")
print("------------------")
print(f"Total checks: {total_checks}")
print(f"Passed: {passed_checks}")
print(f"Failed: {failed_checks}")


# ---------------------------------------------------------
# Save Report
# ---------------------------------------------------------

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

report_path = (
    REPORT_DIR
    / "fact_reviews_validation_report.csv"
)

report.to_csv(
    report_path,
    index=False
)

print("\nReport saved:")
print(report_path)


if failed_checks > 0:
    raise SystemExit(1)