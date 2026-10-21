import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "store_id": ["S1", "S2", "S3", "S1", "S2", "S3", "S1"],
        "revenue": [5000, 12000, 8000, 3000, 15000, 7000, 9000],
    })
    short = pd.DataFrame({"store_id": ["S1", "S2", "S3"], "revenue": [100, 300, 200]})
    missing = pd.DataFrame({"store_id": ["S1", "S2", "S3", "S4", "S5", "S6"], "revenue": [500, None, 900, 100, 300, 700]})
    return [
        case("基本ケース", {"df": df}, df.loc[[4, 1, 6, 2, 5]], ignore_index=True),
        case("5行未満", {"df": short}, short.loc[[1, 2, 0]], ignore_index=True),
        case("欠損は上位に来ない", {"df": missing}, missing.loc[[2, 5, 0, 4, 3]], ignore_index=True),
    ]
