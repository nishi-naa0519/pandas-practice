import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({"ad_id": [10001, 10002, 10001], "clicks": [5, 7, 3]})
    one = pd.DataFrame({"date": ["2025-05-01"], "ad_id": [10008]})
    return [
        case("基本ケース", {"df": df}, pd.DataFrame({"ad_id": ["10001", "10002", "10001"], "clicks": [5, 7, 3]})),
        case("1行だけ", {"df": one}, pd.DataFrame({"date": ["2025-05-01"], "ad_id": ["10008"]})),
    ]
