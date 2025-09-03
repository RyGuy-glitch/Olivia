This is an additive module named **Olivia**. It avoids touching existing packages unless your repo already exposes a CLI hub; in that case, wire `olivia.cli:main` into the hub.

Recon (from GitHub repo):
- Repo: `RyGuy-glitch/Olivia` – **flat layout of Python scripts**, no `src/` package, no `pyproject.toml`/`setup.cfg`, no tests folder detected. Files include `adaptive_risk_v043.py`, `angela_override_v043.py`, `autonomous_simulation.py`, `config_surface_v043.py`, `correlation_filters_v043.py`, `dashboard_complete_v043.html`, `init_database.py`, `strategy_hibernation_v043.py` (and others).
- Package name: none (scripts only). We'll add namespaced package `olivia/` to avoid collisions.
- Dependency manager: none detected → default to pip/uv. Minimal deps added in CI step.
- Test runner: none detected → add `pytest`.
- Data/execution adapters: none formalized; Olivia ships its own under `olivia.data` and `olivia.exec`.

Entrypoints:
- Console script: `olivia` → `olivia.cli:main`. Since no existing CLI hub detected, we add a `[project.scripts]` entry.

Live trading wiring:
- Paper only by default. If `ALPACA_KEY_ID`/`ALPACA_SECRET_KEY` present and `ALPACA_PAPER=1`, `PaperAlpaca` will use Alpaca; otherwise, it falls back to an in‑process simulator aligned with backtest fills.

Configs:
- Default config at `config/olivia.yaml`. Environment overrides via `OLIVIA__SECTION__KEY=value`.

Assumptions kept least‑invasive:
- Backtest operates per symbol; multi‑symbol can be looped externally.
- Futures contract point value defaults to 1 unless a mapping is provided.
- VWAP session boundary uses calendar date (midnight) as a session split; refine as needed.

If repo expectations differ, adjust imports and CLI registration accordingly and keep everything namespaced under `olivia/`.
- Backtest operates per symbol; multi‑symbol can be looped externally.
- Futures contract point value defaults to 1 unless a mapping is provided.
- VWAP session boundary uses calendar date (midnight) as a session split; refine as needed.

If repo expectations differ, adjust imports and CLI registration accordingly and keep everything namespaced under `olivia/`.
