from app.services.llm_client import call_llm
import json


def generate_code(df, question: str, plan: dict):
    """
    Generates executable pandas code using plan + question.
    Must return ONLY Python code.
    """

    schema = {
        "columns": list(df.columns),
        "dtypes": {col: str(df[col].dtype) for col in df.columns}
    }

    system_prompt = """
You are an AI Data Analyst.

You must generate ONLY executable Python code.

Rules:
- The dataframe is already loaded as `df`
- Store final output in a variable called `result`
- Use pandas only
- No markdown
- No explanations
- No triple backticks
- Do NOT import anything
"""

    user_prompt = f"""
Execution Plan:
{json.dumps(plan, indent=2)}

Dataset Schema:
{json.dumps(schema, indent=2)}

User Question:
{question}
"""

    code = call_llm(system_prompt, user_prompt)

    return code.strip()