# 股票台阶式上涨预测工具

一个可在电脑和手机浏览器中使用的 A 股分析工具。输入股票代码或名称后，系统获取最近一段时间的日 K 线数据，根据「上涨—回调—横盘—再上涨」的台阶式走势规律构建简易数学模型，输出：

- 明日上涨/下跌概率
- 预计涨跌幅度区间
- 当前状态判断（上涨阶段 / 健康回调 / 横盘整理 / 突破阶段 / 风险阶段 / 震荡观察）
- 支撑位与压力位
- 模型判断的文字解释
- 历史滚动回测准确率

> ⚠️ **风险提示**：本工具仅基于历史价格、成交量和技术指标进行统计分析，**不构成任何投资建议**。股票价格受政策、业绩、市场情绪、资金流、突发消息等多种因素影响，模型预测结果可能失效。用户应独立判断并自行承担投资风险。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | React 18 + TypeScript + Vite + ECharts |
| 后端 | Python 3.11 + FastAPI |
| 数据处理 | pandas / numpy |
| 数据源 | AKShare（A 股日 K 线，前复权） |
| 部署 | 本地运行 / Docker Compose |

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

接口文档（Swagger）：http://localhost:8000/docs

无法联网获取行情时（仅用于功能演示，结果会标记 `is_mock: true` 并在页面顶部显示提示）：

```bash
USE_MOCK_DATA=1 uvicorn main:app --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173 （开发服务器已将 `/api` 代理到后端 8000 端口）。手机与电脑在同一局域网时，可通过 `http://<电脑IP>:5173` 访问。

### 3. Docker 一键部署（可选）

```bash
docker compose up --build
```

前端访问 http://localhost:8080 ，后端 http://localhost:8000 。

## 接口概览

详细文档见 [docs/API.md](docs/API.md)，或运行后端后访问 `/docs`。

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/stocks/search?keyword=普冉` | GET | 按名称/代码搜索股票 |
| `/api/stocks/{code}/kline?period=30` | GET | 获取日 K 线（含 MA5/10/20） |
| `/api/analyze` | POST | 台阶式分析与次日涨跌预测 |
| `/api/backtest` | POST | 滚动回测，统计方向预测准确率 |

## 模型说明

模型原理（特征计算、状态分类规则、评分表、概率转换、区间估算、回测方法）见 [docs/MODEL.md](docs/MODEL.md)。

核心思路：把台阶式上涨拆成「上涨 → 回调 → 横盘 → 再突破」四个阶段，用趋势涨幅、回调深度、箱体振幅、量比、均线位置、突破/假突破、长上影线等特征判断当前阶段，再用 -100~+100 的评分模型换算成次日上涨概率（`50% + score × 0.35`，限制在 10%~90%），并按状态修正基于近 20 日平均绝对涨跌幅的波动区间。

## 示例输出（演示数据）

```json
{
  "stock": { "code": "688766", "name": "普冉股份" },
  "period": "最近30个交易日",
  "current_state": "上涨阶段",
  "score": 70,
  "up_probability": 74.5,
  "down_probability": 25.5,
  "expected_up_range": "0% ~ 2.33%",
  "expected_down_range": "0% ~ -1.55%",
  "support_price": 133.78,
  "pressure_price": 166.73,
  "explanation": [
    "最近10日累计上涨 22.9%, 短期趋势强劲, 但追高风险增加",
    "当前价格站上5日和10日均线, 短期多头排列",
    "收盘价突破最近10日高点, 若量能持续则可能开启新一轮上涨",
    "综合评分 70 分(满分±100), 当前判定为「上涨阶段」"
  ]
}
```

回测示例（同一演示数据，40 个交易日滚动预测）：总预测 40 次，正确 26 次，准确率 65%。**注意：演示数据本身就是按台阶规律生成的，真实行情下的准确率会明显更低，请务必用 `/api/backtest` 对真实数据自行验证。**

## 目录结构

```
├── backend/
│   ├── main.py                  # FastAPI 入口
│   ├── requirements.txt
│   └── app/
│       ├── api/                 # 路由: stock_api / analyze_api
│       ├── services/            # data / feature / prediction 三层服务
│       ├── models/              # Pydantic 请求/响应模型
│       └── utils/
├── frontend/
│   └── src/
│       ├── api/stockApi.ts
│       ├── pages/               # HomePage / ResultPage
│       ├── components/          # StockSearch / PredictionCard / KLineChart / ExplanationPanel
│       └── styles/main.css
├── docs/                        # API 与模型文档
└── docker-compose.yml
```

## 已知限制

- 模型至少需要 20 个交易日数据；周期过短时只做简单趋势判断，结论可靠性低。
- AKShare 免费接口依赖网络与上游站点稳定性；如需更稳定的数据可自行接入 Tushare Pro。
- 第一版不包含：自动交易、账户登录、机器学习模型、多股票批量扫描、分钟级数据。
