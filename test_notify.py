import asyncio
from datetime import datetime, timezone
from config import get_settings
from models import Signal, Direction
from notifier import Notifier

async def main():
    c = get_settings()
    notifier = Notifier(c)
    dummy = Signal(
        symbol="BTC/USDT:USDT",
        comparison_symbol="JTO/USDT:USDT",
        direction=Direction.BULLISH,
        timeframe=c.execution_timeframe,
        htf_timeframe=c.htf_timeframe,
        detected_at=datetime.now(timezone.utc),
        first_swing=100.0,
        second_swing=95.0,
        entry_low=98.0,
        entry_high=99.0,
        invalidation=94.0,
        target_one=102.0,
        target_two=104.0,
        rr=2,
        rationale=["TEST — verifying Telegram delivery, not a real signal"],
        dedupe_key="test-signal-001"
    )
    await notifier.send(dummy, live_price=98.73)
    print("Done — check Telegram (or your terminal if DRY_RUN is still true).")

asyncio.run(main())