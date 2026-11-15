import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.database import get_connection
from app.llm import question_to_sql
from app.sql_validation import validate_read_only_sql

load_dotenv()

app = FastAPI(title="Orders AI API", version="1.0.0")


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask")
def ask_orders(request: QuestionRequest) -> dict[str, object]:
    try:
        generated_sql = question_to_sql(request.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    try:
        safe_sql = validate_read_only_sql(generated_sql)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid generated query: {exc}") from exc

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(safe_sql)
                columns = [description.name for description in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            connection.commit()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Query execution error: {exc}") from exc
    return {"question": request.question, "sql": safe_sql, "results": result}

