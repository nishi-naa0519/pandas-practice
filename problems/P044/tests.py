import pandas as pd

from src.testing import case


def make_cases():
    basic = pd.DataFrame({
        "a": [1, 2, 3, 4],
        "b": [None, None, None, 1],        # 欠損 75% -> 除外
        "c": ["JP", "JP", "JP", "JP"],     # 1種類 -> 除外
        "d": [None, None, 1, 2],           # 欠損ちょうど 50% -> 残す
    })
    tricky = pd.DataFrame({
        "e": [None, None, None, None],     # 全部欠損 -> 除外
        "f": ["x", None, "x", "x"],        # 欠損を除くと1種類 -> 除外
        "g": [1, 2, 1, 2],
    })
    ok = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    return [
        case("基本ケース(50%ちょうどは残す)", {"df": basic}, ["b", "c"], as_set=True),
        case("全部欠損・欠損を含む定数列", {"df": tricky}, ["e", "f"], as_set=True),
        case("該当なし", {"df": ok}, [], as_set=True),
    ]
