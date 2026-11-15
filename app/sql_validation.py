import re


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
    if not re.match(r"^select\b", query, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")
    if re.search(r"--|/\*|\*/", query):
        raise ValueError("SQL comments are not allowed")
    lowered = query.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            raise ValueError(f"Forbidden SQL keyword: {keyword}")
    referenced = set(re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", lowered))
    if not referenced or not referenced.issubset(ALLOWED_VIEWS):
        raise ValueError("Query must use only the allowed analytics views")
    return query

