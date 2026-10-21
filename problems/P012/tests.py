import pandas as pd

from src.testing import case

COLS = ["session_id", "page", "duration_sec"]


def make_cases():
    df = pd.DataFrame({
        "session_id": ["S1", "S2", "S3", "S4"],
        "page": ["/", "/cart", "/product/101", "/checkout"],
        "device": ["pc", "mobile", "pc", "pc"],
        "duration_sec": [30, 120, 45, 300],
        "converted": [0, 1, 0, 1],
    })
    no_cv = df.assign(converted=0)
    return [
        case("基本ケース", {"df": df}, df.loc[[1, 3], COLS], ignore_index=True),
        case("購入なし", {"df": no_cv}, df.loc[[], COLS], ignore_index=True),
    ]
