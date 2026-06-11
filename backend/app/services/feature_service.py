"""特征计算服务: 趋势、回调、横盘、量能、突破与风险信号。

所有特征都基于截至最后一行的历史数据计算, 供状态分类与评分模型使用。
"""

import pandas as pd

# 模型完整运行所需的最少交易日数
MIN_DAYS_FOR_FULL_MODEL = 20


def _trend_return(df: pd.DataFrame, n: int) -> float:
    """最近 n 天累计涨幅(%)。数据不足时按可用区间计算。"""
    if len(df) < 2:
        return 0.0
    n = min(n, len(df) - 1)
    base = df["close"].iloc[-1 - n]
    return float((df["close"].iloc[-1] - base) / base * 100)


def calculate_features(df: pd.DataFrame) -> dict:
    """计算最后一个交易日的全部模型特征。

    df 需要已包含 add_indicators 算出的 pct_chg / ma / vol_ma 列。
    """
    last = df.iloc[-1]
    current_close = float(last["close"])

    # --- 趋势强度 ---
    trend_return_5 = _trend_return(df, 5)
    trend_return_10 = _trend_return(df, 10)
    trend_return_20 = _trend_return(df, 20)

    # --- 回调幅度: 距最近20天最高价 ---
    recent_high = float(df["high"].tail(20).max())
    drawdown = (current_close - recent_high) / recent_high * 100

    # --- 横盘区间: 最近5天箱体振幅 ---
    box = df.tail(5)
    box_high = float(box["high"].max())
    box_low = float(box["low"].min())
    box_range = (box_high - box_low) / box_low * 100 if box_low > 0 else 0.0

    # --- 量能 ---
    vol_ma20 = float(last["vol_ma20"]) if pd.notna(last["vol_ma20"]) else float(
        df["volume"].mean()
    )
    vol_ma5 = float(last["vol_ma5"]) if pd.notna(last["vol_ma5"]) else vol_ma20
    volume_ratio = float(last["volume"]) / vol_ma20 if vol_ma20 > 0 else 1.0

    # --- 均线 ---
    ma5 = float(last["ma5"]) if pd.notna(last["ma5"]) else current_close
    ma10 = float(last["ma10"]) if pd.notna(last["ma10"]) else current_close
    ma20 = float(last["ma20"]) if pd.notna(last["ma20"]) else current_close

    pct_chg_today = float(last["pct_chg"]) if pd.notna(last["pct_chg"]) else 0.0

    # --- 突破信号: 收盘价创出之前5/10日新高 ---
    prev = df.iloc[:-1]
    high_5 = float(prev["high"].tail(5).max()) if len(prev) >= 5 else current_close
    high_10 = float(prev["high"].tail(10).max()) if len(prev) >= 10 else high_5
    breakout_5 = current_close > high_5
    breakout_10 = current_close > high_10
    breakout = breakout_5 and volume_ratio > 1.3 and current_close > ma5 and current_close > ma10

    # 假突破: 昨日收盘突破前5日高点, 今日收盘又跌回突破位之下
    false_breakout = False
    if len(df) >= 8:
        yesterday_close = float(df["close"].iloc[-2])
        high_5_before_yesterday = float(df["high"].iloc[:-2].tail(5).max())
        false_breakout = (
            yesterday_close > high_5_before_yesterday
            and current_close < high_5_before_yesterday
        )

    # --- 风险信号 ---
    body = abs(current_close - float(last["open"]))
    upper_shadow = float(last["high"]) - max(current_close, float(last["open"]))
    long_upper_shadow = (
        upper_shadow > body * 2 and upper_shadow / current_close * 100 > 1.5
    )
    heavy_volume_down = volume_ratio > 1.5 and pct_chg_today < 0
    high_position = trend_return_10 > 10
    risk_signals = [
        high_position and heavy_volume_down,           # 高位放量下跌
        long_upper_shadow,                             # 长上影线
        current_close < ma10,                          # 跌破10日均线
        current_close < ma20,                          # 跌破20日均线
        trend_return_20 > 25 and volume_ratio > 2.0,   # 涨幅过大且成交量异常放大
    ]
    risk_signal = sum(bool(s) for s in risk_signals) >= 2

    # --- 明日波动区间基础: 最近20天平均绝对涨跌幅 ---
    avg_abs_return = float(df["pct_chg"].tail(20).abs().mean())

    # --- 支撑/压力 ---
    support_price = float(df["low"].tail(10).min())
    pressure_price = float(df["high"].tail(20).max())

    return {
        "days": len(df),
        "enough_data": len(df) >= MIN_DAYS_FOR_FULL_MODEL,
        "current_close": current_close,
        "pct_chg_today": pct_chg_today,
        "trend_return_5": trend_return_5,
        "trend_return_10": trend_return_10,
        "trend_return_20": trend_return_20,
        "recent_high": recent_high,
        "drawdown": drawdown,
        "box_high": box_high,
        "box_low": box_low,
        "box_range": box_range,
        "vol_ma5": vol_ma5,
        "vol_ma20": vol_ma20,
        "volume_ratio": volume_ratio,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "breakout": breakout,
        "breakout_5": breakout_5,
        "breakout_10": breakout_10,
        "false_breakout": false_breakout,
        "long_upper_shadow": long_upper_shadow,
        "heavy_volume_down": heavy_volume_down,
        "risk_signal": risk_signal,
        "avg_abs_return": avg_abs_return,
        "support_price": support_price,
        "pressure_price": pressure_price,
    }
