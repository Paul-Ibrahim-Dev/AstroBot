from datetime import datetime,timezone
import pandas as pd
from config import Settings
from models import Direction,Signal
from smt_engine import SMTSetup,pivots

def atr(f:pd.DataFrame,n:int)->float:
    prev=f.close.shift(1); tr=pd.concat([f.high-f.low,(f.high-prev).abs(),(f.low-prev).abs()],axis=1).max(axis=1)
    return float(tr.rolling(n).mean().iloc[-1])
def bias(f:pd.DataFrame)->Direction|None:
    if len(f)<55:return None
    c=f.close; fast=c.ewm(span=20,adjust=False).mean(); slow=c.ewm(span=50,adjust=False).mean()
    if fast.iloc[-1]>slow.iloc[-1] and slow.iloc[-1]>slow.iloc[-4]:return Direction.BULLISH
    if fast.iloc[-1]<slow.iloc[-1] and slow.iloc[-1]<slow.iloc[-4]:return Direction.BEARISH
    return None
def mss(f,d,left,right):
    ps=pivots(f,'high' if d==Direction.BULLISH else 'low',left,right)
    return bool(ps) and (float(f.close.iloc[-1])>ps[-1].price if d==Direction.BULLISH else float(f.close.iloc[-1])<ps[-1].price)
def fvg(f,d):
    if len(f)<3:return False
    a,z=f.iloc[-3],f.iloc[-1]; price=float(z.close)
    return (a.high<z.low and a.high<=price<=z.low) if d==Direction.BULLISH else (a.low>z.high and z.high<=price<=a.low)
def build_signal(s:SMTSetup,e:pd.DataFrame,h:pd.DataFrame,c:Settings)->Signal|None:
    if e.empty or datetime.now(timezone.utc).hour in c.avoid_utc_hours or bias(h)!=s.direction or not mss(e,s.direction,c.pivot_left,c.pivot_right) or not fvg(e,s.direction):return None
    price=float(e.close.iloc[-1]); vol=atr(e,c.atr_period)
    if not vol or pd.isna(vol):return None
    pct=vol/price*100
    if not c.min_atr_pct<=pct<=c.max_atr_pct:return None
    stop=s.second_a.price-vol*.15 if s.direction==Direction.BULLISH else s.second_a.price+vol*.15
    risk=price-stop if s.direction==Direction.BULLISH else stop-price
    if risk<=0:return None
    t1=price+(2*risk if s.direction==Direction.BULLISH else -2*risk); t2=price+(3*risk if s.direction==Direction.BULLISH else -3*risk)
    stamp=s.second_a.timestamp.isoformat()
    return Signal(symbol=s.symbol,comparison_symbol=s.comparison_symbol,direction=s.direction,timeframe=c.execution_timeframe,htf_timeframe=c.htf_timeframe,detected_at=datetime.now(timezone.utc),first_swing=s.first_a.price,second_swing=s.second_a.price,entry_low=price-vol*.1 if s.direction==Direction.BULLISH else price-vol*.1,entry_high=price+vol*.1, invalidation=stop,target_one=t1,target_two=t2,rr=2,rationale=['Synchronized SMT','HTF trend aligned','MSS confirmed','FVG condition','ATR in range'],dedupe_key=f'{s.symbol}:{s.direction}:{stamp}')
