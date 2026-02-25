import pandas as pd

def execute_code(df, code):
    local_vars = {"df": df}

    try:
        exec(code, {}, local_vars)
        result = local_vars.get("result", None)

        # Convert pandas objects to safe types
        if isinstance(result, pd.Series):
            return result.to_dict()

        if isinstance(result, pd.DataFrame):
            return result.head(50).to_dict(orient="records")

        return result

    except KeyError as e:
        return f"Column not found: {str(e)}. Available columns: {list(df.columns)}"

    except Exception as e:
        return f"Execution error: {str(e)}"