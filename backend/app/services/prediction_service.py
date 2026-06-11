"""预测服务: 状态分类、评分模型、概率转换、涨跌幅区间与回测。

规则完全来自《股票台阶式上涨预测工具开发说明书》第 6~8、16 章。
"""

import pandas as pd

from app.services.feature_service import calculate_features

RISK_WARNING = (
    "本工具仅基于历史价格、成交量和技术指标进行统计分析，不构成任何投资建议。"
    "股票价格受政策、业绩、市场情绪、资金流、突发消息等多种因素影响，"
    "模型预测结果可能失效。用户应独立判断并自行承担投资风险。"
)

STATE_BREAKOUT = "突破阶段"
STATE_RISK = "风险阶段"
STATE_PULLBACK = "健康回调"
STATE_SIDEWAYS = "横盘整理"
STATE_UPTREND = "上涨阶段"
STATE_WATCH = "震荡观察"


# ---------------------------------------------------------------------------
# 6. 状态分类
# ---------------------------------------------------------------------------

def classify_state(f: dict) -> str:
    """按优先级判断当前所处阶段。"""
    if not f["enough_data"]:
        # 数据不足20天, 只做简单趋势判断
        if f["trend_return_5"] > 3:
            return STATE_UPTREND
        if f["trend_return_5"] < -3:
            return STATE_RISK
        return STATE_WATCH

    if f["breakout"]:
        return STATE_BREAKOUT

    if f["risk_signal"]:
        return STATE_RISK

    if (
        f["trend_return_10"] > 10
        and -8 <= f["drawdown"] <= -3
        and f["volume_ratio"] < 1.2
        and f["current_close"] > f["ma20"]
    ):
        return STATE_PULLBACK

    if (
        f["box_range"] < 6
        and f["volume_ratio"] < 1.0
        and abs(f["current_close"] - f["ma5"]) / f["ma5"] * 100 < 3
    ):
        return STATE_SIDEWAYS

    if (
        f["trend_return_5"] > 6
        and f["current_close"] > f["ma5"]
        and f["current_close"] > f["ma10"]
    ):
        return STATE_UPTREND

    return STATE_WATCH


# ---------------------------------------------------------------------------
# 7. 评分模型
# ---------------------------------------------------------------------------

def calculate_score(f: dict, state: str) -> int:
    score = 0

    # --- 趋势分 ---
    if f["trend_return_5"] > 5:
        score += 15
    if f["trend_return_10"] > 10:
        score += 15
    score += 10 if f["current_close"] > f["ma5"] else -10
    score += 10 if f["current_close"] > f["ma10"] else -10

    # --- 回调分 ---
    if -8 <= f["drawdown"] <= -3 and f["volume_ratio"] < 1.2:
        score += 15  # 健康回调且缩量
    if f["drawdown"] < -12:
        score -= 20  # 回调过深
    if f["trend_return_10"] > 15 and f["drawdown"] > -1:
        score -= 10  # 高位无回调连续上涨

    # --- 成交量分 ---
    if f["volume_ratio"] > 1.5 and f["pct_chg_today"] > 0:
        score += 15  # 上涨放量
    if state == STATE_SIDEWAYS and f["volume_ratio"] < 0.8:
        score += 10  # 横盘缩量
    if f["pct_chg_today"] < 0 and f["volume_ratio"] < 0.7:
        score += 8   # 下跌缩量
    if f["volume_ratio"] > 1.5 and f["pct_chg_today"] < 0:
        score -= 20  # 下跌放量

    # --- 突破分 ---
    if f["breakout_10"]:
        score += 30
    elif f["breakout_5"]:
        score += 20
    if f["false_breakout"]:
        score -= 25

    # --- 风险分 ---
    if f["long_upper_shadow"]:
        score -= 15
    if f["trend_return_10"] > 10 and f["volume_ratio"] > 1.5 and f["pct_chg_today"] < 0:
        score -= 30  # 高位放量阴线
    if f["current_close"] < f["ma20"]:
        score -= 25  # 跌破20日均线

    if state == STATE_RISK:
        score -= 30

    return max(-100, min(100, score))


def score_to_probability(score: int) -> tuple[float, float]:
    up = 50 + score * 0.35
    up = max(10.0, min(90.0, up))
    return round(up, 2), round(100 - up, 2)


# ---------------------------------------------------------------------------
# 8. 涨跌幅区间预测
# ---------------------------------------------------------------------------

_RANGE_FACTORS = {
    STATE_UPTREND: (1.2, 0.8),
    STATE_PULLBACK: (0.8, 1.2),
    STATE_SIDEWAYS: (0.7, 0.7),
    STATE_BREAKOUT: (1.5, 1.0),
    STATE_RISK: (0.6, 1.5),
}


def estimate_range(avg_abs_return: float, state: str) -> dict:
    up_factor, down_factor = _RANGE_FACTORS.get(state, (1.0, 1.0))
    up = avg_abs_return * up_factor
    down = avg_abs_return * down_factor
    return {
        "expected_up_range": f"0% ~ {up:.2f}%",
        "expected_down_range": f"0% ~ -{down:.2f}%",
    }


# ---------------------------------------------------------------------------
# 解释生成
# ---------------------------------------------------------------------------

def build_explanation(f: dict, state: str, score: int) -> list[str]:
    notes: list[str] = []

    if not f["enough_data"]:
        notes.append(
            f"当前仅有 {f['days']} 个交易日数据(不足20天), 只做简单趋势判断, 结论可靠性较低"
        )

    # 趋势
    if f["trend_return_10"] > 15:
        notes.append(f"最近10日累计上涨 {f['trend_return_10']:.1f}%, 短期趋势强劲, 但追高风险增加")
    elif f["trend_return_10"] > 10:
        notes.append(f"最近10日累计上涨 {f['trend_return_10']:.1f}%, 说明短期趋势较强")
    elif f["trend_return_10"] < -8:
        notes.append(f"最近10日累计下跌 {abs(f['trend_return_10']):.1f}%, 短期趋势偏弱")

    # 回调
    if -8 <= f["drawdown"] <= -3:
        notes.append(f"距离近期高点回调 {abs(f['drawdown']):.1f}%, 属于健康整理区间")
    elif f["drawdown"] < -15:
        notes.append(f"距离近期高点回调已达 {abs(f['drawdown']):.1f}%, 上涨趋势可能被破坏")
    elif f["drawdown"] < -8:
        notes.append(f"距离近期高点回调 {abs(f['drawdown']):.1f}%, 属于深度回调, 需观察是否止跌")

    # 横盘
    if f["box_range"] < 5:
        notes.append(f"最近5日箱体振幅仅 {f['box_range']:.1f}%, 处于窄幅横盘, 等待方向选择")

    # 量能
    if f["volume_ratio"] > 1.5 and f["pct_chg_today"] > 0:
        notes.append("今日上涨且明显放量, 资金参与度较高")
    elif f["volume_ratio"] > 1.5 and f["pct_chg_today"] < 0:
        notes.append("今日下跌且放量, 存在主动抛压, 需要警惕")
    elif f["volume_ratio"] < 0.7:
        notes.append("成交量明显萎缩, 说明抛压暂时不大, 但上攻动能也不足")

    # 均线
    if f["current_close"] > f["ma5"] and f["current_close"] > f["ma10"]:
        notes.append("当前价格站上5日和10日均线, 短期多头排列")
    elif f["current_close"] < f["ma20"]:
        notes.append("当前价格跌破20日均线, 中期趋势转弱")

    # 突破
    if f["breakout_10"]:
        notes.append("收盘价突破最近10日高点, 若量能持续则可能开启新一轮上涨")
    elif f["breakout_5"]:
        notes.append("收盘价突破最近5日高点, 注意确认是否为有效突破")
    elif f["false_breakout"]:
        notes.append("昨日突破后今日回落, 疑似假突破, 短期需防回调")
    elif state in (STATE_SIDEWAYS, STATE_PULLBACK):
        notes.append("尚未突破最近高点, 因此不能判断为新一轮上涨")

    # 风险
    if f["long_upper_shadow"]:
        notes.append("今日K线留有长上影线, 上方抛压较重")

    notes.append(f"综合评分 {score} 分(满分±100), 当前判定为「{state}」")
    return notes


# ---------------------------------------------------------------------------
# 主分析入口
# ---------------------------------------------------------------------------

def analyze(df: pd.DataFrame) -> dict:
    """对一段日K数据做完整分析, 返回结果字典(不含股票元信息)。"""
    f = calculate_features(df)
    state = classify_state(f)
    score = calculate_score(f, state)
    up_prob, down_prob = score_to_probability(score)
    ranges = estimate_range(f["avg_abs_return"], state)

    return {
        "current_price": round(f["current_close"], 2),
        "today_pct_chg": round(f["pct_chg_today"], 2),
        "current_state": state,
        "score": score,
        "up_probability": up_prob,
        "down_probability": down_prob,
        **ranges,
        "support_price": round(f["support_price"], 2),
        "pressure_price": round(f["pressure_price"], 2),
        "explanation": build_explanation(f, state, score),
        "risk_warning": RISK_WARNING,
    }


# ---------------------------------------------------------------------------
# 16. 回测
# ---------------------------------------------------------------------------

def backtest(df: pd.DataFrame, window_days: int = 30) -> dict:
    """滚动回测: 用前 window_days 天预测下一天涨跌, 统计准确率。

    df 应包含 window_days + 测试天数 的完整指标数据。
    """
    cases = []
    for i in range(window_days, len(df)):
        history = df.iloc[:i]
        actual = df["pct_chg"].iloc[i]
        if pd.isna(actual):
            continue
        f = calculate_features(history)
        state = classify_state(f)
        score = calculate_score(f, state)
        up_prob, _ = score_to_probability(score)
        predicted_up = up_prob >= 50
        actual_up = actual > 0
        cases.append(
            {
                "date": str(df["date"].iloc[i]),
                "predicted": "上涨" if predicted_up else "下跌",
                "up_probability": up_prob,
                "actual_pct_chg": round(float(actual), 2),
                "correct": predicted_up == actual_up,
            }
        )

    total = len(cases)
    correct = sum(c["correct"] for c in cases)
    wrong_cases = [c for c in cases if not c["correct"]]
    # 最大错误案例: 预测方向与实际涨跌幅偏离最大的几次
    worst = sorted(wrong_cases, key=lambda c: -abs(c["actual_pct_chg"]))[:5]

    return {
        "total": total,
        "correct": correct,
        "wrong": total - correct,
        "accuracy": round(correct / total * 100, 2) if total else 0.0,
        "avg_predicted_up_probability": round(
            sum(c["up_probability"] for c in cases) / total, 2
        )
        if total
        else 0.0,
        "avg_actual_pct_chg": round(
            sum(c["actual_pct_chg"] for c in cases) / total, 2
        )
        if total
        else 0.0,
        "worst_cases": worst,
        "risk_warning": RISK_WARNING,
    }
