import pandas as pd

from src.testing import case


def make_cases():
    # 除外しないと U1(bot 3件 + pc 1件)が1位になってしまう
    df = pd.DataFrame({
        "user_id": ["U1", "U1", "U1", "U1", "U2", "U2", "U2", "U3", "U3", "U4", "U4"],
        "device": ["bot", "bot", "bot", "pc", "pc", "mobile", "pc", "mobile", "mobile", "crawler", "crawler"],
    })
    few = pd.DataFrame({"user_id": ["U1", "U2", "U1"], "device": ["pc", "bot", "mobile"]})
    return [
        case("基本ケース", {"df": df}, pd.Series([3, 2, 1], index=["U2", "U3", "U1"])),
        case("ユーザーが3人未満", {"df": few}, pd.Series([2], index=["U1"])),
    ]
