from time import sleep, time

import bit
from bit.network.fees import get_fee, get_fee_cached, set_fee_cache_time


def test_set_fee_cache_time():
    original = bit.network.fees.DEFAULT_CACHE_TIME
    set_fee_cache_time(30)
    updated = bit.network.fees.DEFAULT_CACHE_TIME

    assert original != updated
    assert updated == 30

    set_fee_cache_time(original)


def test_get_fee():
    assert get_fee(fast=True) >= get_fee(fast=False)


class TestFeeCache:
    def test_fast(self):
        sleep(0.2)

        start_time = time()
        set_fee_cache_time(0)
        get_fee_cached(fast=True)
        initial_time = time() - start_time

        start_time = time()
        set_fee_cache_time(600)
        get_fee_cached(fast=True)
        cached_time = time() - start_time

        assert initial_time > cached_time

    def test_hour(self):
        sleep(0.2)

        start_time = time()
        set_fee_cache_time(0)
        get_fee_cached(fast=False)
        initial_time = time() - start_time

        start_time = time()
        set_fee_cache_time(600)
        get_fee_cached(fast=False)
        cached_time = time() - start_time

        assert initial_time > cached_time

    def test_expires(self):
        sleep(0.2)

        set_fee_cache_time(0)
        get_fee_cached()

        start_time = time()
        set_fee_cache_time(600)
        get_fee_cached()
        cached_time = time() - start_time

        sleep(0.2)

        start_time = time()
        set_fee_cache_time(0.1)
        get_fee_cached()
        update_time = time() - start_time

        assert update_time > cached_time
