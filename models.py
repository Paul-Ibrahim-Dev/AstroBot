from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
class Direction(StrEnum):
    BULLISH='bullish'
    BEARISH='bearish'
class Pivot(BaseModel):
    timestamp: datetime
    index: int
    price: float = Field(gt=0)
class Signal(BaseModel):
    model_config=ConfigDict(frozen=True)
    symbol: str
    comparison_symbol: str
    direction: Direction
    timeframe: str
    htf_timeframe: str
    detected_at: datetime
    first_swing: float
    second_swing: float
    entry_low: float
    entry_high: float
    invalidation: float
    target_one: float
    target_two: float
    rr: float=Field(ge=2)
    rationale: list[str]
    dedupe_key: str
