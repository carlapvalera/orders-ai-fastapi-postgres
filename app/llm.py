import os

from openai import OpenAI

from app.normalization import normalize_question


SYSTEM_PROMPT = """You translate Spanish or English questions about orders into PostgreSQL SQL.
Return only one SQL SELECT statement, with no Markdown and no explanation.
You may query only sales_by_month_country and top_customers.
sales_by_month_country columns: month (text in YYYY-MM format), country, total_sales, order_count.
top_customers columns: customer, total_spend, order_count.
Canonical countries: Spain/España/Spanish market -> España; France/Francia -> Francia; Germany/Alemania -> Alemania; Italy/Italia -> Italia; Portugal -> Portugal.
Canonical months: January/enero -> 01, February/febrero -> 02, March/marzo -> 03, and the remaining months follow the same numbering.
"""


def question_to_sql(question: str) -> str:
    client = OpenAI(
        api_key=os.environ["FIREWORKS_API_KEY"],
        base_url="https://api.fireworks.ai/inference/v1",
        timeout=15.0,
        max_retries=1,
    )
    normalized_question = normalize_question(question)
    response = client.chat.completions.create(
        model=os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/glm-5p3-flash"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": normalized_question},
        ],
        temperature=0,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Fireworks returned an empty response")
    return content.strip()

