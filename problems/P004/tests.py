import io

import pandas as pd

from src.testing import case


def normalize(result):
    # 型オブジェクトを "int64" のような文字列にそろえて比較する
    return result.astype(str) if isinstance(result, pd.Series) else result


def read(text):
    return pd.read_csv(io.StringIO(text))


def make_cases():
    return [
        case("欠損を含む数値列", {"df": read("order_id,price,category\n1,1200,book\n2,,food\n3,800,toys\n")},
             pd.Series({"order_id": "int64", "price": "float64", "category": "str"})),
        case("数字だけの文字列", {"df": read("user_id,zip_code\nU1,0600001\nU2,1500001\n")},
             pd.Series({"user_id": "str", "zip_code": "int64"})),
        case("日付と真偽値", {"df": read("signup_date,is_paid\n2025-01-01,True\n2025-01-02,False\n")},
             pd.Series({"signup_date": "str", "is_paid": "bool"})),
    ]
