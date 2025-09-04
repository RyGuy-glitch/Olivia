from olivia.exec.mt5_adapter import MT5Paper, MT5Creds


def test_mt5_adapter_connect_fail_and_safe_methods():
# bogus creds should fail connect and not raise
creds = MT5Creds(login=0, password="x", server="FTMO-Demo")
mt5 = MT5Paper(creds)
ok = mt5.connect()
assert ok is False
# even when not connected, adapter should behave safely
assert isinstance(mt5.ping(), bool)
assert isinstance(mt5.account(), dict)
assert isinstance(list(mt5.positions()), list)
oid = mt5.submit_order("MNQ", "buy", 1)
assert isinstance(oid, str)
