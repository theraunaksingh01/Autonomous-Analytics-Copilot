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
    
    # 🔹 Detect category reference in question
    for col in df.select_dtypes(include="object").columns:
        unique_vals = df[col].dropna().unique()
        for val in unique_vals:
            if str(val).lower() in question.lower():
                return {
                    "analysis_type": "category_filter",
                    "steps": [f"Filter {col} == '{val}' and compute mean Rating"],
                    "columns_used": [col, "Rating"],
                    "needs_chart": False,
                    "chart_type": "none",
                    "category_column": col,
                    "category_value": val
                }

    # --------- LLM FALLBACK (Only if complex) ---------
    system_prompt = f"""
You are an advanced AI Data Analyst.

You have access to:
- statistical tools
- anomaly detection tools
- chart generation tools

Use prior conversation context when needed.

Previous Context:
{memory_context}
"""

    memory_hint = ""

    if memory_context:
        memory_hint = f"""
    Previous Conversation Context:
    {memory_context}

    If the current question is ambiguous (e.g., "what about", "why", "compare"),
    assume it refers to the previously discussed metric or grouping.
    """

    user_prompt = f"""
Dataset columns:
{list(df.columns)}

{memory_hint}

Question:
{question}

Return a JSON plan with:
- analysis_type: "statistics", "anomaly", or "general"
- steps: list of analysis steps to perform
- columns_used: which columns to analyze
- needs_chart: true/false
- chart_type: if needs_chart is true, suggest a chart type (e.g., "line", "bar", "boxplot")
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