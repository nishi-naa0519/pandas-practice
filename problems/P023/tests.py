import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "category": ["book", "food", "book", "toys", "toys", "toys"],
        "price": [1000, 500, 2000, 3000, 1000, 2000],
    })
    missing = pd.DataFrame({"category": ["book", "book", "food"], "price": [100, None, 300]})
    return [
        case("基本ケース", {"df": df}, pd.Series({"book": 1500.0, "food": 500.0, "toys": 2000.0}), ignore_order=True),
        case("欠損は除いて平均", {"df": missing}, pd.Series({"book": 100.0, "food": 300.0}), ignore_order=True),
    ]
