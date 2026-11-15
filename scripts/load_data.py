from pathlib import Path

from dotenv import load_dotenv

from app.cleaning import clean_orders, collect_quality_issues
from app.database import get_connection

load_dotenv()


def load_orders(input_path: str | Path = "data/orders_raw.csv") -> dict[str, int]:
    clean, stats = clean_orders(input_path)
    issues = collect_quality_issues(input_path)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP VIEW IF EXISTS sales_by_month_country")
            cursor.execute("DROP VIEW IF EXISTS top_customers")
            cursor.execute("DROP TABLE IF EXISTS order_quality_summary")
            cursor.execute("DROP TABLE IF EXISTS order_quality_issues")
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("""CREATE TABLE orders (
                order_date DATE NOT NULL, customer TEXT NOT NULL, country TEXT NOT NULL,
                product TEXT NOT NULL, amount NUMERIC(12, 2) NOT NULL, status TEXT NOT NULL
            )""")
            cursor.executemany(
                "INSERT INTO orders (order_date, customer, country, product, amount, status) VALUES (%s, %s, %s, %s, %s, %s)",
                clean.itertuples(index=False, name=None),
            )
            cursor.execute("""CREATE TABLE order_quality_summary (
                metric TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )""")
            cursor.executemany(
                "INSERT INTO order_quality_summary (metric, value) VALUES (%s, %s)",
                [(metric, value) for metric, value in stats.items()],
            )
            cursor.execute("""CREATE TABLE order_quality_issues (
                row_number INTEGER NOT NULL,
                issue_type TEXT NOT NULL,
                order_date TEXT, customer TEXT, country TEXT,
                product TEXT, amount TEXT, status TEXT
            )""")
            cursor.executemany(
                "INSERT INTO order_quality_issues (row_number, issue_type, order_date, customer, country, product, amount, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                issues.itertuples(index=False, name=None),
            )
            cursor.execute(Path("sql/views.sql").read_text(encoding="utf-8"))
        connection.commit()
    Path("data/orders_clean.csv").parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv("data/orders_clean.csv", index=False)
    return stats


if __name__ == "__main__":
    print(load_orders())

