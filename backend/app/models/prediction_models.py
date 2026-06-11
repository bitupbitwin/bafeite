"""预测与回测相关数据模型。"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    code: str
    period_days: int = Field(default=30, ge=5, le=250)


class AnalyzeResponse(BaseModel):
    stock: dict
    period: str
    is_mock: bool = False
    current_price: float
    today_pct_chg: float
    current_state: str
    score: int
    up_probability: float
    down_probability: float
    expected_up_range: str
    expected_down_range: str
    support_price: float
    pressure_price: float
    explanation: list[str]
    risk_warning: str


class BacktestRequest(BaseModel):
    code: str
    window_days: int = Field(default=30, ge=20, le=120)
    test_days: int = Field(default=60, ge=10, le=250)


class BacktestCase(BaseModel):
    date: str
    predicted: str
    up_probability: float
    actual_pct_chg: float
    correct: bool


class BacktestResponse(BaseModel):
    stock: dict
    is_mock: bool = False
    total: int
    correct: int
    wrong: int
    accuracy: float
    avg_predicted_up_probability: float
    avg_actual_pct_chg: float
    worst_cases: list[BacktestCase]
    risk_warning: str
