import pandas as pd
import numpy as np

def generate_dataset_insights(file_location: str):
    df = pd.read_csv(file_location)

    rows, cols = df.shape

    # ---------- KEY FINDINGS ----------
    key_findings = []

    # Missing values
    missing_percent = (df.isnull().sum() / len(df)) * 100
    high_missing = missing_percent[missing_percent > 50]

    for col, pct in high_missing.items():
        key_findings.append(
            f"Column '{col}' has {round(pct,1)}% missing values."
        )

    # Numeric skew & outliers
    numeric_cols = df.select_dtypes(include=np.number).columns
    
    total_outliers = 0

    for col in numeric_cols:
        skew = df[col].skew()

        if skew > 1:
            key_findings.append(f"'{col}' is positively skewed.")
        elif skew < -1:
            key_findings.append(f"'{col}' is negatively skewed.")

        # IQR outlier detection
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        outliers = df[
            (df[col] < Q1 - 1.5 * IQR) |
            (df[col] > Q3 + 1.5 * IQR)
        ]

        outlier_count = len(outliers)

        if outlier_count > 0:
            key_findings.append(
                f"{outlier_count} potential outliers detected in '{col}'."
            )
    
        total_outliers += outlier_count

    # ---------- SUGGESTED QUESTIONS ----------
    suggested_questions = []

    for col in df.columns[:3]:
        if df[col].dtype == "object":
            suggested_questions.append(f"Show distribution of {col}")
        else:
            suggested_questions.append(f"What is the average of {col}?")

    # ---------- EXECUTIVE SUMMARY ----------
    executive_summary = (
        f"This dataset contains {rows} rows and {cols} columns. "
        f"It includes {len(numeric_cols)} numeric columns. "
        f"Several statistical irregularities were detected."
    )
    
    # ---- DATA HEALTH SCORE ----

    health_score = 100

    # Penalize heavy missing columns
    high_missing = [
        col for col in df.columns
        if df[col].isnull().mean() > 0.5
    ]

    if high_missing:
        health_score -= min(20, len(high_missing) * 5)

    # Penalize high outliers
    if total_outliers > 100:
        health_score -= 15
    elif total_outliers > 50:
        health_score -= 10

    health_score = max(50, health_score)

    # ---------- FINAL RETURN ----------
    return {
        "overview": {
            "rows": int(rows),
            "columns": int(cols)
        },
        "key_findings": key_findings,
        "suggested_questions": suggested_questions,
        "executive_summary": executive_summary,
        "health_score": health_score
    }