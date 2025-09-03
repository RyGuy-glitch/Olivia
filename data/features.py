from __future__ import annotations
def ensure_ts(df: pd.DataFrame) -> pd.DataFrame:
if 'ts' not in df.columns:
raise ValueError("DataFrame must contain 'ts'")
out = df.copy()
out['ts'] = pd.to_datetime(out['ts'])
if out['ts'].dt.tz is None:
out['ts'] = out['ts'].dt.tz_localize(NY)
else:
out['ts'] = out['ts'].dt.tz_convert(NY)
return out




def ema(series: pd.Series, span: int) -> pd.Series:
return series.ewm(span=span, adjust=False).mean()




def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
h, l, c = df['high'], df['low'], df['close']
prev_c = c.shift(1)
tr = pd.concat([(h - l).abs(), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
return tr.rolling(window=period, min_periods=1).mean()




def _session_mask(ts: pd.Series, session: str) -> pd.Series:
hour = ts.dt.hour
minute = ts.dt.minute
if session.upper() == "REGULAR":
# 09:30–16:00 ET
start = (hour == 9) & (minute >= 30)
during = (hour > 9) & (hour < 16)
end = (hour == 16)
return start | during | end
elif session.upper() == "EXT":
# EXT here: 17:00–18:00 gap; main session 18:00–17:00 next day
return pd.Series(True, index=ts.index)
else:
return pd.Series(True, index=ts.index)




def session_aware_vwap(df: pd.DataFrame, session: str = "REGULAR") -> pd.Series:
d = ensure_ts(df)
ts = d['ts']
price = d['close']
vol = d['volume']


# Identify session starts
mask = _session_mask(ts, session)
# For REGULAR, reset at first bar >= 09:30 each day
if session.upper() == "REGULAR":
is_start = ((ts.dt.hour == 9) & (ts.dt.minute == 30))
else:
# EXT: reset at 18:00
is_start = ((ts.dt.hour == 18) & (ts.dt.minute == 0))


# New session flag when day changes and first bar condition is met
session_key = ts.dt.date.astype(str)
start_flags = is_start


# Build a group id that increments at each start flag
grp = start_flags.cumsum()


pv = (price * vol)
c_pv = pv.groupby(grp).cumsum()
c_v = vol.groupby(grp).cumsum()


vwap = c_pv / c_v
vwap[~mask] = np.nan
return vwap
