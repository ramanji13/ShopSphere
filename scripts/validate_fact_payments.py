from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

FACT_PATH = (
    BASE_DIR
    / "data"
    / "gold"
    / "facts"
    / "fact_payments"
    / "data.parquet"
)

PAYMENTS_PATH = (
    BASE_DIR
    / "data"
    / "silver"
    / "order_payments"
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


print("Reading fact_payments...")
fact = pd.read_parquet(FACT_PATH)

print("Reading Silver order_payments...")
payments = pd.read_parquet(PAYMENTS_PATH)

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
payment_count = len(payments)

passed = fact_count == payment_count

add_result(
    "Fact row count matches order_payments",
    passed,
    f"fact_payments={fact_count:,}, order_payments={payment_count:,}",
)

print(
    f"Fact row count matches order_payments: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  fact_payments={fact_count:,}, "
    f"order_payments={payment_count:,}"
)


# ---------------------------------------------------------
# 2. Grain Validation
# ---------------------------------------------------------

print("\n2. Grain Validation")

duplicate_grain = fact.duplicated(
    subset=["order_id", "payment_sequential"]
).sum()

passed = duplicate_grain == 0

add_result(
    "Payment grain is unique",
    passed,
    f"duplicate_grain_rows={duplicate_grain}",
)

print(
    f"Payment grain is unique: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  duplicate_grain_rows={duplicate_grain}")


# ---------------------------------------------------------
# 3. Payment Key Validation
# ---------------------------------------------------------

print("\n3. Payment Key Validation")

duplicate_keys = fact["payment_key"].duplicated().sum()

passed = duplicate_keys == 0

add_result(
    "payment_key is unique",
    passed,
    f"duplicate_payment_keys={duplicate_keys}",
)

print(
    f"payment_key is unique: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  duplicate_payment_keys={duplicate_keys}")


# ---------------------------------------------------------
# 4. Foreign Key Validation
# ---------------------------------------------------------

print("\n4. Foreign Key Validation")

for column in ["customer_key", "date_key"]:

    null_count = fact[column].isna().sum()

    passed = null_count == 0

    add_result(
        f"{column} has no null values",
        passed,
        f"nulls={null_count}",
    )

    print(
        f"{column} has no null values: "
        f"{'PASS' if passed else 'FAIL'}"
    )
    print(f"  nulls={null_count}")


# ---------------------------------------------------------
# 5. Referential Integrity
# ---------------------------------------------------------

print("\n5. Referential Integrity")

valid_order_ids = set(orders["order_id"])

missing_orders = (
    ~fact["order_id"].isin(valid_order_ids)
).sum()

passed = missing_orders == 0

add_result(
    "All payment orders exist in Silver orders",
    passed,
    f"missing_orders={missing_orders}",
)

print(
    f"All payment orders exist in Silver orders: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(f"  missing_orders={missing_orders}")


# ---------------------------------------------------------
# 6. Payment Value Validation
# ---------------------------------------------------------

print("\n6. Payment Value Validation")

negative_values = (
    fact["payment_value"] < 0
).sum()

passed = negative_values == 0

add_result(
    "Payment values are non-negative",
    passed,
    f"negative_payment_value_rows={negative_values}",
)

print(
    f"Payment values are non-negative: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  negative_payment_value_rows="
    f"{negative_values}"
)


# ---------------------------------------------------------
# 7. Payment Installment Validation
# ---------------------------------------------------------

print("\n7. Payment Installment Validation")

invalid_installments = (
    fact["payment_installments"] < 1
).sum()

passed = invalid_installments == 0

add_result(
    "Payment installments are at least 1",
    passed,
    f"invalid_installment_rows={invalid_installments}",
)

print(
    f"Payment installments are at least 1: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  invalid_installment_rows="
    f"{invalid_installments}"
)


# ---------------------------------------------------------
# 8. Payment Type Validation
# ---------------------------------------------------------

print("\n8. Payment Type Validation")

null_payment_types = (
    fact["payment_type"].isna()
).sum()

empty_payment_types = (
    fact["payment_type"]
    .astype("string")
    .str.strip()
    .eq("")
    .sum()
)

invalid_payment_types = (
    null_payment_types + empty_payment_types
)

passed = invalid_payment_types == 0

add_result(
    "Payment type is populated",
    passed,
    f"invalid_payment_type_rows={invalid_payment_types}",
)

print(
    f"Payment type is populated: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  invalid_payment_type_rows="
    f"{invalid_payment_types}"
)


# ---------------------------------------------------------
# 9. Order ID Validation
# ---------------------------------------------------------

print("\n9. Order ID Validation")

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
# 10. Payment Sequential Validation
# ---------------------------------------------------------

print("\n10. Payment Sequential Validation")

invalid_sequences = (
    fact["payment_sequential"] < 1
).sum()

passed = invalid_sequences == 0

add_result(
    "payment_sequential values are at least 1",
    passed,
    f"invalid_sequence_rows={invalid_sequences}",
)

print(
    f"payment_sequential values are at least 1: "
    f"{'PASS' if passed else 'FAIL'}"
)
print(
    f"  invalid_sequence_rows="
    f"{invalid_sequences}"
)


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
    / "fact_payments_validation_report.csv"
)

report.to_csv(
    report_path,
    index=False
)

print("\nReport saved:")
print(report_path)


if failed_checks > 0:
    raise SystemExit(1)