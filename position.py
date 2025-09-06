from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

Direction = Literal["long", "short"]

@dataclass
class Position:
    symbol: str
    entry_ts: Optional[int]
    entry_price: float
    stop_price: float
    target_price: float
    qty: int
    direction: Direction
    open: bool = True
    max_favorable_excursion: float = 0.0
    r_value: float = 0.0  # risk per contract
