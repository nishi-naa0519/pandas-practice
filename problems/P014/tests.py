import pandas as pd

from src.testing import case


def make_cases():
    basic = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4"],
        "age": [30, None, 45, None],
        "prefecture": ["Tokyo", None, "Osaka", "Aichi"],
    })
    clean = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    all_missing = pd.DataFrame({"a": [1, 2, 3], "b": [None, None, None]})
    return [
        case("基本ケース", {"df": basic}, pd.Series({"customer_id": 0, "age": 2, "prefecture": 1})),
        case("欠損なし", {"df": clean}, pd.Series({"a": 0, "b": 0})),
        case("全部欠損の列", {"df": all_missing}, pd.Series({"a": 0, "b": 3})),
    ]
