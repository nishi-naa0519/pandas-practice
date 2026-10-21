import pandas as pd

from src.testing import case


def make_cases():
    basic = pd.DataFrame({"os": ["iOS", "ios", "Android", "IOS", "android"]})
    missing = pd.DataFrame({"os": ["iOS", None, "Android", "android", "ANDROID"]})
    clean = pd.DataFrame({"os": ["ios", "ios"]})
    return [
        case("基本ケース", {"df": basic}, pd.Series([3, 2], index=["ios", "android"])),
        case("欠損を含む", {"df": missing}, pd.Series([3, 1], index=["android", "ios"])),
        case("表記ゆれなし", {"df": clean}, pd.Series([2], index=["ios"])),
    ]
