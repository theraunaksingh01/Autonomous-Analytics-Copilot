import numpy as np
import pandas as pd


def generate_executive_summary(df: pd.DataFrame, insights: dict):

    total_rows = len(df)
    total_cols = len(df.columns)

    summary_lines = []

    # Dataset size overview
    summary_lines.append(
        f"This dataset contains {total_rows} records across {total_cols} features."
    )

    # Missing values warning
    missing_report = (
        df.isnull().mean() * 100
    ).sort_values(ascending=False)

    high_missing = missing_report[missing_report > 50]

    if not high_missing.empty:
        for col, pct in high_missing.items():
            summary_lines.append(
                f"Column '{col}' has significant missing values ({pct:.1f}%), which may affect reliability."
            )

    # Skew detection
    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        skewness = df[col].skew()
        if skewness > 1:
            summary_lines.append(
                f"'{col}' is heavily positively skewed, indicating potential extreme high values."
            )
        elif skewness < -1:
            summary_lines.append(
                f"'{col}' is heavily negatively skewed, suggesting concentration near upper bounds."
            )

    # Imbalance detection (categorical)
    categorical_cols = df.select_dtypes(exclude=np.number).columns

    for col in categorical_cols:
        value_counts = df[col].value_counts(normalize=True)
        if not value_counts.empty:
            top_ratio = value_counts.iloc[0]
            if top_ratio > 0.8:
                summary_lines.append(
                    f"'{col}' is highly imbalanced — one category dominates ({top_ratio*100:.1f}%)."
                )

    if not summary_lines:
        summary_lines.append(
            "No significant structural risks detected in dataset."
        )

    return " ".join(summary_lines)