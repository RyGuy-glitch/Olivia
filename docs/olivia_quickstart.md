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
