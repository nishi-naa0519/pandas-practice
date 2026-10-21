import pandas as pd

from src.testing import case


def make_cases():
    df = pd.DataFrame({
        "page": ["/", "/product/101", "/product/102", "/cart", "/product/101", "/productivity", "/search"],
        "device": ["pc", "mobile", "pc", "pc", "mobile", "pc", "mobile"],
    })
    none = pd.DataFrame({"page": ["/", "/cart"], "device": ["pc", "mobile"]})
    return [
        case("基本ケース(/productivity は含まない)", {"df": df}, pd.Series([2, 1], index=["mobile", "pc"])),
        case("該当なし", {"df": none}, pd.Series([], dtype="int64")),
    ]
