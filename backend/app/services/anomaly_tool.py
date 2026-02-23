import pandas as pd
import numpy as np


def detect_anomalies(df, column: str, threshold: float = 2.5):
    if column not in df.columns:
        return {"error": "Column not found"}

    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": "Column is not numeric"}

    mean = df[column].mean()
    std = df[column].std()

    z_scores = (df[column] - mean) / std

    anomalies = df[np.abs(z_scores) > threshold]

    return anomalies.to_dict(orient="records")