import pandas as pd

from src.testing import case


def make_cases():
    return [
        case("基本ケース", {"df": pd.DataFrame({"churn": [0, 0, 1, 0, 0, 0, 1, 0]})},
             pd.Series([0.75, 0.25], index=[0, 1])),
        case("強い不均衡", {"df": pd.DataFrame({"churn": [0] * 9 + [1]})},
             pd.Series([0.9, 0.1], index=[0, 1])),
        case("1クラスだけ", {"df": pd.DataFrame({"churn": [0, 0, 0]})}, pd.Series([1.0], index=[0])),
    ]
