import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({"order_id": [1, 2, 3], "order_date": ["2024-12-31", "2025-01-05", "2025-06-30"]})
    same = pd.DataFrame({"order_id": [1, 2], "order_date": ["2025-03-01", "2025-03-31"]})
    return [
        case("年をまたぐ", {"df": df},
             pd.DataFrame({
                 "order_id": [1, 2, 3],
                 "order_date": [pd.Timestamp("2024-12-31"), pd.Timestamp("2025-01-05"), pd.Timestamp("2025-06-30")],
                 "year": [2024, 2025, 2025],
                 "month": [12, 1, 6],
             })),
        case("同じ月", {"df": same},
             pd.DataFrame({
                 "order_id": [1, 2],
                 "order_date": [pd.Timestamp("2025-03-01"), pd.Timestamp("2025-03-31")],
                 "year": [2025, 2025],
                 "month": [3, 3],
             })),
    ]
