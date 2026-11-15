from pathlib import Path
from decimal import Decimal, InvalidOperation

import pandas as pd


EXPECTED_COLUMNS = ["order_date", "customer", "country", "product", "amount", "status"]


def parse_amount(value: str) -> Decimal | None:
    try:
        return Decimal(value.strip().replace(",", ".")).quantize(Decimal("0.01"))
    except (InvalidOperation, AttributeError):
        return None


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
    frame["amount"] = frame["amount"].map(parse_amount)
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
        "rejected_rows": initial_rows - len(clean),
        "rejection_rate_percent": round((initial_rows - len(clean)) / initial_rows * 100, 2),
    }
    return clean, stats


def collect_quality_issues(csv_path: str | Path) -> pd.DataFrame:
    """Return raw rows and reasons for every rejected quality issue."""
    raw = pd.read_csv(csv_path, dtype=str).fillna("")
    raw.columns = [column.strip().lower() for column in raw.columns]
    frame = raw[EXPECTED_COLUMNS].copy()
    parsed_dates = pd.to_datetime(frame["order_date"], errors="coerce")
    parsed_amounts = frame["amount"].map(parse_amount)
    issue_rows: list[dict[str, object]] = []

    masks = [
        ("invalid_date", parsed_dates.isna()),
        ("missing_amount", (frame["amount"] == "") | parsed_amounts.isna()),
        ("duplicate", frame.duplicated(keep="first")),
    ]
    for issue_type, mask in masks:
        for index in frame.index[mask]:
            issue_rows.append({"original_row_number": int(index) + 2, "issue_type": issue_type, **frame.loc[index].to_dict()})
    return pd.DataFrame(issue_rows, columns=["original_row_number", "issue_type", *EXPECTED_COLUMNS])

