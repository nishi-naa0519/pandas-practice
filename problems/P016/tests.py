import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4", "C5"],
        "age": [30, None, 45, None, 50],
        "prefecture": ["Tokyo", "Osaka", None, None, "Aichi"],
    })
    clean = pd.DataFrame({"customer_id": ["C1"], "age": [30], "prefecture": ["Tokyo"]})
    return [
        case("基本ケース(両方欠損の行を含む)", {"df": df}, df.loc[[1, 2, 3]], ignore_index=True),
        case("欠損なし", {"df": clean}, clean.loc[[]], ignore_index=True),
    ]
