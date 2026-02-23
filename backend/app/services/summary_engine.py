from app.services.llm_client import call_llm
import json


def generate_summary(df, result, question: str):
    """
    Generates executive-level summary of analysis result.
    Avoids sending large payloads to LLM.
    """

    # If result is large list (e.g., anomalies)
    if isinstance(result, list) and len(result) > 10:
        preview = result[:5]
        result_summary = {
            "total_records": len(result),
            "sample_records": preview
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
{json.dumps(result_summary, indent=2)}

Dataset Size:
{len(df)}
"""

    return call_llm(system_prompt, user_prompt)