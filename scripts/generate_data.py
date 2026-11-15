from __future__ import annotations

import csv
import calendar
import random
from datetime import date, timedelta
from pathlib import Path


def generate_orders(output: str | Path = "data/orders_raw.csv", rows: int = 1200, seed: int = 42) -> None:
    random.seed(seed)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    customers = [f"Customer {number:03d}" for number in range(1, 101)]
    customer_weights = [6.0 if number <= 10 else 2.5 if number <= 30 else 1.0 for number in range(1, 101)]
    countries = ["España", "Francia", "Alemania", "Italia", "Portugal"]
    country_weights = [0.38, 0.20, 0.18, 0.16, 0.08]
    products = {
        "Laptop": 1200,
        "Phone": 700,
        "Tablet": 450,
        "Monitor": 300,
        "Keyboard": 80,
        "Headphones": 140,
    }
    statuses = ["completed", "pending", "cancelled"]
    status_weights = [0.65, 0.25, 0.10]
    month_weights = [1.0, 0.9, 1.1, 1.0, 1.0, 0.9, 0.8, 0.85, 1.0, 1.1, 1.3, 1.5]
    start = date(2024, 1, 1)

    records: list[dict[str, object]] = []
    for order_id in range(1, rows + 1):
        month = random.choices(range(1, 13), weights=month_weights, k=1)[0]
        day = random.randint(1, calendar.monthrange(2024, month)[1])
        product = random.choice(list(products))
        amount = products[product] * random.lognormvariate(0, 0.35)
        records.append(
            {
                "order_date": date(2024, month, day).isoformat(),
                "customer": random.choices(customers, weights=customer_weights, k=1)[0],
                "country": random.choices(countries, weights=country_weights, k=1)[0],
                "product": product,
                "amount": f"{amount:.2f}",
                "status": random.choices(statuses, weights=status_weights, k=1)[0],
            }
        )

    # Intentional quality issues: duplicated rows, malformed dates and empty amounts.
    records.extend(records[:25])
    for index in range(30, 830, 40):
        records[index]["order_date"] = "not-a-date"
    for index in range(50, 950, 45):
        records[index]["amount"] = ""

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["order_date", "customer", "country", "product", "amount", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    generate_orders()

