import pandas as pd

from app.cleaning import clean_orders


def test_cleaning_removes_bad_dates_missing_amounts_and_duplicates(tmp_path):
    source = tmp_path / "orders.csv"
    pd.DataFrame(
        [
            ["2024-01-01", "A", "Spain", "Phone", "10", "completed"],
            ["2024-01-01", "A", "Spain", "Phone", "10", "completed"],
            ["bad-date", "B", "France", "Tablet", "20", "completed"],
            ["2024-01-03", "C", "Spain", "Laptop", "", "completed"],
        ],
        columns=["order_date", "customer", "country", "product", "amount", "status"],
    ).to_csv(source, index=False)
    clean, stats = clean_orders(source)
    assert len(clean) == 1
    assert stats["duplicates_removed"] == 1
    assert stats["invalid_dates"] == 1
    assert stats["missing_amounts"] == 1

