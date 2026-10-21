import math

import pandas as pd

from src.testing import case

INDEX = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]


def make_cases():
    # 手計算: price=[100,200,300,400] -> std=sqrt(50000/3), 25%=175, 75%=325
    #         quantity=[1,1,2,4] -> mean=2, std=sqrt(2), 50%=1.5, 75%=2.5
    basic = pd.DataFrame({"price": [100, 200, 300, 400], "quantity": [1, 1, 2, 4], "category": ["a", "b", "a", "c"]})
    expected_basic = pd.DataFrame({
        "price": [4, 250, math.sqrt(50000 / 3), 100, 175, 250, 325, 400],
        "quantity": [4, 2, math.sqrt(2), 1, 1, 1.5, 2.5, 4],
    }, index=INDEX)
    # 欠損は除外: score=[10,30] -> std=sqrt(200), 25%=15, 75%=25
    missing = pd.DataFrame({"score": [10, None, 30]})
    expected_missing = pd.DataFrame({"score": [2, 20, math.sqrt(200), 10, 15, 20, 25, 30]}, index=INDEX)
    return [
        case("基本ケース(文字列列は除外)", {"df": basic}, expected_basic),
        case("欠損を含む列", {"df": missing}, expected_missing),
    ]
