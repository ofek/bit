from functools import wraps
from time import time

import requests
from requests.exceptions import ConnectionError, Timeout

DEFAULT_FEE_FAST = 160
DEFAULT_FEE_HOUR = 120
DEFAULT_CACHE_TIME = 60 * 10
URL = 'https://bitcoinfees.21.co/api/v1/fees/recommended'


def set_fee_cache_time(seconds):
    global DEFAULT_CACHE_TIME
    DEFAULT_CACHE_TIME = seconds


def get_fee(fast=True):
    return requests.get(URL).json()['fastestFee' if fast else 'hourFee']


def get_fee_local_cache(f):
    expiry_time = DEFAULT_CACHE_TIME

    cached_fee_fast = None
    cached_fee_hour = None
    fast_last_update = time()
    hour_last_update = time()

    @wraps(f)
    def wrapper(fast=True, expires=None):
        now = time()

        if expires is not None:
            nonlocal expiry_time
            expiry_time = expires

        if fast:
            nonlocal cached_fee_fast
            nonlocal fast_last_update

            if not cached_fee_fast or now - fast_last_update > expiry_time:
                try:
                    cached_fee_fast = requests.get(URL).json()['fastestFee']
                    fast_last_update = now
                except (ConnectionError, Timeout):  # pragma: no cover
                    return cached_fee_fast or DEFAULT_FEE_FAST

            return cached_fee_fast

        else:
            nonlocal cached_fee_hour
            nonlocal hour_last_update

            if not cached_fee_hour or now - hour_last_update > expiry_time:
                try:
                    cached_fee_hour = requests.get(URL).json()['hourFee']
                    hour_last_update = now
                except (ConnectionError, Timeout):  # pragma: no cover
                    return cached_fee_hour or DEFAULT_FEE_HOUR

            return cached_fee_hour

    return wrapper


@get_fee_local_cache
def get_fee_local_cached():
    pass  # pragma: no cover


def get_fee_cached(*args, **kwargs):
    return get_fee_local_cached(*args, **kwargs)
