"""股票相关数据模型。"""

from pydantic import BaseModel


class StockInfo(BaseModel):
    code: str
    name: str
    market: str = "A股"
    exchange: str = ""


class KLineBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float | None = None
    pct_chg: float | None = None
    ma5: float | None = None
    ma10: float | None = None
    ma20: float | None = None


class KLineResponse(BaseModel):
    code: str
    name: str = ""
    is_mock: bool = False
    data: list[KLineBar]
