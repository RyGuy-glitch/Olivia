from olivia.risk import PositionSizer




def test_qty_sizing_mnq():
sizer = PositionSizer()
# stop distance 5 points on MNQ, equity 10k, frorisk 1%
qty = sizer.calc_qty(price=16000, stop_distance=5.0, equity=10_000, per_trade_risk_pct=1.0, symbol='MNQ')
assert qty >= 1
