import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "id": [1, 2, 2, 3, 4],
        "age": [30, 40, 40, 50, None],
        "churn": [0, 1, 1, None, 0],
    })
    clean = pd.DataFrame({"id": [1, 2], "age": [30, None], "churn": [0, 1]})
    return [
        case("基本ケース(age の欠損は残す)", {"df": df}, df.loc[[0, 1, 4]], ignore_index=True),
        case("削除するものがない", {"df": clean}, clean.copy(), ignore_index=True),
    ]
