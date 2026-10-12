from datetime import datetime
from pydantic import BaseModel

class SummaryStats(BaseModel):
    total_requests: int
    total_tokens: int
    prompt_tokens: int
    decision_tokens: int
    avg_latency_ms: float
    active_keys_count: int
    total_keys_count: int

class TimeSeriesPoint(BaseModel):
    date: str
    requests: int
    tokens: int
    avg_latency_ms: float

class DecisionTypeDistribution(BaseModel):
    choice: int
    noul: int
    score: int

class KeyUsageItem(BaseModel):
    key_id: int
    name: str
    key_prefix: str
    tokens_used: int
    token_limit: int
    percent_used: float
    requests_count: int
    is_active: bool

class UsageLogItem(BaseModel):
    id: int
    request_id: str
    key_id: int | None = None
    key_name: str | None = None
    key_prefix: str | None = None
    decision_types: str
    prompt_tokens: int
    decision_tokens: int
    total_tokens: int
    latency_ms: float
    status_code: int
    created_at: datetime

class AnalyticsDashboardData(BaseModel):
    summary: SummaryStats
    timeseries: list[TimeSeriesPoint]
    type_distribution: DecisionTypeDistribution
    key_usage: list[KeyUsageItem]
