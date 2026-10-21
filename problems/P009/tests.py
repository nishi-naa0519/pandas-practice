import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6],
        "category": ["book", "book", "food", "book", "toys", "book"],
        "quantity": [1, 2, 3, 4, 2, 2],
    })
    no_book = pd.DataFrame({"order_id": [1, 2], "category": ["food", "toys"], "quantity": [3, 5]})
    return [
        case("基本ケース", {"df": df}, df.loc[[1, 3, 5]], ignore_index=True),
        case("片方の条件しか満たさない行だけ", {"df": no_book}, no_book.loc[[]], ignore_index=True),
    ]
