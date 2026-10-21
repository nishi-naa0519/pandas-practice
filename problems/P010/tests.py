import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3", "C4", "C5"],
        "plan": ["free", "premium", "standard", "premium", "free"],
        "n_orders": [12, 3, 9, 15, 10],
    })
    none = pd.DataFrame({"customer_id": ["C1", "C2"], "plan": ["free", "standard"], "n_orders": [1, 9]})
    return [
        case("基本ケース(両方満たす行・10ちょうどを含む)", {"df": df}, df.loc[[0, 1, 3, 4]], ignore_index=True),
        case("該当なし", {"df": none}, none.loc[[]], ignore_index=True),
    ]
