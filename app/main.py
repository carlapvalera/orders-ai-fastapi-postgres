import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.database import get_connection
from app.llm import question_to_sql
from app.sql_validation import validate_read_only_sql

load_dotenv()

app = FastAPI(title="Orders AI API", version="1.0.0")
logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class AskResponse(BaseModel):
    question: str
    sql: str
    results: list[dict[str, object]]


class ErrorResponse(BaseModel):
    detail: str


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
    except Exception as exc:
        logger.exception("Health check database connection failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "ok"}


@app.post(
    "/ask",
    response_model=AskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Generated query could not be executed"},
        422: {"model": ErrorResponse, "description": "Generated query failed validation"},
        502: {"model": ErrorResponse, "description": "LLM provider error"},
        503: {"model": ErrorResponse, "description": "Required configuration or database is unavailable"},
    },
)
def ask_orders(request: QuestionRequest) -> AskResponse:
    missing = [name for name in ("FIREWORKS_API_KEY", "DATABASE_URL") if not os.getenv(name)]
    if missing:
        raise HTTPException(status_code=503, detail=f"Missing configuration: {', '.join(missing)}")
    try:
        generated_sql = question_to_sql(request.question)
    except Exception as exc:
        logger.exception("LLM request failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    try:
        safe_sql = validate_read_only_sql(generated_sql)
    except ValueError as exc:
        logger.warning("Generated SQL rejected: %s", exc)
        raise HTTPException(status_code=422, detail=f"Invalid generated query: {exc}") from exc

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(safe_sql)
                columns = [description.name for description in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            connection.commit()
    except Exception as exc:
        logger.exception("Query execution failed")
        raise HTTPException(status_code=400, detail=f"Query execution error: {exc}") from exc
    return AskResponse(question=request.question, sql=safe_sql, results=result)

