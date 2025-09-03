import pandas as pd
import numpy as np
from olivia.data.features import ema, atr, session_aware_vwap




def test_ema_basic():
s = pd.Series([1,2,3,4,5], dtype=float)
out = ema(s, span=2)
assert len(out) == len(s)
assert not out.isna().all()




def test_atr_nonnegative():
df = pd.DataFrame({
'high':[2,3,4], 'low':[1,1,2], 'close':[1.5,2.5,3.5]
})
a = atr(df, 2)
assert (a >= 0).all()




def test_session_vwap_not_nan_inside_regular():
idx = pd.date_range('2024-07-01 09:25', periods=20, freq='1min', tz='America/New_York').tz_convert(None)
df = pd.DataFrame({
'ts': idx, 'open': 1.0, 'high': 1.0, 'low': 1.0, 'close': 1.0, 'volume': 1
})
v = session_aware_vwap(df, 'REGULAR')
# After 09:30, values exist
assert v[ (pd.to_datetime(df['ts']).dt.hour > 9) | ((pd.to_datetime(df['ts']).dt.hour==9)&(pd.to_datetime(df['ts']).dt.minute>=30)) ].notna().any()
