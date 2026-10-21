import pandas as pd

from src.testing import case


def make_cases():
    # 有料: [10, 4, 7] -> 中央値 7, 最大 10
    odd = pd.DataFrame({"is_paid": [1, 0, 1, 1, 0], "sessions_7d": [10, 50, 4, 7, 2]})
    # 有料: [10, 4, 7, 9] -> 中央値 (7+9)/2 = 8.0
    even = pd.DataFrame({"is_paid": [1, 1, 0, 1, 1], "sessions_7d": [10, 4, 99, 7, 9]})
    one = pd.DataFrame({"is_paid": [0, 1, 0], "sessions_7d": [3, 6, 100]})
    return [
        case("基本ケース(無料ユーザーの大きい値は無視)", {"df": odd}, (7, 10)),
        case("有料ユーザーが偶数人", {"df": even}, (8.0, 10)),
        case("有料ユーザーが1人", {"df": one}, (6, 6)),
    ]
