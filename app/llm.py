import os

from openai import OpenAI


SYSTEM_PROMPT = """You translate Spanish or English questions about orders into DuckDB SQL.
Return only one SQL SELECT statement, with no Markdown and no explanation.
You may query only sales_by_month_country and top_customers.
sales_by_month_country columns: month, country, total_sales, order_count.
top_customers columns: customer, total_spend, order_count.
"""


def question_to_sql(question: str) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        instructions=SYSTEM_PROMPT,
        input=question,
        temperature=0,
    )
    return response.output_text.strip()

