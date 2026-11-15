from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


def generate_orders(output: str | Path = "data/orders_raw.csv", rows: int = 1200, seed: int = 42) -> None:
    random.seed(seed)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    customers = [f"Customer {number:03d}" for number in range(1, 101)]
    countries = ["Spain", "France", "Germany", "Italy", "Portugal"]
    products = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Headphones"]
    statuses = ["completed", "completed", "completed", "pending", "cancelled"]
    start = date(2024, 1, 1)

    records: list[dict[str, object]] = []
    for order_id in range(1, rows + 1):
        records.append(
            {
                "order_date": (start + timedelta(days=random.randrange(365))).isoformat(),
                "customer": random.choice(customers),
                "country": random.choice(countries),
                "product": random.choice(products),
                "amount": f"{random.uniform(15, 2500):.2f}",
                "status": random.choice(statuses),
            }
        )

    # Intentional quality issues: duplicated rows, malformed dates and empty amounts.
    records.extend(records[:25])
    for index in range(30, 830, 40):
        records[index]["order_date"] = "not-a-date"
    for index in range(50, 950, 45):
        records[index]["amount"] = ""

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["order_date", "customer", "country", "product", "amount", "status"])
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    generate_orders()

