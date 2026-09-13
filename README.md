# VinaMart Online — Simulated Retail Dataset

A synthetic e-commerce dataset generated for practicing Python statistics (pandas, numpy, scipy). It models a fictional Vietnamese retail business ("VinaMart Online") with realistic distributions, correlations, missing values, and outliers.

## Contents

| File | Rows | Description |
|---|---|---|
| `generate_data.py` | — | Script that generates the dataset (fixed seed = 42, fully reproducible) |
| `orders.csv` | 6,000 | Order-level transactions, 2024-01-01 to 2025-12-31 |
| `daily_marketing.csv` | 731 | Daily marketing spend, website visits, and revenue |
| `DATA_DICTIONARY.md` | — | Column-by-column reference (in Vietnamese) |

## Quick start

```bash
pip install pandas numpy
python3 generate_data.py   # regenerates orders.csv and daily_marketing.csv
```

```python
import pandas as pd

orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
marketing = pd.read_csv("daily_marketing.csv", parse_dates=["date"])
```

## Why this dataset

It's built for exercises, not just display, so it bakes in the kind of messiness real data has:

- **Skewed distributions** — prices and revenue follow a log-normal shape (good for log transforms, skewness/kurtosis exercises).
- **Missing values** — `customer_age`, `delivery_days`, and `customer_satisfaction` each have a few percent of nulls (missing-data handling).
- **Outliers** — a handful of unusually large orders are injected on purpose (outlier detection).
- **Built-in correlations** — e.g. `delivery_days` correlates negatively with `customer_satisfaction` (~ -0.47), and low satisfaction increases the odds of `is_returned` (good for regression / logistic regression practice).
- **Seasonality & trend** — revenue grows over the two-year window, spikes in November–December, and dips in February (Lunar New Year) — useful for time-series and group comparisons.
- **Unequal group sizes** — regions, channels, and categories aren't evenly distributed, which matters for chi-square and ANOVA exercises.

See `DATA_DICTIONARY.md` for the full column reference and suggested statistical techniques per column.

## Suggested exercises

- Descriptive statistics & distribution plots on `unit_price_vnd`, `net_revenue_vnd`, `profit_vnd`
- Missing-data imputation on `customer_satisfaction` / `delivery_days`
- Outlier detection (z-score, IQR) on `quantity` and `profit_vnd`
- Correlation & simple linear regression: `marketing_spend_vnd` → `daily_net_revenue_vnd` (in `daily_marketing.csv`)
- Hypothesis testing / ANOVA: revenue across `region` or `product_category`
- Chi-square test of independence: `payment_method` vs `region`
- Logistic regression: predicting `is_returned` from `delivery_days` and `customer_satisfaction`

## License

This is synthetic, fictional data intended for learning purposes. Use it however you like.
