"""日期工具函数。"""

from datetime import date, timedelta


def estimate_start_date(trading_days: int, end: date | None = None) -> date:
    """根据需要的交易日数量, 估算应该从哪个自然日开始取数据。

    A 股一周约 5 个交易日, 按 1.6 倍自然日再加 20 天缓冲, 保证取够。
    """
    end = end or date.today()
    calendar_days = int(trading_days * 1.6) + 20
    return end - timedelta(days=calendar_days)


def fmt_yyyymmdd(d: date) -> str:
    return d.strftime("%Y%m%d")
