import pandas as pd

from src.testing import case


def make_cases():
    orders = pd.DataFrame({"order_id": [1, 2, 3, 4], "customer_id": ["C1", "C2", "C1", "C9"], "price": [100, 200, 300, 400]})
    customers = pd.DataFrame({"customer_id": ["C1", "C2", "C3"], "plan": ["free", "premium", "free"]})
    all_match = pd.DataFrame({"order_id": [1], "customer_id": ["C3"], "price": [500]})
    return [
        case("対応のない注文(C9)と顧客(C3)は消える", {"orders": orders, "customers": customers},
             pd.DataFrame({
                 "order_id": [1, 2, 3],
                 "customer_id": ["C1", "C2", "C1"],
                 "price": [100, 200, 300],
                 "plan": ["free", "premium", "free"],
             }),
             ignore_order=True, ignore_index=True),
        case("1件だけ", {"orders": all_match, "customers": customers},
             pd.DataFrame({"order_id": [1], "customer_id": ["C3"], "price": [500], "plan": ["free"]}),
             ignore_index=True),
    ]
