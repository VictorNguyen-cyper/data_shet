# Bộ dữ liệu mô phỏng: VinaMart Online (bán lẻ/e-commerce)

Sinh bởi `generate_data.py` (seed cố định = 42, chạy lại sẽ ra kết quả giống hệt).
Giai đoạn: 2024-01-01 → 2025-12-31 (2 năm, có xu hướng tăng trưởng + mùa vụ).

## 1. `orders.csv` — 6000 đơn hàng, 20 cột

| Cột | Kiểu | Mô tả | Dùng để luyện |
|---|---|---|---|
| order_id | int | Mã đơn hàng | — |
| order_date | date | Ngày đặt hàng | time series, xu hướng, mùa vụ |
| customer_id | int | Mã khách hàng (có khách mua lại) | groupby, RFM |
| customer_age | float | Tuổi khách hàng (**có ~2% thiếu**) | xử lý missing, phân phối |
| customer_gender | str | Nam / Nữ | thống kê theo nhóm, chi-square |
| region | str | 5 khu vực (Hà Nội, TP.HCM, Đà Nẵng, Hải Phòng, Cần Thơ) | ANOVA, chi-square |
| acquisition_channel | str | Kênh tiếp cận (Organic, Facebook Ads, Google Ads, Referral, Email) | so sánh nhóm |
| product_category | str | 6 ngành hàng | ANOVA, phân phối theo nhóm |
| unit_price_vnd | int | Đơn giá | phân phối lệch phải (log-normal) |
| quantity | int | Số lượng mua (có vài đơn "khủng" — outlier) | phát hiện outlier |
| discount_pct | float | % giảm giá (0–0.5) | tương quan với quantity |
| gross_revenue_vnd | int | Doanh thu trước giảm giá | — |
| net_revenue_vnd | int | Doanh thu sau giảm giá | biến mục tiêu hồi quy |
| unit_cost_vnd | int | Giá vốn/đơn vị | tính margin |
| profit_vnd | int | Lợi nhuận (có thể âm) | phân phối, outlier |
| payment_method | str | COD / Thẻ tín dụng / Ví điện tử / Chuyển khoản | chi-square |
| device | str | Mobile / Desktop / Tablet | chi-square |
| delivery_days | float | Số ngày giao hàng (**có ~3% thiếu**) | tương quan âm với satisfaction |
| customer_satisfaction | float | Điểm hài lòng 1–5 (**có ~5% thiếu**) | hồi quy, kiểm định giả thuyết |
| is_returned | int | 1 = trả hàng (xác suất cao hơn khi hài lòng thấp) | logistic regression |

**Tương quan đáng chú ý đã cài sẵn:**
- `delivery_days` ↔ `customer_satisfaction`: tương quan âm (~ -0.47)
- `unit_price_vnd` ↔ `quantity`: tương quan âm nhẹ
- `customer_satisfaction` thấp → `is_returned` xác suất cao hơn
- Doanh thu tăng dần theo thời gian, cao điểm tháng 11–12, giảm mạnh tháng 2 (Tết)

## 2. `daily_marketing.csv` — 731 ngày, 4 cột

| Cột | Mô tả |
|---|---|
| date | Ngày |
| marketing_spend_vnd | Chi tiêu marketing/ngày |
| website_visits | Lượt truy cập web/ngày (tương quan dương với chi tiêu, có nhiễu) |
| daily_net_revenue_vnd | Tổng doanh thu net trong ngày (tổng hợp từ orders.csv) |

Dùng để luyện: hồi quy tuyến tính đơn/đa biến (`marketing_spend` → `website_visits`/`daily_net_revenue`), tương quan Pearson, kiểm định ý nghĩa hệ số hồi quy.

## Cách đưa vào Google Sheets

1. Mở Google Sheets → **File > Import** (hoặc **Nhập**).
2. Chọn **Upload**, kéo thả file `orders.csv` (hoặc `daily_marketing.csv`).
3. Chọn "Insert new sheet" và "Comma" làm dấu phân tách → **Import data**.
4. Lặp lại để import file còn lại vào 1 sheet khác trong cùng file.

## Cách đọc bằng Python

```python
import pandas as pd
orders = pd.read_csv("orders.csv", parse_dates=["order_date"])
marketing = pd.read_csv("daily_marketing.csv", parse_dates=["date"])
```
