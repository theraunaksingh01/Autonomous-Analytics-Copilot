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

        outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
        if len(outliers) > 0:
            key_findings.append(
                f"{len(outliers)} potential outliers detected in '{col}'."
            )

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

    # ---------- FINAL RETURN ----------
    return {
        "overview": {
            "rows": int(rows),
            "columns": int(cols)
        },
        "key_findings": key_findings,
        "suggested_questions": suggested_questions,
        "executive_summary": executive_summary
    }