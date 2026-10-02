from functools import lru_cache
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    exchange_id: str = 'binance'
    monitored_pairs: list[str] = Field(default_factory=lambda: ['BTC/USDT','ETH/USDT'])
    comparison_pairs: list[str] = Field(default_factory=lambda: ['BTC/USDT:USDT|ETH/USDT:USDT'])
    execution_timeframe: str = '15m'
    htf_timeframe: str = '1h'
    ohlcv_limit: int = Field(default=500, ge=100, le=1500)
    poll_seconds: int = Field(default=20, ge=5)
    pivot_left: int = Field(default=3, ge=1, le=10)
    pivot_right: int = Field(default=3, ge=1, le=10)
    atr_period: int = Field(default=14, ge=5)
    min_atr_pct: float = Field(default=.10, ge=0)
    max_atr_pct: float = Field(default=4, gt=0)
    min_rr: float = Field(default=2, ge=2)
    swing_lookback: int = Field(default=80, ge=20)
    cooldown_minutes: int = Field(default=90, ge=1)
    avoid_utc_hours: list[int] = Field(default_factory=list)
    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None
    discord_webhook_url: SecretStr | None = None
    dry_run: bool = True
    log_level: str = 'INFO'
    @model_validator(mode='after')
    def valid(self):
        if self.min_atr_pct >= self.max_atr_pct: raise ValueError('MIN_ATR_PCT must be below MAX_ATR_PCT')
        if any(h not in range(24) for h in self.avoid_utc_hours): raise ValueError('UTC hours must be 0..23')
        if not self.dry_run and not ((self.telegram_bot_token and self.telegram_chat_id) or self.discord_webhook_url): raise ValueError('Live notifications require a destination')
        return self

@lru_cache
def get_settings() -> Settings: return Settings()