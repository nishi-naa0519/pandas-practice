import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5],
        "category": ["book", "electronics", "food", "electronics", "toys"],
        "price": [1200, 3000, 800, 5000, 2999],
    })
    cheap = pd.DataFrame({"order_id": [1, 2], "category": ["food", "book"], "price": [300, 2990]})
    return [
        case("基本ケース(3000ちょうどを含む)", {"df": df}, df.loc[[1, 3]], ignore_index=True),
        case("該当なし", {"df": cheap}, cheap.loc[[]], ignore_index=True),
    ]
