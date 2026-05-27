from pathlib import Path
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

ALLOWED_CHART_TYPES = {
    "bar",
    "line",
    "scatter",
    "pie"
}

def recommend_chart_type(question, df):
    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "chart_recommendation_prompt.txt"
    )

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.format(
        question=question,
        columns=list(df.columns),
        sample=df.head(5).to_string(index=False)
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres un experto en visualización BI. Devuelve solo el tipo de gráfico."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    chart_type = response.choices[0].message.content.strip().lower()
    if chart_type not in ALLOWED_CHART_TYPES:
        return "bar"
    return chart_type