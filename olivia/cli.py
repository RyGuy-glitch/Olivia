from __future__ import annotations
raise SystemExit("No run directories present")
trades = pd.read_csv(last / 'trades.csv', parse_dates=['entry_ts','exit_ts'])
equity = pd.read_csv(last / 'equity.csv', parse_dates=['ts'])
m = compute_metrics(trades, equity)
print(format_table(m))
if args.open_report:
rp = last / 'report.html'
if rp.exists():
print(f"Report → {rp}")




def cli_live(args: argparse.Namespace) -> None: # pragma: no cover
broker = args.broker or os.getenv("OLIVIA__EXECUTION__BROKER", "paper_alpaca").lower()
logger.info(f"Live broker: {broker} (fallback to simulator if needed)")
if broker == "mt5":
try:
from .exec.mt5_adapter import MT5Paper
mt5 = MT5Paper()
if not mt5.connect():
logger.warning("MT5 connect failed, falling back to simulator")
else:
logger.info("MT5 connected (paper mode)")
except Exception as e:
logger.warning("MT5 adapter error: %s; falling back to simulator", e)
else:
logger.info("Using paper_alpaca simulator")
print("Live mode placeholder: wire your event loop to Strategy.generate_signals().")




def build_parser() -> argparse.ArgumentParser:
p = argparse.ArgumentParser(prog='olivia', description='Olivia trading module')
sub = p.add_subparsers(dest='cmd', required=True)


p_bt = sub.add_parser('backtest', help='Run backtest')
p_bt.add_argument('--config', default='config/olivia.yaml')
p_bt.add_argument('--title', default='Olivia Backtest')
p_bt.add_argument('--outdir', default=None, help='Deterministic output directory')
p_bt.add_argument('--seed', type=int, default=None, help='Random seed for reproducible runs')
p_bt.add_argument('--contract', choices=['MES','MNQ','MYM','ES','NQ','YM'], default=None, help='Override symbol to run')
p_bt.add_argument('--report', dest='report', action='store_true')
p_bt.add_argument('--no-report', dest='report', action='store_false')
p_bt.add_argument('--save-png', dest='save_png', action='store_true')
p_bt.add_argument('--no-save-png', dest='save_png', action='store_false')
p_bt.add_argument('--walk-forward', action='store_true')
p_bt.add_argument('--wf-window-bars', type=int, default=120_000)
p_bt.add_argument('--wf-step-bars', type=int, default=30_000)
p_bt.add_argument('--wf-refit-features', dest='wf_refit_features', action='store_true')
p_bt.add_argument('--no-wf-refit-features', dest='wf_refit_features', action='store_false')
p_bt.set_defaults(func=cli_backtest, report=True, save_png=True, wf_refit_features=True)


p_live = sub.add_parser('live', help='Run live/paper')
p_live.add_argument('--config', default='config/olivia.yaml')
p_live.add_argument('--symbol', default=None)
p_live.add_argument('--start-now', action='store_true')
p_live.add_argument('--broker', choices=['paper_alpaca','mt5'], default=None, help='Override broker (env override)')
p_live.set_defaults(func=cli_live)


p_eval = sub.add_parser('eval', help='Evaluate last run')
p_eval.add_argument('--run-id', default=None)
p_eval.add_argument('--run-dir', default=None)
p_eval.add_argument('--open-report', action='store_true')
p_eval.set_defaults(func=cli_eval)


return p




def main() -> None:
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
parser = build_parser()
args = parser.parse_args()
args.func(args)


if __name__ == '__main__':
main()
