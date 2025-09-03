from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import numpy as np
from ..data.features import ema, atr, session_aware_vwap




@dataclass
class EMAVWAPScalpParams:
fast_ema: int = 9
slow_ema: int = 21
vwap_confirm: bool = True
r_mult_target: float = 1.2
r_mult_stop: float = 1.0
max_concurrent: int = 1
cooldown_sec: int = 15




class EMAVWAPScalpStrategy:
def __init__(self, params: EMAVWAPScalpParams, session: str = "REGULAR") -> None:
self.p = params
self.session = session


def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
d = df.copy()
d['ts'] = pd.to_datetime(d['ts'])
d['ema_fast'] = ema(d['close'], self.p.fast_ema)
d['ema_slow'] = ema(d['close'], self.p.slow_ema)
d['vwap'] = session_aware_vwap(d, session=self.session)
d['atr'] = atr(d, 14)


# Cross above/below VWAP within last 3 bars
above = d['close'] >= d['vwap']
below_prev = d['close'].shift(1) < d['vwap'].shift(1)
crossed_up = above & below_prev
crossed_dn = (~above) & (~below_prev) & (d['close'] < d['vwap']) & (d['close'].shift(1) >= d['vwap'].shift(1))
recent_up = crossed_up.rolling(3, min_periods=1).max().astype(bool)
recent_dn = crossed_dn.rolling(3, min_periods=1).max().astype(bool)


# Pullback to EMA_fast within 0.25 ATR
pull_long = (d['close'] - d['ema_fast']).abs() <= (0.25 * d['atr'])
pull_short = (d['close'] - d['ema_fast']).abs() <= (0.25 * d['atr'])


trend_up = d['ema_fast'] > d['ema_slow']
trend_dn = d['ema_fast'] < d['ema_slow']


long_entry = trend_up & recent_up & pull_long
short_entry = trend_dn & recent_dn & pull_short


out = d[['ts','open','high','low','close','volume','ema_fast','ema_slow','vwap','atr']].copy()
out['long_entry'] = long_entry.fillna(False)
out['short_entry'] = short_entry.fillna(False)
return out


def on_bar(self, bar: dict) -> None: # placeholder for live wiring
pass
