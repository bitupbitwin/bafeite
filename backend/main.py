"""股票台阶式上涨预测工具 - FastAPI 入口。

启动方式:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

环境变量:
    USE_MOCK_DATA=1   使用本地生成的演示数据(无需联网, 仅用于功能演示)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.stock_api import router as stock_router
from app.api.analyze_api import router as analyze_router

RISK_WARNING = (
    "本工具仅基于历史价格、成交量和技术指标进行统计分析，不构成任何投资建议。"
    "股票价格受政策、业绩、市场情绪、资金流、突发消息等多种因素影响，"
    "模型预测结果可能失效。用户应独立判断并自行承担投资风险。"
)

app = FastAPI(
    title="股票台阶式上涨预测工具",
    description="基于历史 K 线、成交量、回调幅度、横盘区间和突破信号的"
    "台阶式上涨识别与次日涨跌概率估算工具。" + RISK_WARNING,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "股票台阶式上涨预测工具",
        "docs": "/docs",
        "risk_warning": RISK_WARNING,
    }
