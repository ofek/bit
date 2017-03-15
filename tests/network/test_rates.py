from time import sleep, time

import bit
from bit.network.rates import (
    RatesAPI, btc_to_satoshi, currency_to_satoshi, currency_to_satoshi_cached,
    mbtc_to_satoshi, satoshi_to_currency, satoshi_to_currency_cached,
    satoshi_to_satoshi, set_rate_cache_time, ubtc_to_satoshi
)
from bit.utils import Decimal


def test_set_rate_cache_time():
    original = bit.network.rates.DEFAULT_CACHE_TIME
    set_rate_cache_time(30)
    updated = bit.network.rates.DEFAULT_CACHE_TIME

    assert original != updated
    assert updated == 30

    set_rate_cache_time(original)


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


def test_currency_to_satoshi():
    assert currency_to_satoshi(1, 'usd') > currency_to_satoshi(1, 'jpy')


class TestSatoshiToCurrency:
    def test_no_exponent(self):
        assert satoshi_to_currency(1, 'btc') == '0.00000001'

    def test_zero_places(self):
        assert Decimal(satoshi_to_currency(100000, 'jpy')).as_tuple().exponent == 0


def test_satoshi_to_currency_cached():
    assert satoshi_to_currency_cached(1, 'ubtc') == '0.01'


def test_rates_close():
    rates = sorted([
        api_call() for api_call in RatesAPI.USD_RATES
    ])
    assert rates[-1] - rates[0] < 2000


class TestRateCache:
    def test_cache(self):
        sleep(0.2)

        start_time = time()
        set_rate_cache_time(0)
        currency_to_satoshi_cached(1, 'usd')
        initial_time = time() - start_time

        start_time = time()
        set_rate_cache_time(60)
        currency_to_satoshi_cached(1, 'usd')
        cached_time = time() - start_time

        assert initial_time > cached_time

    def test_expires(self):
        sleep(0.2)

        set_rate_cache_time(0)
        currency_to_satoshi_cached(1, 'usd')

        start_time = time()
        set_rate_cache_time(60)
        currency_to_satoshi_cached(1, 'usd')
        cached_time = time() - start_time

        sleep(0.2)

        start_time = time()
        set_rate_cache_time(0.1)
        currency_to_satoshi_cached(1, 'usd')
        update_time = time() - start_time

        assert update_time > cached_time
