from app.services.llm_client import call_llm
import json


def evaluate_confidence(question: str, result):
    """
    Evaluates reliability of analysis result.
    Avoids sending large payloads to LLM.
    """

    # Compress large results
    if isinstance(result, list):
        result_summary = {
            "result_type": "list",
            "total_items": len(result),
            "sample": result[:3]
        }
    elif isinstance(result, dict):
        result_summary = {
            "result_type": "dict",
            "keys": list(result.keys())[:5]
        }
    else:
        result_summary = str(result)[:300]

    system_prompt = """
You are a Data Quality Auditor.

Rate confidence from 0 to 100 based on:
- clarity of result
- completeness
- statistical reliability

Return ONLY a number.
"""

    user_prompt = f"""
User Question:
{question}

Result Summary:
{json.dumps(result_summary, indent=2)}
"""

    response = call_llm(system_prompt, user_prompt)

    try:
        return int("".join(filter(str.isdigit, response)))
    except:
        return 80  # safe fallback