# Olivia Quickstart


## Data
- Place CSV files under `data/` (or set `OLIVIA_DATA_DIR`).
- Filename pattern: `{SYMBOL}_{INTERVAL}.csv`, e.g., `MNQ_1s.csv`.
- Columns: `ts,open,high,low,close,volume` (UTC or local consistently).


## Contracts
- Micros: MES (0.25 tick / $1.25), MNQ (0.25 / $0.50), MYM (1.0 / $0.50)
- Minis: ES (0.25 / $12.50), NQ (0.25 / $5), YM (1.0 / $5)
- Sizing: qty based on ticks at stop and $ risk per contract.


## Run Backtest
```bash
olivia backtest --config config/olivia.yaml --title "MNQ scalp test" --outdir runs/ci-smoke --save-png --report

## Live (Paper / MT5)
- To try MT5/FTMO paper adapter:
```bash
olivia live --config config/olivia.yaml --broker mt5 --symbol MNQ --start-now

---


## Makefile
```make
.PHONY: live-mt5 smoke-ci clean-ci eval


live-mt5:
@echo "Running live MT5 (paper) ..."
OLIVIA_DATA_DIR=data olivia live --config config/olivia.yaml --broker mt5 --symbol MNQ --start-now --seed 42


smoke-ci:
@echo "Running CI smoke test..."
mkdir -p data
python - <<'PY'
import pandas as pd, numpy as np
idx = pd.date_range('2024-06-03 09:30:00', periods=3600, freq='1s', tz='America/New_York').tz_convert(None)
base = 10000 + np.cumsum(np.random.default_rng(0).normal(0, 0.4, len(idx)))
df = pd.DataFrame({
'ts': idx,
'open': base,
'high': base + 0.5,
'low': base - 0.5,
'close': base + np.random.default_rng(1).normal(0, 0.2, len(idx)),
'volume': np.random.default_rng(2).integers(1, 10, len(idx))
})
df.to_csv('data/MNQ_1s.csv', index=False)
PY
OLIVIA_DATA_DIR=data \
olivia backtest \
--config config/olivia.yaml \
--title "CI-local" \
--outdir runs/ci-smoke \
--seed 42 \
--save-png --report
@echo "Artifacts in runs/ci-smoke (trades.csv, equity.csv, report.html, equity*.png)"


clean-ci:
@echo "Cleaning CI artifacts and sample data..."
rm -rf runs/ci-smoke
rm -f data/MNQ_1s.csv
@echo "Cleaned."


eval:
@echo "Evaluating run in runs/ci-smoke..."
olivia eval --run-dir runs/ci-smoke --open-report
