import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5, 6],
        "b": [10, 20, 30, 40, 50, 60],
        "c": ["p", "q", "r", "s", "t", "u"],
        "d": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    })
    small = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9], "w": [0, 0, 0]})
    return [
        case("基本ケース", {"df": df},
             pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [10, 20, 30, 40, 50], "c": ["p", "q", "r", "s", "t"]})),
        case("5行未満", {"df": small}, pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]})),
    ]
