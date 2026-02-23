import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=20)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    return response.choices[0].message.content.strip()