# SMT Signal Monitor

Read-only Python 3.11+ crypto market monitor. Confirms synchronized SMT pivots, then applies HTF trend, execution MSS, FVG, ATR bounds and a minimum estimated 2R target before sending a private-channel alert. It never submits orders and does not require exchange API keys. This strategy scaffold is not a validated profitable system.

## Directory structure

```text
smt-signal-bot/
├── config.py          # Pydantic environment settings
├── models.py          # Shared typed domain objects
├── data_feed.py       # Async CCXT, closed bars, caching and retries
├── smt_engine.py      # Confirmed pivots and SMT comparisons
├── safety_filter.py   # HTF/MSS/FVG/ATR/RRR confluence gates
├── notifier.py        # Telegram or Discord delivery
├── main.py            # Async monitor loop and cooldown
├── .env.example       # Starter configuration
└── requirements.txt
```

## Setup

1. Install Python 3.11+, create and activate a virtual environment.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`; use `DRY_RUN=true` first.
4. Run `python main.py` from this directory.
5. For Telegram, create a bot and add it to your private channel, then set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. For Discord, set a private channel `DISCORD_WEBHOOK_URL`. Set `DRY_RUN=false` only after verifying the destination.

No exchange credentials are used or needed. Never commit `.env`.

## Strategy and operational limits

- Only closed bars are analyzed. Execution candles are inner-joined on exact UTC open timestamp. Fractal pivots wait for `PIVOT_RIGHT` closed bars before confirmation.
- The latest two synchronized pivots define SMT. HTF alignment uses a rising/falling 20/50 EMA proxy. MSS requires a close through the latest confirmed opposing pivot. FVG is a simple three-candle imbalance check with price retracing into its bounds. ATR percent must fit configured limits.
- Stops are placed beyond the divergent asset swing with a small ATR buffer. Targets are mechanical 2R and 3R levels, not measured liquidity pools. Entry zone is indicative; price can move before delivery. No position sizing or order execution exists.
- Risk percentage is intentionally omitted from code since there is no order sizing. UTC quiet hours are operator-configured, not an exchange liquidity model. This scaffold does not account for fees, spread, funding, order book depth, or slippage. Backtest and paper trade before relying on alerts.

Modules keep exchange access, strategy, filtering and delivery separate for straightforward debugging. Increase `LOG_LEVEL=DEBUG` when extending behavior.
