import pandas as pd

from src.testing import case


def make_cases():
    clean = pd.DataFrame({"customer_id": ["C1", "C2"], "age": [30, 40]})
    pair = pd.DataFrame({"customer_id": ["C1", "C2", "C1"], "age": [30, 40, 30]})
    # C1 が3回(重複2) / C2 は age が違うので重複ではない
    triple = pd.DataFrame({"customer_id": ["C1", "C1", "C1", "C2", "C2"], "age": [30, 30, 30, 40, 41]})
    return [
        case("重複なし", {"df": clean}, 0),
        case("1組の重複", {"df": pair}, 1),
        case("3回出てくる行と、一部の列だけ同じ行", {"df": triple}, 2),
    ]
