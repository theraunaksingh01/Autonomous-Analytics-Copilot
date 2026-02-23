from app.services.planner import plan_analysis
from app.services.code_generator import generate_code
from app.services.sandbox import execute_code
from app.services.chart_engine import build_chart
from app.services.summary_engine import generate_summary
from app.services.confidence_engine import evaluate_confidence
from app.services.memory_engine import get_memory, update_memory
from app.services.stat_tool import descriptive_statistics
from app.services.anomaly_tool import detect_anomalies

import pandas as pd
import time


def run_agent(filepath: str, question: str):
    start_time = time.time()

    df = pd.read_csv(filepath)

    memory_context = get_memory()

    # 1️⃣ Planning
    plan = plan_analysis(df, question, memory_context)
    print("PLAN:", plan)

    analysis_type = plan.get("analysis_type")

    if analysis_type == "statistics" and plan.get("columns_used"):
        column = plan["columns_used"][0]
        result = descriptive_statistics(df, column)
        code = "Used built-in statistical tool"
    
    elif analysis_type == "anomaly" and plan.get("columns_used"):
        column = plan["columns_used"][0]
        result = detect_anomalies(df, column)
        code = "Used built-in anomaly detection tool"
    
    else:
        code = generate_code(df, question, plan)
        result = execute_code(df, code)

    # 4️⃣ Chart Decision
    chart = build_chart(result, question)

    # 5️⃣ Executive Summary
    summary = generate_summary(df, result, question)

    # 6️⃣ Confidence Evaluation
    confidence = evaluate_confidence(question, result)

    # 7️⃣ Update Memory
    update_memory(question, result)

    latency = round(time.time() - start_time, 3)

    return {
        "answer": str(result),
        "generated_code": code,
        "chart": chart,
        "summary": summary,
        "confidence": confidence,
        "latency": latency,
        "plan": plan
    }