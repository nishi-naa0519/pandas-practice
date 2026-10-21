import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "customer_id": ["C1", "C2", "C3"],
        "plan": ["free", "premium", "free"],
        "age": [25, None, 41],
        "prefecture": ["Tokyo", "Osaka", "Aichi"],
    })
    return [
        case("元と列の順番が違う", {"df": df},
             pd.DataFrame({"customer_id": ["C1", "C2", "C3"], "age": [25, None, 41], "plan": ["free", "premium", "free"]})),
        case("1行だけ", {"df": df.iloc[[0]]},
             pd.DataFrame({"customer_id": ["C1"], "age": [25.0], "plan": ["free"]})),
    ]
