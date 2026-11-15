from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = ["order_date", "customer", "country", "product", "amount", "status"]


def clean_orders(csv_path: str | Path) -> tuple[pd.DataFrame, dict[str, int]]:
    """Clean raw orders and return rows suitable for analytics."""
    raw = pd.read_csv(csv_path, dtype=str)
    raw.columns = [column.strip().lower() for column in raw.columns]
    missing = set(EXPECTED_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    frame = raw[EXPECTED_COLUMNS].copy()
    initial_rows = len(frame)
    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce", dayfirst=False)
    frame["amount"] = pd.to_numeric(frame["amount"].str.replace(",", ".", regex=False), errors="coerce")
    frame["status"] = frame["status"].str.strip().str.lower()
    frame["country"] = frame["country"].str.strip()
    frame["customer"] = frame["customer"].str.strip()
    frame["product"] = frame["product"].str.strip()

    invalid_date = frame["order_date"].isna()
    missing_amount = frame["amount"].isna()
    duplicate = frame.duplicated(keep="first")
    clean = frame.loc[~invalid_date & ~missing_amount & ~duplicate].copy()
    clean["order_date"] = clean["order_date"].dt.date

    stats = {
        "input_rows": initial_rows,
        "invalid_dates": int(invalid_date.sum()),
        "missing_amounts": int(missing_amount.sum()),
        "duplicates_removed": int(duplicate.sum()),
        "output_rows": len(clean),
    }
    return clean, stats

