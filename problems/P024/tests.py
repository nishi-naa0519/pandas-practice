import pandas as pd

from src.testing import case


def make_cases():
    # JP: (4+6)/2=5, US: (10+6)/2=8, KR: (1+2+3)/3=2
    df = pd.DataFrame({
        "country": ["JP", "US", "JP", "KR", "US", "KR", "KR"],
        "sessions_7d": [4, 10, 6, 1, 6, 2, 3],
    })
    two = pd.DataFrame({"country": ["JP", "TW", "JP"], "sessions_7d": [3, 9, 5]})
    return [
        case("基本ケース", {"df": df}, pd.Series([8.0, 5.0, 2.0], index=["US", "JP", "KR"])),
        case("2グループ", {"df": two}, pd.Series([9.0, 4.0], index=["TW", "JP"])),
    ]
