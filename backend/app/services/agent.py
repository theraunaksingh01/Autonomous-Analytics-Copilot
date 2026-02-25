from app.services.planner import plan_analysis
from app.services.code_generator import generate_code
from app.services.sandbox import execute_code
from app.services.chart_engine import build_chart
from app.services.summary_engine import generate_summary
from app.services.confidence_engine import evaluate_confidence
from app.services.memory_engine import build_memory_context, update_memory
from app.services.stat_tool import descriptive_statistics
from app.services.anomaly_tool import detect_anomalies

import pandas as pd
import time


# ---------------------------------------------------
# Detect categorical value mentioned in question
# ---------------------------------------------------
def find_category_match(df, question):
    question_lower = question.lower()

    for col in df.select_dtypes(include="object").columns:
        unique_values = df[col].dropna().unique()

        for val in unique_values:
            if str(val).lower() in question_lower:
                return col, val

    return None, None


# ---------------------------------------------------
# Normalize numeric columns safely
# ---------------------------------------------------
def normalize_dataframe(df):
    for col in df.columns:
        try:
            converted = pd.to_numeric(df[col], errors="coerce")
            # Replace only if at least some numeric values exist
            if not converted.isna().all():
                df[col] = converted
        except:
            pass
    return df


# ---------------------------------------------------
# MAIN AGENT
# ---------------------------------------------------
def run_agent(filepath: str, question: str, db, file_id: int):

    start_time = time.time()

    # Load dataset
    df = pd.read_csv(filepath)

    # Normalize types
    df = normalize_dataframe(df)

    # Inject memory only for short follow-ups
    if len(question.split()) <= 5:
        memory_context = build_memory_context(db, file_id)
    else:
        memory_context = ""

    # Plan analysis
    plan = plan_analysis(df, question, memory_context)
    print("PLAN:", plan)

    analysis_type = plan.get("analysis_type")

    # ------------------------------------------
    # TOOL ROUTING
    # ------------------------------------------
    if analysis_type == "statistics" and plan.get("columns_used"):
        column = plan["columns_used"][0]
        answer = descriptive_statistics(df, column)
        generated_code = "Used built-in statistical tool"

    elif analysis_type == "anomaly" and plan.get("columns_used"):
        column = plan["columns_used"][0]
        answer = detect_anomalies(df, column)
        generated_code = "Used built-in anomaly detection tool"

    elif analysis_type == "category_filter":

        # Smart detection from question
        col, val = find_category_match(df, question)

        if col and val:
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) == 0:
                answer = f"No numeric columns available for aggregation in category '{val}'."
                generated_code = None
            else:
                target_col = numeric_cols[0]
                value = df[df[col] == val][target_col].mean()
                answer = float(value) if pd.notna(value) else None
                generated_code = f"df[df['{col}']=='{val}']['{target_col}'].mean()"
        else:
            answer = "No matching category found in dataset."
            generated_code = None

    else:
        # Default execution path
        generated_code = generate_code(df, question, plan)
        execution_result = execute_code(df, generated_code)

        if isinstance(execution_result, dict) and "error" in execution_result:
            return {
                "answer": execution_result["error"],
                "generated_code": generated_code,
                "chart": None,
                "summary": "Execution failed due to invalid column or operation.",
                "confidence": 0.3,
                "latency": 0,
                "plan": plan
            }

        answer = execution_result

    # ------------------------------------------
    # CHART
    # ------------------------------------------
    chart = build_chart(answer, question)

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------
    summary = generate_summary(df, answer, question)

    # ------------------------------------------
    # CONFIDENCE
    # ------------------------------------------
    confidence = evaluate_confidence(question, answer)

    # Normalize confidence to 0–1
    try:
        confidence = float(confidence)
        if confidence > 1:
            confidence = confidence / 100
        confidence = min(max(confidence, 0), 1)
    except:
        confidence = 0.5

    # ------------------------------------------
    # MEMORY UPDATE
    # ------------------------------------------
    try:
        update_memory(db, file_id, question, str(answer))
    except:
        pass

    latency = round(time.time() - start_time, 3)

    # ------------------------------------------
    # FINAL RESPONSE
    # ------------------------------------------
    return {
        "answer": answer,
        "generated_code": generated_code,
        "chart": chart,
        "summary": summary,
        "confidence": confidence,
        "latency": latency,
        "plan": plan
    }