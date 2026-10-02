import asyncio, logging, time
from typing import Any
import ccxt.async_support as ccxt
import pandas as pd
from config import Settings
log=logging.getLogger(__name__)
class DataFeed:
    """Read-only async CCXT market data with cached closed candles and retry."""
    def __init__(self, settings: Settings):
        cls=getattr(ccxt, settings.exchange_id, None)
        if cls is None: raise ValueError(f'Unknown exchange {settings.exchange_id}')
        self.exchange: Any=cls({'enableRateLimit':True})
        self.limit=settings.ohlcv_limit
        self.cache={}
        self.lock=asyncio.Lock()
    async def close(self): await self.exchange.close()
    async def fetch(self,symbol:str,timeframe:str)->pd.DataFrame:
        key=(symbol,timeframe); old=self.cache.get(key)
        if old and time.monotonic()-old[0]<5: return old[1].copy()
        async with self.lock:
            for attempt in range(6):
                try:
                    rows=await self.exchange.fetch_ohlcv(symbol,timeframe,limit=self.limit)
                    f=pd.DataFrame(rows,columns=['timestamp','open','high','low','close','volume'])
                    f['timestamp']=pd.to_datetime(f.timestamp,unit='ms',utc=True)
                    f=f.drop_duplicates('timestamp').sort_values('timestamp').reset_index(drop=True)
                    if len(f)>1: f=f.iloc[:-1].copy()
                    self.cache[key]=(time.monotonic(),f)
                    return f.copy()
                except (ccxt.NetworkError,ccxt.ExchangeNotAvailable,ccxt.RateLimitExceeded) as e:
                    wait=min(30,.75*2**attempt); log.warning('retry %s %s %s',symbol,timeframe,e); await asyncio.sleep(wait)
            raise RuntimeError(f'Unable to fetch {symbol} {timeframe}')
