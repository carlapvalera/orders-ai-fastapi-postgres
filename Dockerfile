FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY sql ./sql
COPY data ./data

EXPOSE 8000

CMD ["sh", "-c", "python scripts/generate_data.py && python -m scripts.load_data && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

