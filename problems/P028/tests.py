import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({"order_id": [1, 2, 3], "price": [1000, 500, 2000], "quantity": [2, 1, 3]})
    missing = pd.DataFrame({"order_id": [1, 2], "price": [1000, None], "quantity": [1, 2]})
    return [
        case("基本ケース", {"df": df},
             pd.DataFrame({"order_id": [1, 2, 3], "price": [1000, 500, 2000], "quantity": [2, 1, 3], "amount": [2000, 500, 6000]})),
        case("欠損を含む", {"df": missing},
             pd.DataFrame({"order_id": [1, 2], "price": [1000, None], "quantity": [1, 2], "amount": [1000, None]})),
    ]
