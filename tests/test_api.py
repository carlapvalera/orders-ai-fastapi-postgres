from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_ask_endpoint_executes_mocked_llm_query():
    class Cursor:
        description = [type("Description", (), {"name": "country"})(), type("Description", (), {"name": "total_sales"})()]

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def execute(self, _query):
            return None

        def fetchall(self):
            return [("Spain", 123.45)]

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def cursor(self):
            return Cursor()

        def commit(self):
            return None

    with patch("app.main.get_connection", return_value=Connection()), patch("app.main.question_to_sql", return_value="SELECT country, total_sales FROM sales_by_month_country"):
        response = TestClient(app).post("/ask", json={"question": "¿Cuánto vendimos en España?"})
    assert response.status_code == 200
    assert response.json()["results"][0]["country"] == "Spain"


def test_ask_endpoint_returns_clear_error_when_llm_fails():
    with patch("app.main.question_to_sql", side_effect=RuntimeError("provider unavailable")):
        response = TestClient(app).post("/ask", json={"question": "total de ventas"})
    assert response.status_code == 502
    assert "LLM error" in response.json()["detail"]


def test_ask_endpoint_rejects_invalid_generated_sql():
    with patch("app.main.question_to_sql", return_value="DELETE FROM orders"):
        response = TestClient(app).post("/ask", json={"question": "borra los pedidos"})
    assert response.status_code == 422
    assert "Invalid generated query" in response.json()["detail"]

