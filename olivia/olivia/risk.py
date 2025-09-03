from __future__ import annotations
from dataclasses import dataclass
from math import ceil
from typing import Iterable, Dict
import numpy as np
import logging


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ContractSpec:
    tick_size: float
    tick_value: float
    point_value: float


# Micros (preferred)
CONTRACT_SPECS: Dict[str, ContractSpec] = {
    "MES": ContractSpec(tick_size=0.25, tick_value=1.25, point_value=5.00),
    "MNQ": ContractSpec(tick_size=0.25, tick_value=0.50, point_value=2.00),
    "MYM": ContractSpec(tick_size=1.00, tick_value=0.50, point_value=0.50),
    # Minis
    "ES": ContractSpec(tick_size=0.25, tick_value=12.50, point_value=50.0),
    "NQ": ContractSpec(tick_size=0.25, tick_value=5.00, point_value=20.0),
    "YM": ContractSpec(tick_size=1.00, tick_value=5.00, point_value=5.0),
}


def get_spec(symbol: str) -> ContractSpec:
    """Return contract spec for symbol or raise a clear error if missing."""
    try:
        return CONTRACT_SPECS[symbol.upper()]
    except KeyError as e:
        raise KeyError(f"No CONTRACT_SPECS for symbol '{symbol}'. Add it to CONTRACT_SPECS.") from e


class PositionSizer:
    def __init__(self, contract_specs: Dict[str, ContractSpec] | None = None) -> None:
        self.specs = contract_specs or CONTRACT_SPECS

    def spec_for(self, symbol: str) -> ContractSpec:
        if symbol.upper() in self.specs:
            return self.specs[symbol.upper()]
        # fall back to global helper for consistent error
        return get_spec(symbol)

    def calc_qty(self, price: float, stop_distance: float, equity: float, per_trade_risk_pct: float, symbol: str = "MNQ") -> int:
        """Return integer qty sized by percent equity at risk.
        - stop_distance is in **points**. We convert to ticks and then dollar risk per contract.
        - per_trade_risk_pct is a percent (e.g., 0.25 means 0.25%).
        - Clamp to at least 1 contract if there is any positive budget.
        """
        spec = self.spec_for(symbol)
        ticks = max(1, int(ceil(abs(stop_distance) / spec.tick_size)))
        risk_per_contract = ticks * spec.tick_value
        budget = equity * (per_trade_risk_pct / 100.0)
        if risk_per_contract <= 0 or budget <= 0:
            return 0
        qty = max(1, int(budget // risk_per_contract))
        logger.info("risk $%.2f per contract → qty %d at equity $%.0f", risk_per_contract, qty, equity)
        return qty


class RiskGuard:
    def check_daily_limits(self, pnl_series: Iterable[float], daily_loss_limit_pct: float, starting_equity: float = 10000.0) -> bool:
        """True if trading allowed. Stops if drawdown from start exceeds limit."""
        pnl = np.array(list(pnl_series), dtype=float)
        equity = starting_equity + np.cumsum(pnl)
        if equity.size == 0:
            return True
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / peak
        max_dd_pct = float(dd.max() * 100.0)
        return max_dd_pct <= daily_loss_limit_pct
