import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "date": ["04-01", "04-01", "04-01", "04-02", "04-02", "04-03"],
        "region": ["east", "east", "east", "west", "west", "west"],
        "product": ["coffee", "coffee", "tea", "coffee", "tea", "tea"],
        "units": [10, 5, 3, 7, 2, 4],
    })
    one = pd.DataFrame({"region": ["east", "east"], "product": ["tea", "tea"], "units": [1, 2]})
    return [
        case("基本ケース", {"df": df},
             pd.DataFrame({"region": ["east", "east", "west", "west"], "product": ["coffee", "tea", "coffee", "tea"], "units": [15, 3, 7, 6]}),
             ignore_order=True, ignore_index=True),
        case("組み合わせが1つ", {"df": one}, pd.DataFrame({"region": ["east"], "product": ["tea"], "units": [3]}),
             ignore_index=True),
    ]
