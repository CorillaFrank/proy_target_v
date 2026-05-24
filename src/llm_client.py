from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def clean_sql_response(response: str) -> str:
    response = response.strip()

    response = response.replace("```sql", "")
    response = response.replace("```", "")

    return response.strip()


def generate_sql(prompt: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres un generador SQL seguro para PostgreSQL. Devuelve únicamente SQL plano, sin Markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    raw_sql = response.choices[0].message.content.strip()

    return clean_sql_response(raw_sql)