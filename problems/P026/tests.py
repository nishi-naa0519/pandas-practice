import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "plan": ["basic", "basic", "basic", "basic", "premium", "premium", "standard"],
        "churn": [1, 0, 1, 0, 0, 0, 1],
    })
    missing = pd.DataFrame({"plan": ["basic", "basic", "basic", "premium"], "churn": [1, None, 0, 1]})
    return [
        case("基本ケース", {"df": df},
             pd.DataFrame({"mean": [0.5, 0.0, 1.0], "count": [4, 2, 1]}, index=["basic", "premium", "standard"]),
             ignore_order=True),
        case("目的変数に欠損", {"df": missing},
             pd.DataFrame({"mean": [0.5, 1.0], "count": [2, 1]}, index=["basic", "premium"]),
             ignore_order=True),
    ]
