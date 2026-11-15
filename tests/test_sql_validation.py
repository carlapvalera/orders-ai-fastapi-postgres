import pytest

from app.sql_validation import validate_read_only_sql


def test_validation_allows_select_on_allowed_view():
    query = validate_read_only_sql("SELECT country, total_sales FROM sales_by_month_country;")
    assert query.startswith("SELECT")


@pytest.mark.parametrize("query", [
    "DROP TABLE orders",
    "SELECT * FROM orders",
    "SELECT * FROM top_customers; DELETE FROM top_customers",
])
def test_validation_rejects_unsafe_queries(query):
    with pytest.raises(ValueError):
        validate_read_only_sql(query)

