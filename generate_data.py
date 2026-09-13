"""
Sinh du lieu mo phong cho mot doanh nghiep ban le / thuong mai dien tu
("VinaMart Online") de luyen tap thong ke voi Python (pandas/numpy/scipy).

Chay: python3 generate_data.py
Ket qua: orders.csv, daily_marketing.csv trong thu muc hien tai.
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# Cau hinh chung
# ---------------------------------------------------------------------------
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")
N_ORDERS = 6000

REGIONS = ["Hà Nội", "TP.HCM", "Đà Nẵng", "Hải Phòng", "Cần Thơ"]
REGION_WEIGHTS = [0.30, 0.35, 0.13, 0.12, 0.10]

CHANNELS = ["Organic", "Facebook Ads", "Google Ads", "Referral", "Email"]
CHANNEL_WEIGHTS = [0.28, 0.30, 0.22, 0.12, 0.08]

CATEGORIES = {
    "Điện tử":     {"weight": 0.20, "price": (300_000, 1.10), "cost_ratio": 0.72},
    "Thời trang":  {"weight": 0.28, "price": (150_000, 0.85), "cost_ratio": 0.55},
    "Gia dụng":    {"weight": 0.18, "price": (250_000, 0.90), "cost_ratio": 0.60},
    "Mỹ phẩm":     {"weight": 0.17, "price": (200_000, 0.80), "cost_ratio": 0.45},
    "Sách":        {"weight": 0.09, "price": (90_000, 0.50),  "cost_ratio": 0.65},
    "Thực phẩm":   {"weight": 0.08, "price": (120_000, 0.40), "cost_ratio": 0.70},
}
CAT_NAMES = list(CATEGORIES.keys())
CAT_WEIGHTS = [CATEGORIES[c]["weight"] for c in CAT_NAMES]

PAYMENT_METHODS = ["COD", "Thẻ tín dụng", "Ví điện tử", "Chuyển khoản"]
PAYMENT_WEIGHTS = [0.35, 0.25, 0.28, 0.12]

DEVICES = ["Mobile", "Desktop", "Tablet"]
DEVICE_WEIGHTS = [0.62, 0.30, 0.08]


def random_dates(n):
    """Ngay dat hang, co xu huong tang theo thoi gian + mua cao diem cuoi nam."""
    total_days = (END_DATE - START_DATE).days
    day_idx = np.arange(total_days + 1)

    # Xu huong tang truong dan deu (~tang 1.6 lan tu dau den cuoi)
    trend = 1.0 + 0.6 * (day_idx / total_days)

    dates = START_DATE + pd.to_timedelta(day_idx, unit="D")
    month = dates.month
    dow = dates.dayofweek  # 0=thu2 ... 6=chu nhat

    # Mua cao diem: thang 11-12 (Black Friday, Tet prep) cao hon; thang 2 (Tet) thap hon
    seasonal = np.ones(len(day_idx))
    seasonal[np.isin(month, [11, 12])] *= 1.5
    seasonal[np.isin(month, [2])] *= 0.6
    seasonal[np.isin(month, [6, 7])] *= 1.1  # mua he

    # Cuoi tuan mua sam nhieu hon
    weekday_effect = np.where(dow >= 5, 1.25, 1.0)

    weight = trend * seasonal * weekday_effect
    weight = weight / weight.sum()

    chosen_idx = RNG.choice(day_idx, size=n, p=weight)
    return START_DATE + pd.to_timedelta(chosen_idx, unit="D")


def build_orders():
    n = N_ORDERS
    order_id = np.arange(1, n + 1)
    order_date = random_dates(n)

    # --- Khach hang ---
    n_customers = int(n * 0.55)  # co khach mua lai
    customer_id = RNG.integers(1, n_customers + 1, size=n)
    customer_age = np.clip(RNG.normal(32, 9, size=n_customers + 1), 18, 70).round().astype(int)
    customer_gender_pool = RNG.choice(["Nữ", "Nam"], size=n_customers + 1, p=[0.58, 0.42])
    age = customer_age[customer_id]
    gender = customer_gender_pool[customer_id]

    region = RNG.choice(REGIONS, size=n, p=REGION_WEIGHTS)
    channel = RNG.choice(CHANNELS, size=n, p=CHANNEL_WEIGHTS)
    category = RNG.choice(CAT_NAMES, size=n, p=CAT_WEIGHTS)
    payment_method = RNG.choice(PAYMENT_METHODS, size=n, p=PAYMENT_WEIGHTS)
    device = RNG.choice(DEVICES, size=n, p=DEVICE_WEIGHTS)

    # --- Gia, so luong, giam gia (phu thuoc category) ---
    base_price = np.array([CATEGORIES[c]["price"][0] for c in category], dtype=float)
    price_sigma = np.array([CATEGORIES[c]["price"][1] for c in category], dtype=float)
    cost_ratio = np.array([CATEGORIES[c]["cost_ratio"] for c in category], dtype=float)

    # Gia don vi phan phoi log-normal (lech phai, dac trung du lieu doanh thu)
    unit_price = base_price * RNG.lognormal(mean=0, sigma=price_sigma * 0.35)
    unit_price = np.round(unit_price, -3)  # lam tron hang nghin VND
    unit_price = np.clip(unit_price, 10_000, None)

    discount_pct = np.clip(RNG.beta(2, 8, size=n) * 0.5, 0, 0.5)  # da so giam it, it truong hop giam sau

    # Gia cao hon -> so luong mua it hon (tuong quan am nhe) + nhieu
    lam = np.clip(3.2 - 0.35 * np.log1p(unit_price / 100_000) + RNG.normal(0, 0.4, n), 0.3, None)
    quantity = RNG.poisson(lam=lam) + 1
    quantity = np.clip(quantity, 1, 12)

    # Giam gia sau hon -> co xu huong mua nhieu hon mot chut
    quantity = np.where(discount_pct > 0.25, quantity + RNG.integers(0, 2, n), quantity)

    gross_revenue = unit_price * quantity
    net_revenue = np.round(gross_revenue * (1 - discount_pct), 0)
    unit_cost = np.round(unit_price * cost_ratio * RNG.normal(1, 0.05, n), 0)
    profit = np.round(net_revenue - unit_cost * quantity, 0)

    # --- Giao hang & hai long ---
    delivery_days = np.clip(RNG.gamma(shape=2.2, scale=1.3, size=n), 0.5, 14).round().astype(float)

    # Giao lau hon -> hai long thap hon (tuong quan am), them nhieu
    satisfaction_raw = 4.6 - 0.18 * delivery_days + RNG.normal(0, 0.6, n)
    satisfaction = np.clip(np.round(satisfaction_raw), 1, 5)

    # Vai don "khung" (outlier) de luyen phat hien outlier
    outlier_idx = RNG.choice(n, size=max(1, n // 250), replace=False)
    quantity[outlier_idx] = RNG.integers(15, 40, size=len(outlier_idx))
    gross_revenue[outlier_idx] = unit_price[outlier_idx] * quantity[outlier_idx]
    net_revenue[outlier_idx] = np.round(gross_revenue[outlier_idx] * (1 - discount_pct[outlier_idx]), 0)
    profit[outlier_idx] = np.round(net_revenue[outlier_idx] - unit_cost[outlier_idx] * quantity[outlier_idx], 0)

    # Tra hang: xac suat cao hon khi hai long thap
    return_prob = np.clip(0.25 - 0.045 * satisfaction, 0.01, 0.5)
    is_returned = (RNG.random(n) < return_prob).astype(int)

    df = pd.DataFrame({
        "order_id": order_id,
        "order_date": order_date,
        "customer_id": customer_id,
        "customer_age": age,
        "customer_gender": gender,
        "region": region,
        "acquisition_channel": channel,
        "product_category": category,
        "unit_price_vnd": unit_price.astype(int),
        "quantity": quantity,
        "discount_pct": discount_pct.round(3),
        "gross_revenue_vnd": gross_revenue.astype(int),
        "net_revenue_vnd": net_revenue.astype(int),
        "unit_cost_vnd": unit_cost.astype(int),
        "profit_vnd": profit.astype(int),
        "payment_method": payment_method,
        "device": device,
        "delivery_days": delivery_days,
        "customer_satisfaction": satisfaction,
        "is_returned": is_returned,
    })

    df = df.sort_values("order_date").reset_index(drop=True)
    df["order_id"] = np.arange(1, n + 1)

    # --- Them gia tri thieu de luyen xu ly missing data ---
    for col, frac in [("customer_satisfaction", 0.05), ("delivery_days", 0.03), ("customer_age", 0.02)]:
        idx = RNG.choice(n, size=int(n * frac), replace=False)
        df.loc[idx, col] = np.nan

    return df


def build_daily_marketing(orders: pd.DataFrame):
    """Bang chi tieu marketing & doanh thu theo ngay - luyen hoi quy tuyen tinh."""
    daily_revenue = orders.groupby("order_date")["net_revenue_vnd"].sum()
    all_days = pd.date_range(START_DATE, END_DATE, freq="D")
    daily_revenue = daily_revenue.reindex(all_days, fill_value=0)

    n = len(all_days)
    dow = all_days.dayofweek
    base_spend = 3_000_000 + 800_000 * np.where(dow >= 5, 1.3, 1.0)
    month = all_days.month
    base_spend = base_spend * np.where(np.isin(month, [11, 12]), 1.6, 1.0)
    marketing_spend = np.clip(base_spend * RNG.normal(1, 0.15, n), 500_000, None).round(0)

    website_visits = np.clip(
        200 + 0.012 * marketing_spend + RNG.normal(0, 150, n), 50, None
    ).round(0)

    df = pd.DataFrame({
        "date": all_days,
        "marketing_spend_vnd": marketing_spend.astype(int),
        "website_visits": website_visits.astype(int),
        "daily_net_revenue_vnd": daily_revenue.values.astype(int),
    })
    return df


if __name__ == "__main__":
    orders_df = build_orders()
    orders_df.to_csv("orders.csv", index=False, encoding="utf-8-sig")
    print(f"Da tao orders.csv: {len(orders_df)} dong, {orders_df.shape[1]} cot")

    marketing_df = build_daily_marketing(orders_df)
    marketing_df.to_csv("daily_marketing.csv", index=False, encoding="utf-8-sig")
    print(f"Da tao daily_marketing.csv: {len(marketing_df)} dong, {marketing_df.shape[1]} cot")
