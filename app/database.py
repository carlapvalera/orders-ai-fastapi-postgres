from pathlib import Path

import duckdb


DEFAULT_DATABASE_PATH = Path("data/orders.duckdb")


def get_connection(database_path: str | Path = DEFAULT_DATABASE_PATH) -> duckdb.DuckDBPyConnection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))

