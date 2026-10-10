from pathlib import Path
import pandas as pd


FACT_SALES = Path("data/gold/facts/fact_sales/data.parquet")
SILVER_ORDERS = Path("data/silver/orders/data.parquet")
SILVER_ORDER_ITEMS = Path("data/silver/order_items/data.parquet")


def check(name, condition, details=""):
    status = "PASS" if condition else "FAIL"

    print(f"{name}: {status}")

    if details:
        print(f"  {details}")

    return {
        "check": name,
        "status": status,
        "details": details,
    }


def main():
    print("Reading fact_sales...")
    fact_sales = pd.read_parquet(FACT_SALES)

    print("Reading Silver order_items...")
    order_items = pd.read_parquet(SILVER_ORDER_ITEMS)

    print("Reading Silver orders...")
    orders = pd.read_parquet(SILVER_ORDERS)

    results = []

    print("\n1. Row Count Validation")

    results.append(
        check(
            "Fact row count matches order_items",
            len(fact_sales) == len(order_items),
            f"fact_sales={len(fact_sales):,}, "
            f"order_items={len(order_items):,}",
        )
    )

    print("\n2. Grain Validation")

    duplicate_grain = fact_sales.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()

    results.append(
        check(
            "Order item grain is unique",
            duplicate_grain == 0,
            f"duplicate_grain_rows={duplicate_grain:,}",
        )
    )

    print("\n3. Foreign Key Validation")

    for column in [
        "customer_key",
        "product_key",
        "seller_key",
        "date_key",
    ]:
        null_count = fact_sales[column].isna().sum()

        results.append(
            check(
                f"{column} has no null values",
                null_count == 0,
                f"nulls={null_count:,}",
            )
        )

    print("\n4. Referential Integrity")

    missing_orders = (
        ~fact_sales["order_id"].isin(orders["order_id"])
    ).sum()

    results.append(
        check(
            "All fact orders exist in Silver orders",
            missing_orders == 0,
            f"missing_orders={missing_orders:,}",
        )
    )

    print("\n5. Numeric Validation")

    negative_price = (fact_sales["price"] < 0).sum()
    negative_freight = (fact_sales["freight_value"] < 0).sum()

    results.append(
        check(
            "Price values are non-negative",
            negative_price == 0,
            f"negative_price_rows={negative_price:,}",
        )
    )

    results.append(
        check(
            "Freight values are non-negative",
            negative_freight == 0,
            f"negative_freight_rows={negative_freight:,}",
        )
    )

    print("\n6. Measure Validation")

    expected_total = (
        fact_sales["price"] + fact_sales["freight_value"]
    )

    incorrect_total = (
        fact_sales["total_item_value"] != expected_total
    ).sum()

    results.append(
        check(
            "total_item_value calculation is correct",
            incorrect_total == 0,
            f"incorrect_rows={incorrect_total:,}",
        )
    )

    print("\n7. Sales Key Validation")

    duplicate_sales_keys = fact_sales["sales_key"].duplicated().sum()

    results.append(
        check(
            "sales_key is unique",
            duplicate_sales_keys == 0,
            f"duplicate_sales_keys={duplicate_sales_keys:,}",
        )
    )

    print("\nValidation Summary")

    total_checks = len(results)
    passed = sum(
        result["status"] == "PASS"
        for result in results
    )
    failed = total_checks - passed

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    report = pd.DataFrame(results)

    report_dir = Path("reports/gold_quality")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = (
        report_dir / "fact_sales_validation_report.csv"
    )

    report.to_csv(report_file, index=False)

    print(f"\nReport saved:")
    print(report_file)


if __name__ == "__main__":
    main()