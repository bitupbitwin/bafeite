# 后端接口文档

Base URL: `http://localhost:8000/api`。运行后端后也可访问 Swagger 交互文档 `http://localhost:8000/docs`。

数据源不可用时接口返回 `502`，K 线不足时返回 `400`，`detail` 字段为中文错误说明。所有响应中 `is_mock: true` 表示当前为演示数据（后端以 `USE_MOCK_DATA=1` 启动）。

---

## 1. 股票搜索

```
GET /api/stocks/search?keyword=普冉
```

按股票名称或代码模糊搜索 A 股，最多返回 20 条。

```json
[
  { "code": "688766", "name": "普冉股份", "market": "A股", "exchange": "SH" }
]
```

## 2. 获取 K 线数据

```
GET /api/stocks/{code}/kline?period=30
```

- `period`：交易日数量，5~250，默认 30。
- 返回前复权日 K 线，已包含 MA5/MA10/MA20（区间起始处均线已用更早数据算好，不会为空）。

```json
{
  "code": "688766",
  "name": "普冉股份",
  "is_mock": false,
  "data": [
    {
      "date": "2026-06-10",
      "open": 110.2, "high": 116.5, "low": 109.8, "close": 115.3,
      "volume": 182000, "amount": 20988000,
      "pct_chg": 1.22, "ma5": 113.4, "ma10": 110.1, "ma20": 105.8
    }
  ]
}
```

## 3. 分析预测

```
POST /api/analyze
Content-Type: application/json

{ "code": "688766", "period_days": 30 }
```

- `period_days`：参与分析的交易日数量，5~250。少于 20 时只做简单趋势判断，并在 `explanation` 中说明。

```json
{
  "stock": { "code": "688766", "name": "普冉股份" },
  "period": "最近1个月",
  "is_mock": false,
  "current_price": 115.3,
  "today_pct_chg": 1.22,
  "current_state": "横盘整理",
  "score": 35,
  "up_probability": 62.25,
  "down_probability": 37.75,
  "expected_up_range": "0% ~ 3.8%",
  "expected_down_range": "0% ~ -2.4%",
  "support_price": 112.3,
  "pressure_price": 119.8,
  "explanation": ["..."],
  "risk_warning": "..."
}
```

`current_state` 取值：`上涨阶段`、`健康回调`、`横盘整理`、`突破阶段`、`风险阶段`、`震荡观察`。

## 4. 回测

```
POST /api/backtest
Content-Type: application/json

{ "code": "688766", "window_days": 30, "test_days": 60 }
```

- `window_days`：每次预测使用的历史窗口（20~120，默认 30）。
- `test_days`：滚动测试的交易日数量（10~250，默认 60）。

逻辑：用第 1~30 天预测第 31 天，用第 2~31 天预测第 32 天……统计方向预测正确率。

```json
{
  "stock": { "code": "688766", "name": "普冉股份" },
  "total": 60,
  "correct": 33,
  "wrong": 27,
  "accuracy": 55.0,
  "avg_predicted_up_probability": 58.4,
  "avg_actual_pct_chg": 0.12,
  "worst_cases": [
    { "date": "2026-05-12", "predicted": "上涨", "up_probability": 71.0, "actual_pct_chg": -6.8, "correct": false }
  ],
  "risk_warning": "..."
}
```

`worst_cases` 为预测方向错误且实际波动最大的 5 个案例。
