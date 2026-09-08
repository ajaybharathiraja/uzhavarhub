# Data Audit and Preprocessing Report

## 1. Crop Recommendation Dataset
- **Row count:** 2200
- **Columns:** N, P, K, temperature, humidity, ph, rainfall, label
- **Missing values:** None
- **Class balance:** Perfectly balanced (most classes have ~200 samples).
- **Saved to:** `data/processed/crop_recommendation.csv`

## 2. Demand Forecasting Dataset
- **Row count:** 76000
- **Columns:** Date, Store ID, Product ID, Category, Region, Inventory Level, Units Sold, Units Ordered, Price, Discount, Weather Condition, Promotion, Competitor Pricing, Seasonality, Epidemic, Demand
- **Missing values:** None
- **Saved to:** `data/processed/demand_forecasting.csv`

## 3. E-commerce Sales Dataset
- **Row count:** 5000
- **Columns:** order_id, order_date, customer_id, product_category, region, quantity, unit_price, discount, payment_method, delivery_days, customer_rating, revenue
- **Missing values:** None
- **Saved to:** `data/processed/ecommerce_sales.csv`
