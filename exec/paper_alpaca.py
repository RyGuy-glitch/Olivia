from __future__ import annotations
from typing import Optional


class PaperAlpaca:
def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, paper: bool = True, rng=None):
self.api_key = api_key
self.api_secret = api_secret
self.paper = paper
self.rng = rng
# Submit/cancel/positions/account would be implemented to mirror backtest fills.
