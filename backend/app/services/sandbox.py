import pandas as pd


def execute_code(df, code: str):
    local_vars = {"df": df}

    exec(code, {}, local_vars)

    result = local_vars.get("result", None)

    # Convert Pandas objects safely
    if isinstance(result, pd.DataFrame):
        return result.to_dict(orient="records")

    if isinstance(result, pd.Series):
        return result.to_dict()

    return result