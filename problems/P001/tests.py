import io

import pandas as pd

from src.testing import case


def make_cases():
    csv_basic = "order_id,category,price\n1,book,1200\n2,food,800\n3,toys,3000\n4,book,1500\n5,food,500\n"
    csv_short = "order_id,price\n1,100\n2,200\n"
    csv_missing = "user_id,score\n1,\n2,80\n3,90\n4,70\n"
    return [
        case("基本ケース", {"path": io.StringIO(csv_basic)},
             pd.DataFrame({"order_id": [1, 2, 3], "category": ["book", "food", "toys"], "price": [1200, 800, 3000]})),
        case("3行未満のファイル", {"path": io.StringIO(csv_short)},
             pd.DataFrame({"order_id": [1, 2], "price": [100, 200]})),
        case("欠損を含むファイル", {"path": io.StringIO(csv_missing)},
             pd.DataFrame({"user_id": [1, 2, 3], "score": [float("nan"), 80.0, 90.0]})),
    ]
