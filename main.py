import asyncio,logging
from datetime import datetime,timezone
from config import get_settings
from data_feed import DataFeed
from notifier import Notifier
from safety_filter import build_signal
from smt_engine import identify_smt
async def run():
 c=get_settings(); logging.basicConfig(level=c.log_level.upper(),format='%(asctime)s %(levelname)s %(name)s: %(message)s')
 feed=DataFeed(c); notifier=Notifier(c); sent={}
 try:
  while True:
   for pair in c.comparison_pairs:
    try:
     sa,sb=pair.split('|',1)
     a,b,h=await asyncio.gather(feed.fetch(sa,c.execution_timeframe),feed.fetch(sb,c.execution_timeframe),feed.fetch(sa,c.htf_timeframe))
     setup=identify_smt(sa,a,sb,b,c.pivot_left,c.pivot_right,c.swing_lookback)
     if not setup:continue
     execution=a if setup.symbol==sa else b
     higher=h if setup.symbol==sa else await feed.fetch(sb,c.htf_timeframe)
     signal=build_signal(setup,execution,higher,c)
     if not signal:continue
     now=datetime.now(timezone.utc); prev=sent.get(signal.dedupe_key)
     if prev and (now-prev).total_seconds()<c.cooldown_minutes*60:continue
     live_price=None
     try:
      t=await feed.exchange.fetch_ticker(signal.symbol); live_price=float(t['last'])
     except Exception:pass
     await notifier.send(signal,live_price);sent[signal.dedupe_key]=now
    except Exception:logging.getLogger(__name__).exception('Pair cycle failed: %s',pair)
   await asyncio.sleep(c.poll_seconds)
 finally:await feed.close()
if __name__=='__main__':
 try:asyncio.run(run())
 except KeyboardInterrupt:pass