import os

import pytest

from app.database import get_connection
from scripts.load_data import load_orders


@pytest.mark.integration
def test_postgres_load_creates_expected_views():
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 to run PostgreSQL integration tests")

    stats = load_orders("data/orders_raw.csv")
    assert stats["output_rows"] > 1000

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sales_by_month_country")
            assert cursor.fetchone()[0] > 0
            cursor.execute("SELECT COUNT(*) FROM top_customers")
            assert cursor.fetchone()[0] == 10
            cursor.execute("SELECT COUNT(*) FROM order_quality_summary")
            assert cursor.fetchone()[0] == 5
            cursor.execute("SELECT COUNT(*) FROM order_quality_issues")
            assert cursor.fetchone()[0] >= 65

