"""問題用の合成データセットを生成する。

乱数シードを固定しているので、何度実行しても同じCSVになる。
各問題が使うデータは problems/Pxxx/content.yaml の `data:` に書き、
tools/build_problems.py が problems/Pxxx/data/ にコピーする。

EDA練習のため、意図的に以下のような「品質上の問題」を混ぜている。
    customers     : age の欠損、prefecture の欠損、完全重複行
    app_users     : os の表記ゆれ、極端な sessions_7d、負の avg_session_min
    web_logs      : bot / crawler のアクセス
    churn_train   : 欠損の多い列、定数列、"unknown" が混ざった数値列、重複行、目的変数の欠損
    churn_test    : train に存在しない region
    store_sales   : 特定店舗・期間に偏った revenue 欠損、途中開店の店舗
    ad_logs       : clicks > impressions、負の cost、重複行、campaign の表記ゆれ
    members_raw   : 上記をまとめた「汚い」顧客マスタ
"""

import numpy as np
import pandas as pd

PREFS = ["Tokyo", "Osaka", "Kanagawa", "Aichi", "Fukuoka", "Hokkaido"]


def _dates(rng, start, end, n):
    days = (pd.Timestamp(end) - pd.Timestamp(start)).days
    return pd.Timestamp(start) + pd.to_timedelta(rng.integers(0, days + 1, n), unit="D")


def customers():
    rng = np.random.default_rng(1)
    n = 120
    df = pd.DataFrame({
        "customer_id": [f"C{i:03d}" for i in range(1, n + 1)],
        "age": rng.integers(18, 71, n).astype(float),
        "prefecture": rng.choice(PREFS, n, p=[0.32, 0.2, 0.16, 0.12, 0.12, 0.08]),
        "plan": rng.choice(["free", "standard", "premium"], n, p=[0.58, 0.27, 0.15]),
        "n_orders": rng.poisson(5, n),
        "signup_date": _dates(rng, "2023-01-01", "2025-03-31", n).strftime("%Y-%m-%d"),
    })
    df["total_spent"] = (df["n_orders"] * rng.integers(1500, 6000, n)).round(-1)
    df.loc[rng.choice(n, 13, replace=False), "age"] = np.nan
    df = df.astype({"prefecture": object})
    df.loc[rng.choice(n, 4, replace=False), "prefecture"] = np.nan
    df.loc[df.sample(8, random_state=3).index, "n_orders"] += 10
    dup = df.iloc[[17, 54, 88]]
    return pd.concat([df, dup], ignore_index=True)


def orders():
    rng = np.random.default_rng(2)
    n = 300
    cats = ["book", "fashion", "electronics", "food", "toys"]
    category = rng.choice(cats, n, p=[0.3, 0.25, 0.15, 0.2, 0.1])
    lo = {"book": 600, "fashion": 1500, "electronics": 3000, "food": 300, "toys": 1000}
    hi = {"book": 3500, "fashion": 12000, "electronics": 60000, "food": 4000, "toys": 9000}
    price = [int(round(rng.integers(lo[c], hi[c]), -1)) for c in category]
    # C121〜C125 は customers に存在しない顧客(left join の練習用)
    cust = [f"C{i:03d}" for i in rng.integers(1, 126, n)]
    df = pd.DataFrame({
        "order_id": range(1, n + 1),
        "customer_id": cust,
        "order_date": np.sort(_dates(rng, "2025-01-05", "2025-06-30", n)).astype("datetime64[ns]"),
        "category": category,
        "price": price,
        "quantity": rng.choice([1, 2, 3, 4], n, p=[0.6, 0.25, 0.1, 0.05]),
        "payment_method": rng.choice(
            ["credit_card", "e_money", "bank_transfer", "convenience_store"], n, p=[0.46, 0.26, 0.17, 0.11]
        ),
        "coupon_used": rng.choice([0, 1], n, p=[0.75, 0.25]),
    })
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")
    return df


def app_users():
    rng = np.random.default_rng(3)
    n = 250
    is_paid = rng.choice([0, 1], n, p=[0.8, 0.2])
    os_ = rng.choice(["iOS", "Android"], n, p=[0.55, 0.45]).astype(object)
    idx = rng.choice(n, 30, replace=False)
    os_[idx[:12]] = "ios"
    os_[idx[12:17]] = "IOS"
    os_[idx[17:]] = "android"
    sessions = rng.poisson(6, n) + is_paid * rng.poisson(5, n)
    df = pd.DataFrame({
        "user_id": [f"U{i:04d}" for i in range(1, n + 1)],
        "os": os_,
        "app_version": rng.choice(["3.1.0", "3.2.0", "3.2.1", "4.0.0"], n, p=[0.1, 0.25, 0.35, 0.3]),
        "country": rng.choice(["JP", "US", "KR", "TW", "TH"], n, p=[0.5, 0.2, 0.13, 0.1, 0.07]),
        "sessions_7d": sessions,
        "avg_session_min": rng.gamma(2.0, 3.0, n).round(1),
        "is_paid": is_paid,
        "signup_date": np.sort(_dates(rng, "2024-04-01", "2025-03-31", n)).astype("datetime64[ns]"),
    })
    df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.strftime("%Y-%m-%d")
    df.loc[rng.choice(n, 20, replace=False), "avg_session_min"] = np.nan
    df.loc[[41, 177], "sessions_7d"] = [999, 812]  # ログ集計バグを想定した極端な値
    df.loc[96, "avg_session_min"] = -3.0
    return df


def web_logs():
    rng = np.random.default_rng(4)
    n = 500
    device = rng.choice(["mobile", "pc", "tablet", "bot", "crawler"], n, p=[0.5, 0.33, 0.07, 0.06, 0.04])
    page = rng.choice(["/", "/search", "/product", "/cart", "/checkout"], n, p=[0.22, 0.2, 0.38, 0.12, 0.08])
    page = np.array([f"/product/{rng.integers(100, 140)}" if p == "/product" else p for p in page])
    cvr = {"mobile": 0.025, "pc": 0.08, "tablet": 0.04, "bot": 0.0, "crawler": 0.0}
    page_boost = np.where(np.isin(page, ["/cart", "/checkout"]), 3.0, 1.0)
    converted = (rng.random(n) < np.array([cvr[d] for d in device]) * page_boost).astype(int)
    duration = np.where(np.isin(device, ["bot", "crawler"]), rng.integers(0, 3, n), rng.gamma(2.0, 40.0, n).astype(int))
    start = pd.Timestamp("2025-03-01")
    ts = np.sort(start + pd.to_timedelta(rng.integers(0, 31 * 24 * 3600, n), unit="s"))
    return pd.DataFrame({
        "session_id": [f"S{i:05d}" for i in range(1, n + 1)],
        "user_id": [f"U{i:04d}" for i in rng.integers(1, 180, n)],
        "timestamp": pd.to_datetime(ts).strftime("%Y-%m-%d %H:%M:%S"),
        "page": page,
        "device": device,
        "duration_sec": duration,
        "converted": converted,
    })


def _churn_features(rng, n, start_id, regions, region_p):
    plan = rng.choice(["basic", "standard", "premium"], n, p=[0.5, 0.35, 0.15])
    fee = pd.Series(plan).map({"basic": 990, "standard": 1490, "premium": 1990}).to_numpy()
    tenure = rng.integers(1, 73, n)
    calls = rng.poisson(1.5, n)
    age = rng.integers(18, 75, n)
    income = (rng.lognormal(6.0, 0.4, n)).round(-1).astype(int).astype(object)
    income[rng.choice(n, int(n * 0.04), replace=False)] = "unknown"
    pref_code = rng.integers(1, 48, n)
    postal = [f"{p:02d}{rng.integers(0, 100000):05d}" for p in pref_code]
    df = pd.DataFrame({
        "id": range(start_id, start_id + n),
        "age": age,
        "gender": rng.choice(["F", "M"], n),
        "region": rng.choice(regions, n, p=region_p),
        "postal_code": postal,
        "plan": plan,
        "monthly_fee": fee,
        "tenure_months": tenure,
        "n_support_calls": calls,
        "avg_watch_hours": rng.gamma(2.0, 4.0, n).round(1),
        "last_login_days": rng.integers(0, 60, n).astype(float),
        "income": income,
        "coupon_code": np.where(rng.random(n) < 0.12, rng.choice(["SPRING10", "WELCOME", "FRIEND"], n), None),
        "country": "JP",
    })
    df.loc[rng.choice(n, int(n * 0.25), replace=False), "avg_watch_hours"] = np.nan
    return df, plan, tenure, calls


REGIONS = ["Kanto", "Kansai", "Chubu", "Kyushu", "Tohoku", "Hokkaido", "Chugoku", "Shikoku"]
REGION_P = [0.36, 0.2, 0.14, 0.1, 0.08, 0.05, 0.04, 0.03]


def churn_train():
    rng = np.random.default_rng(5)
    n = 600
    df, plan, tenure, calls = _churn_features(rng, n, 1, REGIONS, REGION_P)
    logit = -1.2 - 0.04 * tenure + 0.45 * calls + np.where(plan == "basic", 0.5, np.where(plan == "premium", -0.6, 0))
    df["churn"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(float)
    df.loc[rng.choice(n, 30, replace=False), "last_login_days"] = np.nan
    df.loc[rng.choice(n, 5, replace=False), "churn"] = np.nan
    dup = df.iloc[[10, 200, 201, 455]]
    return pd.concat([df, dup], ignore_index=True)


def churn_test():
    rng = np.random.default_rng(6)
    regions = REGIONS + ["Okinawa"]
    df, *_ = _churn_features(rng, 250, 601, regions, [0.33, 0.2, 0.14, 0.1, 0.08, 0.05, 0.04, 0.03, 0.03])
    df["last_login_days"] = df["last_login_days"].astype(int)
    return df


def store_sales():
    rng = np.random.default_rng(7)
    stores = {"S01": "east", "S02": "east", "S03": "west", "S04": "west", "S05": "north"}
    prices = {"coffee": 450, "tea": 380, "juice": 300}
    rows = []
    for date in pd.date_range("2025-04-01", "2025-06-30"):
        for store, region in stores.items():
            if store == "S05" and date < pd.Timestamp("2025-05-15"):
                continue  # S05 は途中で開店
            for product, price in prices.items():
                base = {"coffee": 60, "tea": 35, "juice": 25}[product] * (1.3 if date.dayofweek >= 5 else 1.0)
                units = int(rng.poisson(base * (0.8 if region == "north" else 1.0)))
                rows.append([date.strftime("%Y-%m-%d"), store, region, product, units, units * price])
    df = pd.DataFrame(rows, columns=["date", "store_id", "region", "product", "units", "revenue"])
    df["revenue"] = df["revenue"].astype(float)
    # S04 の POS 障害で 5月後半の revenue が欠損
    broken = (df["store_id"] == "S04") & df["date"].between("2025-05-20", "2025-05-31")
    df.loc[broken, "revenue"] = np.nan
    df.loc[df.sample(6, random_state=1).index, "revenue"] = np.nan
    return df


def ad_logs():
    rng = np.random.default_rng(8)
    ads = {10001: "spring_sale", 10002: "spring_sale", 10003: "spring_sale", 10004: "brand",
           10005: "brand", 10006: "retarget", 10007: "retarget", 10008: "retarget"}
    rows = []
    for date in pd.date_range("2025-05-01", "2025-05-31"):
        for ad_id, campaign in ads.items():
            imp = int(rng.integers(800, 6000))
            ctr = {"spring_sale": 0.02, "brand": 0.008, "retarget": 0.035}[campaign]
            clicks = int(rng.binomial(imp, ctr))
            conv = int(rng.binomial(clicks, 0.05 if campaign != "retarget" else 0.09))
            rows.append([date.strftime("%Y-%m-%d"), ad_id, campaign, imp, clicks, round(clicks * rng.uniform(40, 90)), conv])
    df = pd.DataFrame(rows, columns=["date", "ad_id", "campaign", "impressions", "clicks", "cost", "conversions"])
    df.loc[[37, 150], "clicks"] = df.loc[[37, 150], "impressions"] + [12, 230]
    df.loc[201, "cost"] = -4200
    df.loc[df["ad_id"].isin([10004, 10005]) & df["date"].between("2025-05-10", "2025-05-11"), "campaign"] = "Brand"
    df.loc[[118], "impressions"] = 0
    df.loc[[118], ["clicks", "cost", "conversions"]] = 0
    dup = df.iloc[[5, 6, 99]]
    return pd.concat([df, dup], ignore_index=True)


def members_raw():
    rng = np.random.default_rng(9)
    n = 200
    df = pd.DataFrame({
        "member_id": [f"M{i:04d}" for i in range(1, n + 1)],
        "age": rng.integers(18, 70, n).astype(object),
        "gender": rng.choice(["F", "M"], n).astype(object),
        "prefecture": rng.choice(PREFS, n).astype(object),
        "signup_date": pd.Series(_dates(rng, "2022-01-01", "2025-03-31", n)).dt.strftime("%Y-%m-%d"),
        "plan": rng.choice(["free", "standard", "premium"], n, p=[0.6, 0.28, 0.12]),
        "monthly_spend": rng.integers(0, 20000, n).round(-1),
    })
    df.loc[rng.choice(n, 18, replace=False), "age"] = np.nan
    df.loc[[12, 140], "age"] = 999
    df.loc[77, "age"] = -1
    df.loc[[5, 33, 91, 150, 160], "gender"] = ["male", "female", "female", "male", "女性"]
    df.loc[[8, 44, 120], "prefecture"] = ["tokyo", "TOKYO", "Tokyo "]
    df.loc[rng.choice(n, 9, replace=False), "prefecture"] = np.nan
    df["monthly_spend"] = [f"{v:,}" for v in df["monthly_spend"]]  # "1,200" のような文字列
    df.loc[60, "signup_date"] = "2026-12-01"  # 未来の日付
    # 同じ member_id で内容が違う行(更新履歴の混入)と、完全重複行
    changed = df.iloc[[20, 21]].copy()
    changed["plan"] = "premium"
    return pd.concat([df, changed, df.iloc[[100, 101, 102]]], ignore_index=True)


DATASETS = {
    "customers.csv": customers,
    "orders.csv": orders,
    "app_users.csv": app_users,
    "web_logs.csv": web_logs,
    "churn_train.csv": churn_train,
    "churn_test.csv": churn_test,
    "store_sales.csv": store_sales,
    "ad_logs.csv": ad_logs,
    "members_raw.csv": members_raw,
}


def write(name, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    DATASETS[name]().to_csv(dest_dir / name, index=False)
