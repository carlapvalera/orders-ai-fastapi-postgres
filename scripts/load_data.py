from pathlib import Path

from app.cleaning import clean_orders
from app.database import get_connection


def load_orders(input_path: str | Path = "data/orders_raw.csv", database_path: str | Path = "data/orders.duckdb") -> dict[str, int]:
    clean, stats = clean_orders(input_path)
    with get_connection(database_path) as connection:
        connection.execute("DROP TABLE IF EXISTS orders")
        connection.register("clean_orders", clean)
        connection.execute("CREATE TABLE orders AS SELECT * FROM clean_orders")
        connection.execute("DROP VIEW IF EXISTS sales_by_month_country")
        connection.execute("DROP VIEW IF EXISTS top_customers")
        connection.execute(Path("sql/views.sql").read_text(encoding="utf-8"))
    Path("data/orders_clean.csv").parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv("data/orders_clean.csv", index=False)
    return stats


if __name__ == "__main__":
    print(load_orders())

