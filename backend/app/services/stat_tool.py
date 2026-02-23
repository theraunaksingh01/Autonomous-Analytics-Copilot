import pandas as pd


def descriptive_statistics(df, column: str):
    if column not in df.columns:
        return {"error": "Column not found"}

    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": "Column is not numeric"}

    return {
        "mean": float(df[column].mean()),
        "median": float(df[column].median()),
        "std": float(df[column].std()),
        "min": float(df[column].min()),
        "max": float(df[column].max())
    }