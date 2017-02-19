from bit.network.rates import (
    satoshi_to_satoshi, ubtc_to_satoshi, mbtc_to_satoshi,
    btc_to_satoshi
)


def test_satoshi_to_satoshi():
    s = satoshi_to_satoshi()
    assert isinstance(s, int)
    assert s == 1


def test_ubtc_to_satoshi():
    s = ubtc_to_satoshi()
    assert isinstance(s, int)
    assert s == 100


def test_mbtc_to_satoshi():
    s = mbtc_to_satoshi()
    assert isinstance(s, int)
    assert s == 100000


def test_btc_to_satoshi():
    s = btc_to_satoshi()
    assert isinstance(s, int)
    assert s == 100000000
