from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def clean_sql_response(response: str) -> str:
    response = response.strip()

    response = response.replace("```sql", "")
    response = response.replace("```", "")

    return response.strip()

def clean_json_response(response: str) -> str:
    response = response.strip()

    response = response.replace("```json", "")
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
def generate_json(prompt: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres un generador de JSON para sistemas de Business Intelligence. Devuelve únicamente JSON válido, sin Markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    raw_json = response.choices[0].message.content.strip()

    return clean_json_response(raw_json)


def generate_text(prompt: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un analista ejecutivo de Business Intelligence. "
                    "Genera explicaciones claras, prudentes y basadas únicamente en los datos proporcionados."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()