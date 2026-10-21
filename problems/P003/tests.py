import pandas as pd

from src.testing import case


def make_cases():
    return [
        case("基本ケース",
             {"df": pd.DataFrame({"customer_id": ["C1", "C2"], "age": [30, 40], "plan": ["free", "premium"]})},
             ["customer_id", "age", "plan"]),
        case("1列だけ", {"df": pd.DataFrame({"user_id": ["U1", "U2"]})}, ["user_id"]),
        case("空白を含む列名", {"df": pd.DataFrame({"user id": [1], "Signup Date": ["2025-01-01"]})},
             ["user id", "Signup Date"]),
    ]
