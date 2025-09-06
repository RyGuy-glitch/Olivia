from __future__ import annotations




class MT5Paper:
"""Thin MT5/FTMO paper adapter.
- If MT5 is unavailable or connect fails, methods fall back to a no-op simulator.
"""


def __init__(self, creds: Optional[MT5Creds] = None) -> None:
self.creds = creds or self._from_env()
self._connected = False
# fallback sim state
self._sim_equity = 10000.0
self._sim_positions: list[Dict[str, Any]] = []


def _from_env(self) -> MT5Creds:
def getenv_i(k: str) -> Optional[int]:
v = os.getenv(k)
try:
return int(v) if v is not None and v.strip() != "" else None
except Exception:
return None
return MT5Creds(
login=getenv_i("OLIVIA__MT5__LOGIN"),
password=os.getenv("OLIVIA__MT5__PASSWORD"),
server=os.getenv("OLIVIA__MT5__SERVER"),
platform=os.getenv("OLIVIA__MT5__PLATFORM", "MT5"),
terminal_path=os.getenv("OLIVIA__MT5__TERMINAL_PATH"),
)


# --- Public API ---
def connect(self) -> bool:
if mt5 is None:
logger.warning("MT5 module not available; falling back to simulator")
self._connected = False
return False
if not self.creds.login or not self.creds.password or not self.creds.server:
logger.warning("MT5 creds missing; falling back to simulator")
self._connected = False
return False
try: # pragma: no cover - external dependency
if not mt5.initialize(self.creds.terminal_path or ""):
logger.warning("MT5 initialize() failed: %s", mt5.last_error() if hasattr(mt5, 'last_error') else "unknown")
self._connected = False
return False
authorized = mt5.login(self.creds.login, password=self.creds.password, server=self.creds.server)
if not authorized:
logger.warning("MT5 login failed; falling back to simulator")
self._connected = False
try:
mt5.shutdown()
except Exception:
pass
return False
self._connected = True
return True
except Exception as e: # pragma: no cover
logger.warning("MT5 connect exception: %s; falling back to simulator", e)
self._connected = False
try:
mt5.shutdown()
except Exception:
pass
return False


def ping(self) -> bool:
return bool(self._connected)


def submit_order(self, symbol: str, side: str, qty: int, type: str = "MKT") -> str:
# For CI and safety, we simulate even when connected (paper-only)
return f"MT5SIM-{symbol}-{side}-{qty}"


def positions(self) -> Iterable[Dict[str, Any]]:
if not self._connected:
return list(self._sim_positions)
# Keep simple for paper; real impl would query mt5.positions_get()
return list(self._sim_positions)


def account(self) -> Dict[str, Any]:
if not self._connected:
return {"equity": self._sim_equity, "buying_power": self._sim_equity}
return {"equity": self._sim_equity, "buying_power": self._sim_equity}
