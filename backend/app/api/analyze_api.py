"""分析预测与回测接口。"""

from fastapi import APIRouter, HTTPException

from app.models.prediction_models import (
    AnalyzeRequest,
    AnalyzeResponse,
    BacktestRequest,
    BacktestResponse,
)
from app.services import data_service, prediction_service
from app.services.data_service import DataSourceError

router = APIRouter(tags=["analyze"])


def _period_label(days: int) -> str:
    mapping = {7: "最近7个交易日", 15: "最近15个交易日", 22: "最近1个月", 44: "最近2个月", 66: "最近3个月"}
    return mapping.get(days, f"最近{days}个交易日")


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """对指定股票做台阶式上涨分析, 输出明日涨跌概率与区间预测。"""
    try:
        df = data_service.get_stock_daily_data(req.code, req.period_days)
    except DataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if len(df) < 5:
        raise HTTPException(status_code=400, detail="K线数据不足5个交易日, 无法分析")

    result = prediction_service.analyze(df)
    return AnalyzeResponse(
        stock={"code": req.code, "name": data_service.get_stock_name(req.code)},
        period=_period_label(req.period_days),
        is_mock=bool(df.attrs.get("is_mock", False)),
        **result,
    )


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest):
    """滚动回测: 验证模型在该股票最近一段时间的方向预测准确率。"""
    try:
        df = data_service.get_stock_daily_data(req.code, req.window_days + req.test_days)
    except DataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if len(df) <= req.window_days + 5:
        raise HTTPException(status_code=400, detail="历史数据不足, 无法回测")

    result = prediction_service.backtest(df, window_days=req.window_days)
    return BacktestResponse(
        stock={"code": req.code, "name": data_service.get_stock_name(req.code)},
        is_mock=bool(df.attrs.get("is_mock", False)),
        **result,
    )
