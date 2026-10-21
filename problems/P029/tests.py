import pandas as pd

from src.testing import case


def make_cases():
    # age の中央値は [20, 40, 30] の 30
    basic = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4"],
        "age": [20, None, 40, 30],
        "prefecture": ["Tokyo", None, "Osaka", "Aichi"],
    })
    # 中央値は [10, 20, 30, 40] の 25
    even = pd.DataFrame({"customer_id": ["C1", "C2", "C3", "C4", "C5"], "age": [10, 20, None, 30, 40]})
    clean = pd.DataFrame({"customer_id": ["C1", "C2"], "age": [25, 35]})
    return [
        case("基本ケース(他の列の欠損は残す)", {"df": basic},
             pd.DataFrame({"customer_id": ["C1", "C2", "C3", "C4"], "age": [20, 30, 40, 30], "prefecture": ["Tokyo", None, "Osaka", "Aichi"]})),
        case("中央値が2つの値の間", {"df": even},
             pd.DataFrame({"customer_id": ["C1", "C2", "C3", "C4", "C5"], "age": [10, 20, 25, 30, 40]})),
        case("欠損なし", {"df": clean}, pd.DataFrame({"customer_id": ["C1", "C2"], "age": [25, 35]})),
    ]
