from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


def explain_result(question, sql, df):

    result_text = df.to_string(index=False)

    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "business_explanation_prompt.txt"
    )

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.format(
        question=question,
        sql=sql,
        result=result_text
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres un analista senior de Business Intelligence."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()