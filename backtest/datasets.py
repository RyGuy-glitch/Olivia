from __future__ import annotations
import os
from pathlib import Path
import pandas as pd




def load_csv(symbol: str, interval: str, data_dir: str | Path) -> pd.DataFrame:
path = Path(data_dir) / f"{symbol}_{interval}.csv"
df = pd.read_csv(path)
df['ts'] = pd.to_datetime(df['ts'])
return df
