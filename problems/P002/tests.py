import pandas as pd

from src.testing import case


def make_cases():
    return [
        case("基本ケース",
             {"df": pd.DataFrame({"a": [1, 2, 3, 4], "b": [5, 6, 7, 8], "c": ["x", "y", "z", "w"]})},
             (4, 3)),
        case("1行だけ", {"df": pd.DataFrame({"user_id": ["U1"], "age": [30]})}, (1, 2)),
        case("行が0件(列だけある)", {"df": pd.DataFrame(columns=["a", "b", "c"])}, (0, 3)),
    ]
