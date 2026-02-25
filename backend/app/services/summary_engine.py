from app.services.llm_client import call_llm
import json
import pandas as pd



def safe_serialize(obj):
    """
    Converts pandas objects into JSON-safe Python types.
    """
    if isinstance(obj, pd.Series):
        return obj.to_dict()

    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")

    if isinstance(obj, list):
        return [safe_serialize(i) for i in obj]

    return obj




def generate_summary(df, result, question: str):
    """
    Generates executive-level summary of analysis result.
    Avoids sending large payloads to LLM.
    Handles pandas objects safely.
    """

    # 🔥 Normalize pandas objects
    if isinstance(result, pd.Series):
        result_summary = result.to_dict()

    elif isinstance(result, pd.DataFrame):
        result_summary = result.head(10).to_dict(orient="records")

    elif isinstance(result, list) and len(result) > 10:
        preview = result[:5]
        result_summary = {
            "total_records": len(result),
            "sample_records": result[:5]
        }

    else:
        result_summary = result

    system_prompt = """
You are a Senior Data Analyst.

Provide a short executive-level insight based on the analysis result.

Rules:
- 2–4 sentences
- Highlight key findings
- Mention severity if anomalies
- No markdown
- No bullet points
"""

    user_prompt = f"""
User Question:
{question}

Analysis Result:
{json.dumps(result_summary, indent=2, default=str)}

Dataset Size:
{len(df)}
"""

    return call_llm(system_prompt, user_prompt)