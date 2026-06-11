"""数据获取服务: 股票搜索与日 K 线数据。

数据源优先使用 AKShare。设置环境变量 USE_MOCK_DATA=1 可使用本地生成的
演示数据(用于无网络环境下的功能演示, 返回结果中 is_mock=True)。
"""

import logging
import os
from datetime import date, timedelta
from functools import lru_cache

import numpy as np
import pandas as pd

from app.utils.date_utils import estimate_start_date, fmt_yyyymmdd

logger = logging.getLogger(__name__)

USE_MOCK_DATA = os.environ.get("USE_MOCK_DATA", "0") == "1"

# 统一后的 K 线列名
KLINE_COLUMNS = ["date", "open", "high", "low", "close", "volume", "amount", "pct_chg", "turnover"]


class DataSourceError(Exception):
    """数据源不可用或返回为空。"""


def _exchange_of(code: str) -> str:
    if code.startswith(("60", "68", "9")):
        return "SH"
    if code.startswith(("00", "30", "2")):
        return "SZ"
    if code.startswith(("8", "4")):
        return "BJ"
    return ""


# ---------------------------------------------------------------------------
# 股票搜索
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_stock_list() -> pd.DataFrame:
    """加载全部 A 股代码和名称(缓存)。"""
    if USE_MOCK_DATA:
        return _mock_stock_list()
    try:
        import akshare as ak

        df = ak.stock_info_a_code_name()
        df = df.rename(columns={"code": "code", "name": "name"})
        return df[["code", "name"]]
    except Exception as exc:  # noqa: BLE001
        logger.warning("AKShare 股票列表获取失败: %s", exc)
        raise DataSourceError(
            "无法从 AKShare 获取股票列表, 请检查网络; "
            "或设置环境变量 USE_MOCK_DATA=1 使用演示数据"
        ) from exc


def search_stocks(keyword: str, limit: int = 20) -> list[dict]:
    """按股票代码或名称模糊搜索 A 股。"""
    keyword = keyword.strip()
    if not keyword:
        return []
    df = _load_stock_list()
    mask = df["code"].str.contains(keyword, na=False) | df["name"].str.contains(
        keyword, na=False
    )
    hits = df[mask].head(limit)
    return [
        {
            "code": row["code"],
            "name": row["name"],
            "market": "A股",
            "exchange": _exchange_of(row["code"]),
        }
        for _, row in hits.iterrows()
    ]


def get_stock_name(code: str) -> str:
    try:
        df = _load_stock_list()
        hit = df[df["code"] == code]
        if not hit.empty:
            return str(hit.iloc[0]["name"])
    except DataSourceError:
        pass
    return ""


# ---------------------------------------------------------------------------
# 日 K 线
# ---------------------------------------------------------------------------

def get_stock_daily_data(code: str, days: int, indicator_buffer: int = 25) -> pd.DataFrame:
    """获取最近 days 个交易日的日 K 线(前复权), 并完成数据清洗。

    为了让均线等指标在整个展示区间内有效, 额外多取 indicator_buffer 个
    交易日参与计算, 返回的 DataFrame 仍只保留最近 days 行(指标列已算好)。
    """
    total_days = days + indicator_buffer
    if USE_MOCK_DATA:
        raw = _mock_daily_data(code, total_days)
        raw.attrs["is_mock"] = True
    else:
        raw = _fetch_from_akshare(code, total_days)
        raw.attrs["is_mock"] = False

    df = clean_data(raw)
    df = add_indicators(df)
    result = df.tail(days).reset_index(drop=True)
    result.attrs["is_mock"] = raw.attrs.get("is_mock", False)
    return result


def _fetch_from_akshare(code: str, trading_days: int) -> pd.DataFrame:
    try:
        import akshare as ak

        start = estimate_start_date(trading_days)
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=fmt_yyyymmdd(start),
            end_date=fmt_yyyymmdd(date.today()),
            adjust="qfq",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("AKShare K线获取失败 code=%s: %s", code, exc)
        raise DataSourceError(
            f"无法从 AKShare 获取 {code} 的日K线数据, 请检查代码是否正确或网络是否可用; "
            "或设置环境变量 USE_MOCK_DATA=1 使用演示数据"
        ) from exc

    if df is None or df.empty:
        raise DataSourceError(f"股票 {code} 没有查询到K线数据, 请确认代码是否正确")

    df = df.rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "pct_chg",
            "换手率": "turnover",
        }
    )
    keep = [c for c in KLINE_COLUMNS if c in df.columns]
    return df[keep]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """日期升序、去空值、统一类型。"""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values("date").reset_index(drop=True)
    numeric_cols = [c for c in df.columns if c != "date"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close", "volume"]).reset_index(drop=True)
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算涨跌幅、振幅、量比基础、均线等指标列。"""
    df = df.copy()
    prev_close = df["close"].shift(1)
    df["pct_chg"] = (df["close"] - prev_close) / prev_close * 100
    df["amplitude"] = (df["high"] - df["low"]) / prev_close * 100
    df["volume_change"] = df["volume"].pct_change() * 100
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma10"] = df["close"].rolling(10).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["vol_ma5"] = df["volume"].rolling(5).mean()
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    return df


# ---------------------------------------------------------------------------
# 演示数据(无网络环境下使用, is_mock=True)
# ---------------------------------------------------------------------------

_MOCK_STOCKS = [
    ("688766", "普冉股份"),
    ("300604", "长川科技"),
    ("600519", "贵州茅台"),
    ("002371", "北方华创"),
    ("688981", "中芯国际"),
]


def _mock_stock_list() -> pd.DataFrame:
    return pd.DataFrame(_MOCK_STOCKS, columns=["code", "name"])


def _mock_daily_data(code: str, trading_days: int) -> pd.DataFrame:
    """生成台阶式走势的演示K线: 上涨-回调-横盘-再上涨 循环加噪声。"""
    rng = np.random.default_rng(abs(hash(code)) % (2**32))
    n = trading_days
    # 阶段日收益均值: 上涨 / 回调 / 横盘 / 突破
    phases = [(8, 0.018), (5, -0.008), (7, 0.0005), (4, 0.025)]
    drift = []
    while len(drift) < n:
        for length, mu in phases:
            drift.extend([mu] * length)
    drift = np.array(drift[:n])
    returns = drift + rng.normal(0, 0.015, n)
    close = 100 * np.cumprod(1 + returns)
    open_ = close / (1 + returns) * (1 + rng.normal(0, 0.004, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.008, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.008, n)))
    base_vol = 150000
    volume = base_vol * (1 + np.clip(returns * 18, -0.6, 2.5)) * (
        1 + rng.normal(0, 0.2, n)
    )
    volume = np.abs(volume)

    end = date.today()
    dates: list[str] = []
    d = end
    while len(dates) < n:
        if d.weekday() < 5:
            dates.append(d.strftime("%Y-%m-%d"))
        d -= timedelta(days=1)
    dates.reverse()

    return pd.DataFrame(
        {
            "date": dates,
            "open": open_.round(2),
            "high": high.round(2),
            "low": low.round(2),
            "close": close.round(2),
            "volume": volume.round(0),
            "amount": (volume * close).round(0),
        }
    )
