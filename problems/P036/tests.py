import pandas as pd

from src.testing import case


def make_cases():
    customers = pd.DataFrame({"customer_id": ["C1", "C2"], "age": [30, None], "plan": ["free", "premium"]})
    orders = pd.DataFrame({"order_id": [1, 2, 3, 4, 5], "customer_id": ["C1", "C2", "C9", "C1", "C8"]})
    matched = pd.DataFrame({"order_id": [1, 2], "customer_id": ["C2", "C2"]})
    return [
        case("対応のない注文が2件(age の欠損は数えない)", {"orders": orders, "customers": customers}, 2),
        case("すべて対応あり", {"orders": matched, "customers": customers}, 0),
    ]
