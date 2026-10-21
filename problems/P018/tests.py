import pandas as pd

from src.testing import case


def make_cases():
    unique = pd.DataFrame({"customer_id": ["C1", "C2", "C3"], "age": [30, 30, 40]})
    dup_id = pd.DataFrame({"customer_id": ["C1", "C2", "C1"], "age": [30, 35, 41]})
    one = pd.DataFrame({"customer_id": ["C1"], "age": [30]})
    return [
        case("一意(他の列は重複していてもよい)", {"df": unique}, True),
        case("IDだけ重複している", {"df": dup_id}, False),
        case("1行だけ", {"df": one}, True),
    ]
