import pandas as pd

from src.testing import case


def make_cases():
    return [
        case("並び順がばらばら", {"df": pd.DataFrame({"timestamp": ["2025-03-05 12:00:00", "2025-03-01 08:00:00", "2025-03-10 08:00:00"]})}, 9),
        case("1日に満たない端数は切り捨て", {"df": pd.DataFrame({"timestamp": ["2025-03-01 10:00:00", "2025-03-31 09:00:00"]})}, 29),
        case("年をまたぐ", {"df": pd.DataFrame({"timestamp": ["2025-01-02 00:00:00", "2024-12-30 00:00:00"]})}, 3),
    ]
