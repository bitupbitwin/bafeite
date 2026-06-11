"""股票搜索与K线数据接口。"""

import math

from fastapi import APIRouter, HTTPException, Query

from app.models.stock_models import KLineBar, KLineResponse, StockInfo
from app.services import data_service
from app.services.data_service import DataSourceError

router = APIRouter(tags=["stocks"])


@router.get("/stocks/search", response_model=list[StockInfo])
def search_stocks(keyword: str = Query(..., min_length=1)):
    """按股票名称或代码搜索 A 股。"""
    try:
        return data_service.search_stocks(keyword)
    except DataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def _safe(v) -> float | None:
    try:
        f = float(v)
        return None if math.isnan(f) else round(f, 3)
    except (TypeError, ValueError):
        return None


@router.get("/stocks/{code}/kline", response_model=KLineResponse)
def get_kline(code: str, period: int = Query(default=30, ge=5, le=250)):
    """获取最近 period 个交易日的日K线(含均线指标)。"""
    try:
        df = data_service.get_stock_daily_data(code, period)
    except DataSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    bars = [
        KLineBar(
            date=row["date"],
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
            volume=row["volume"],
            amount=_safe(row.get("amount")),
            pct_chg=_safe(row.get("pct_chg")),
            ma5=_safe(row.get("ma5")),
            ma10=_safe(row.get("ma10")),
            ma20=_safe(row.get("ma20")),
        )
        for _, row in df.iterrows()
    ]
    return KLineResponse(
        code=code,
        name=data_service.get_stock_name(code),
        is_mock=bool(df.attrs.get("is_mock", False)),
        data=bars,
    )
