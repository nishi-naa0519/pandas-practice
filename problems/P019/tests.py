import pandas as pd

from src.testing import case


def make_cases():
    basic = pd.DataFrame({"payment_method": ["credit_card", "e_money", "credit_card", "bank_transfer", "credit_card", "e_money"]})
    missing = pd.DataFrame({"payment_method": ["e_money", None, "e_money", "credit_card", None]})
    single = pd.DataFrame({"payment_method": ["credit_card", "credit_card"]})
    return [
        case("基本ケース", {"df": basic}, pd.Series([3, 2, 1], index=["credit_card", "e_money", "bank_transfer"])),
        case("欠損は数えない", {"df": missing}, pd.Series([2, 1], index=["e_money", "credit_card"])),
        case("1種類だけ", {"df": single}, pd.Series([2], index=["credit_card"])),
    ]
