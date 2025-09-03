from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class UniverseCfg:
    symbols: List[str] = field(default_factory=lambda: ["MNQ"])
    session: str = "REGULAR"  # or EXT

@dataclass
class DataCfg:
    source: str = "csv"
    bar_interval: str = "1s"
    warmup_bars: int = 1200

@dataclass
class StrategyParams:
    fast_ema: int = 9
    slow_ema: int = 21
    vwap_confirm: bool = True
    r_mult_target: float = 1.2
    r_mult_stop: float = 1.0
    max_concurrent: int = 1
    cooldown_sec: int = 15

@dataclass
class StrategyCfg:
    name: str = "ema_vwap_scalp"
    params: StrategyParams = field(default_factory=StrategyParams)

@dataclass
class RiskCfg:
    per_trade_risk_pct: float = 0.25
    daily_loss_limit_pct: float = 2.0
    max_positions: int = 1
    hard_kill_on_loss_limit: bool = True

@dataclass
class ExecCfg:
    broker: str = "paper_alpaca"
    throttle_ms: int = 80
    slippage_bp: float = 1.5

@dataclass
class LoggingCfg:
    level: str = "INFO"
    outdir: str = "runs/olivia"

@dataclass
class BacktestCfg:
    commission_per_contract: float = 1.2
    start: Optional[str] = None
    end: Optional[str] = None

@dataclass
class OliviaConfig:
    universe: UniverseCfg = field(default_factory=UniverseCfg)
    data: DataCfg = field(default_factory=DataCfg)
    strategy: StrategyCfg = field(default_factory=StrategyCfg)
    risk: RiskCfg = field(default_factory=RiskCfg)
    execution: ExecCfg = field(default_factory=ExecCfg)
    logging: LoggingCfg = field(default_factory=LoggingCfg)
    backtest: BacktestCfg = field(default_factory=BacktestCfg)

    @staticmethod
    def from_yaml(path: str) -> "OliviaConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        raw = apply_env_overrides(raw, prefix="OLIVIA")
        return from_dict(raw)


def from_dict(d: Dict[str, Any]) -> OliviaConfig:
    def get(section: str, cls):
        sub = d.get(section, {}) or {}
        return cls(**{
            k: (v if not isinstance(getattr(cls, k, None), type) else getattr(cls, k)(**v))
            for k, v in sub.items()
        }) if sub else cls()

    return OliviaConfig(
        universe=get("universe", UniverseCfg),
        data=get("data", DataCfg),
        strategy=StrategyCfg(
            name=(d.get("strategy", {}) or {}).get("name", "ema_vwap_scalp"),
            params=StrategyParams(**(((d.get("strategy", {}) or {}).get("params", {})) or {})),
        ),
        risk=get("risk", RiskCfg),
        execution=get("execution", ExecCfg),
        logging=get("logging", LoggingCfg),
        backtest=get("backtest", BacktestCfg),
    )


def apply_env_overrides(cfg: Dict[str, Any], prefix: str = "OLIVIA") -> Dict[str, Any]:
    """Apply env vars like OLIVIA__RISK__MAX_DRAWDOWN_PCT=2.5 to nested dict."""
    out = dict(cfg)
    for key, val in os.environ.items():
        if not key.startswith(prefix + "__"):
            continue
        path = key[len(prefix + "__"):].lower().split("__")
        cursor: Any = out
        for part in path[:-1]:
            if part not in cursor or not isinstance(cursor[part], dict):
                cursor[part] = {}
            cursor = cursor[part]
        try:
            parsed: Any
            if val.lower() in {"true", "false"}:
                parsed = val.lower() == "true"
            else:
                parsed = float(val) if val.replace('.', '', 1).isdigit() else val
        except Exception:
            parsed = val
        cursor[path[-1]] = parsed
    return out
