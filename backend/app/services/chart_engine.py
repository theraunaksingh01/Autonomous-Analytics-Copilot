import pandas as pd


def build_chart(result, question: str):
    """
    Returns Plotly JSON-compatible chart object or None.
    """

    # If result is dict (like groupby output)
    if isinstance(result, dict):
        keys = list(result.keys())
        values = list(result.values())

        return {
            "data": [
                {
                    "type": "bar",
                    "x": keys,
                    "y": values
                }
            ],
            "layout": {
                "title": question,
                "template": "plotly_dark"
            }
        }

    # If result is list of records
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):

        df = pd.DataFrame(result)

        if df.shape[1] >= 2:
            return {
                "data": [
                    {
                        "type": "bar",
                        "x": df.iloc[:, 0].astype(str).tolist(),
                        "y": df.iloc[:, 1].tolist()
                    }
                ],
                "layout": {
                    "title": question,
                    "template": "plotly_dark"
                }
            }

    return None