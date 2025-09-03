from __future__ import annotations
trades.append(
Trade(symbol=symbol, entry_ts=open_pos['ts'], exit_ts=ts, direction=side,
entry_price=entry, exit_price=exit_px, qty=open_pos['qty'], pnl=pnl,
r_multiple=(pnl_per / r_per_contract) if r_per_contract else 0.0)
)
open_pos = None
last_exit_ts = ts
continue


# Entry logic (cooldown)
if open_pos is None:
cooldown_ok = True
if last_exit_ts is not None:
cooldown_ok = (ts - last_exit_ts).total_seconds() >= cfg.strategy.params.cooldown_sec
if cooldown_ok and (row.long_entry or row.short_entry):
side = 'long' if row.long_entry else 'short'
entry_px = _slip(o, 'buy' if side == 'long' else 'sell', cfg.execution.slippage_bp)
stop_dist = cfg.strategy.params.r_mult_stop * row.atr
target_dist = cfg.strategy.params.r_mult_target * row.atr
if side == 'long':
stop_px = entry_px - stop_dist
target_px = entry_px + target_dist
else:
stop_px = entry_px + stop_dist
target_px = entry_px - target_dist
qty = sizer.calc_qty(entry_px, abs(entry_px - stop_px), equity, cfg.risk.per_trade_risk_pct, symbol)
if qty > 0:
open_pos = {
'ts': ts,
'entry': entry_px,
'stop': stop_px,
'target': target_px,
'qty': qty,
'side': side,
'mfe': 0.0,
}


# Equity curve from trades
if trades:
tr_df = pd.DataFrame([t.__dict__ for t in trades])
tr_df.sort_values('exit_ts', inplace=True)
else:
tr_df = pd.DataFrame(columns=["symbol","entry_ts","exit_ts","direction","entry_price","exit_price","qty","pnl","r_multiple"]) # noqa


eq = tr_df[['exit_ts','pnl']].copy()
if not eq.empty:
eq.rename(columns={'exit_ts': 'ts'}, inplace=True)
eq['equity'] = 10000.0 + eq['pnl'].cumsum()
else:
eq = pd.DataFrame({"ts": [], "equity": []})


trades_csv = outdir / 'trades.csv'
equity_csv = outdir / 'equity.csv'
tr_df.to_csv(trades_csv, index=False)
eq.to_csv(equity_csv, index=False)


if opts.save_png:
try:
from ..report import save_equity_png
png_path = save_equity_png(eq, outdir, title=opts.title)
logger.info("Equity PNG written to %s", png_path)
except Exception as e:
logger.warning("Failed to save equity PNG: %s", e)


if opts.report:
try:
from ..report import render_html_report
summary = {
"symbols": cfg.universe.symbols,
"bar_interval": cfg.data.bar_interval,
"session": cfg.universe.session,
"slippage_bp": cfg.execution.slippage_bp,
"commission_per_contract": cfg.backtest.commission_per_contract,
}
report_path = render_html_report(outdir, title=opts.title or "Olivia Backtest Report", summary=summary)
logger.info("Report written to %s", report_path)
except Exception as e:
logger.warning("Failed to render report: %s", e)


return outdir, tr_df, eq
