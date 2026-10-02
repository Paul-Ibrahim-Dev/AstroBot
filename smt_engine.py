from dataclasses import dataclass
import pandas as pd
from models import Direction, Pivot
@dataclass(frozen=True)
class SMTSetup:
    direction: Direction
    symbol: str
    comparison_symbol: str
    first_a: Pivot
    second_a: Pivot
    first_b: Pivot
    second_b: Pivot

def pivots(frame:pd.DataFrame,kind:str,left:int=3,right:int=3)->list[Pivot]:
    """Confirmed fractals; right-hand closed bars are required."""
    col={'high':'high','low':'low'}.get(kind)
    if col is None: raise ValueError("kind must be high or low")
    vals=frame[col].to_numpy(); out=[]
    for i in range(left,len(frame)-right):
        before=vals[i-left:i]; after=vals[i+1:i+right+1]
        ok=(vals[i]>max(before) and vals[i]>=max(after)) if kind=='high' else (vals[i]<min(before) and vals[i]<=min(after))
        if ok: out.append(Pivot(timestamp=frame.iloc[i].timestamp.to_pydatetime(),index=i,price=float(vals[i])))
    return out

def identify_smt(sa:str,a:pd.DataFrame,sb:str,b:pd.DataFrame,left:int=3,right:int=3,lookback:int=80)->SMTSetup|None:
    """Inner-align bars; return the latest synchronized divergence, if any."""
    x=a.merge(b,on='timestamp',suffixes=('_a','_b')).tail(lookback+left+right+5).reset_index(drop=True)
    if len(x)<20:return None
    def side(suffix): return x.rename(columns={f'{c}_{suffix}':c for c in ('open','high','low','close','volume')})
    aa,bb=side('a'),side('b')
    def paired(kind):
        pa=pivots(aa,kind,left,right); pb={p.index:p for p in pivots(bb,kind,left,right)}
        return [(u,pb[u.index]) for u in pa if u.index in pb]
    lows=paired('low')
    if len(lows)>=2:
        (a1,b1),(a2,b2)=lows[-2:]
        if a2.price<a1.price and b2.price>=b1.price:return SMTSetup(Direction.BULLISH,sa,sb,a1,a2,b1,b2)
        if b2.price<b1.price and a2.price>=a1.price:return SMTSetup(Direction.BULLISH,sb,sa,b1,b2,a1,a2)
    highs=paired('high')
    if len(highs)>=2:
        (a1,b1),(a2,b2)=highs[-2:]
        if a2.price>a1.price and b2.price<=b1.price:return SMTSetup(Direction.BEARISH,sa,sb,a1,a2,b1,b2)
        if b2.price>b1.price and a2.price<=a1.price:return SMTSetup(Direction.BEARISH,sb,sa,b1,b2,a1,a2)
    return None
