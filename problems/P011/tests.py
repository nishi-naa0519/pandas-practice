import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4", "C5", "C6"],
        "prefecture": ["Tokyo", "Osaka", "Aichi", "Tokyo", None, "Fukuoka"],
    })
    other = pd.DataFrame({"customer_id": ["C1", "C2"], "prefecture": ["Aichi", "Hokkaido"]})
    return [
        case("基本ケース(欠損は含まない)", {"df": df}, df.loc[[0, 1, 3]], ignore_index=True),
        case("該当なし", {"df": other}, other.loc[[]], ignore_index=True),
    ]
