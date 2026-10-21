import pandas as pd

from src.testing import case


def make_cases():
    basic = pd.DataFrame({
        "id": range(60),                               # 60種類
        "plan": ["a", "b", "c"] * 20,                  # 3種類
        "zip_code": [f"Z{i % 55}" for i in range(60)],  # 55種類
        "country": ["JP"] * 60,                        # 1種類
    })
    boundary = pd.DataFrame({
        "id": range(50),                               # ちょうど50 -> 含む
        "shop": [f"S{i % 49}" for i in range(50)],     # 49 -> 含まない
    })
    small = pd.DataFrame({"id": range(10), "plan": ["a", "b"] * 5})
    return [
        case("基本ケース", {"df": basic}, ["id", "zip_code"], as_set=True),
        case("ちょうど50", {"df": boundary}, ["id"], as_set=True),
        case("該当なし", {"df": small}, [], as_set=True),
    ]
