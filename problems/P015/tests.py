import pandas as pd

from src.testing import case


def make_cases():
    # a: 1/4, b: 3/4, c: 2/4, d: 0
    basic = pd.DataFrame({
        "a": [1, None, 3, 4],
        "b": [None, None, None, 4],
        "c": [None, 2, None, 4],
        "d": [1, 2, 3, 4],
    })
    # x: 1/5, y: 3/5, z: 2/5
    five = pd.DataFrame({
        "x": [1, 2, None, 4, 5],
        "y": [None, None, 3, None, 5],
        "z": ["p", None, "r", None, "t"],
    })
    clean = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    return [
        case("基本ケース", {"df": basic}, pd.Series([0.75, 0.5, 0.25, 0.0], index=["b", "c", "a", "d"])),
        case("行数5", {"df": five}, pd.Series([0.6, 0.4, 0.2], index=["y", "z", "x"])),
        case("欠損なし(順番は問わない)", {"df": clean}, pd.Series({"a": 0.0, "b": 0.0}), ignore_order=True),
    ]
