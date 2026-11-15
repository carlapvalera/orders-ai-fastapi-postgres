import re

import sqlglot
from sqlglot import exp

ALLOWED_VIEWS = {"sales_by_month_country", "top_customers"}
FORBIDDEN_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", "create", "truncate", "attach", "copy", "pragma", "call",
}


def validate_read_only_sql(sql: str) -> str:
    """Validate a single SELECT against the small analytics surface exposed by the API."""
    query = sql.strip().rstrip(";").strip()
    if not query:
        raise ValueError("The generated query is empty")
    if ";" in query:
        raise ValueError("Multiple SQL statements are not allowed")
    try:
        parsed = sqlglot.parse(query, read="postgres")
    except sqlglot.errors.ParseError as exc:
        raise ValueError("Generated SQL is not valid PostgreSQL") from exc
    if len(parsed) != 1 or not isinstance(parsed[0], exp.Select):
        raise ValueError("Only SELECT queries are allowed")
    if re.search(r"--|/\*|\*/", query):
        raise ValueError("SQL comments are not allowed")
    lowered = query.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            raise ValueError(f"Forbidden SQL keyword: {keyword}")
    referenced_tables = list(parsed[0].find_all(exp.Table))
    referenced = {table.name.lower() for table in referenced_tables}
    if any(table.db or table.catalog for table in referenced_tables):
        raise ValueError("Qualified table names are not allowed")
    if not referenced or not referenced.issubset(ALLOWED_VIEWS):
        raise ValueError("Query must use only the allowed analytics views")
    return query

