import json
from app.services.llm_client import call_llm


def plan_analysis(df, question, memory_context=None):
    q = question.lower()

    # --------- RULE-BASED FAST PATH ---------
    if "anomal" in q or "outlier" in q:
        return {
            "analysis_type": "anomaly",
            "steps": ["Detect anomalies using IQR"],
            "columns_used": list(df.select_dtypes(include='number').columns),
            "needs_chart": True,
            "chart_type": "boxplot"
        }

    if "stat" in q or "mean" in q or "median" in q:
        return {
            "analysis_type": "statistics",
            "steps": ["Compute descriptive statistics"],
            "columns_used": list(df.select_dtypes(include='number').columns),
            "needs_chart": False,
            "chart_type": "none"
        }

    # --------- LLM FALLBACK (Only if complex) ---------
    system_prompt = """
You are a data analysis planner.
Return JSON with:
analysis_type
steps
columns_used
needs_chart
chart_type
"""

    user_prompt = f"""
Dataset columns:
{list(df.columns)}

Question:
{question}
"""

    response = call_llm(system_prompt, user_prompt)

    try:
        return json.loads(response)
    except:
        return {
            "analysis_type": "general",
            "steps": ["Run basic aggregation"],
            "columns_used": list(df.columns[:2]),
            "needs_chart": False,
            "chart_type": "none"
        }