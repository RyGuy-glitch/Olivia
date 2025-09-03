from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import numpy as np
from tabulate import tabulate


@dataclass
class Metrics:
cagr: float
sharpe: float
sortino: float
max_dd: float
avg_trade: float
win_rate: float
exposure_pct: float
profit_factor: float




def calc_drawdown_series(equity_df: pd.DataFrame) -> pd.Series:
if equity_df.empty:
return pd.Series(dtype=float)
eq = equity_df.set_index('ts')['equity'].astype(float)
peak = eq.cummax()
dd = (eq - peak) / peak
return dd




def compute_metrics(trades: pd.DataFrame, equity: pd.DataFrame) -> Metrics:
if equity.empty:
return Metrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
eq = equity.copy()
eq['ts'] = pd.to_datetime(eq['ts'])
eq = eq.set_index('ts').sort_index()
ret = eq['equity'].pct_change().fillna(0.0)
daily = ret.resample('1D').sum().fillna(0.0)
ann = np.sqrt(252)
sharpe = (daily.mean() / (daily.std() + 1e-12)) * np.sqrt(252) if daily.std() > 0 else 0.0
neg = daily[daily < 0]
sortino = (daily.mean() / (neg.std() + 1e-12)) * np.sqrt(252) if neg.std() > 0 else 0.0
dd = calc_drawdown_series(equity)
max_dd = float(-dd.min()) if not dd.empty else 0.0


if trades.empty:
avg_trade = 0.0
win_rate = 0.0
profit_factor = 0.0
else:
pnl = trades['pnl']
avg_trade = float(pnl.mean())
wins = pnl[pnl > 0].sum()
losses = -pnl[pnl < 0].sum()
profit_factor = float(wins / losses) if losses > 0 else float('inf') if wins > 0 else 0.0
win_rate = float((pnl > 0).mean())


# Simple CAGR (if multi-day)
days = max(1, (eq.index.max() - eq.index.min()).days)
total_ret = eq['equity'].iloc[-1] / eq['equity'].iloc[0] - 1.0 if len(eq) > 1 else 0.0
cagr = (1.0 + total_ret) ** (365.0 / days) - 1.0 if days > 1 else total_ret


exposure_pct = 0.0 # placeholder without per-bar position tracking
return Metrics(cagr, float(sharpe), float(sortino), max_dd, avg_trade, win_rate, exposure_pct, float(profit_factor))




def format_table(m: Metrics) -> str:
rows = [
("CAGR", f"{m.cagr*100:.2f}%"),
("Sharpe (daily)", f"{m.sharpe:.2f}"),
("Sortino", f"{m.sortino:.2f}"),
("Max DD", f"{m.max_dd*100:.2f}%"),
("Profit Factor", f"{m.profit_factor:.2f}"),
("Win Rate", f"{m.win_rate*100:.2f}%"),
("Avg Trade", f"{m.avg_trade:.2f}"),
("Exposure", f"{m.exposure_pct*100:.1f}%"),
]
return tabulate(rows, headers=["Metric", "Value"], tablefmt="github")
