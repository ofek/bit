from functools import wraps
from time import time

import requests
from requests.exceptions import ConnectionError, Timeout

DEFAULT_FEE_FAST = 220
DEFAULT_FEE_HOUR = 160
DEFAULT_CACHE_TIME = 60 * 10
URL = 'https://bitcoinfees.21.co/api/v1/fees/recommended'


def set_fee_cache_time(seconds):
    global DEFAULT_CACHE_TIME
    DEFAULT_CACHE_TIME = seconds


def get_fee(fast=True):
    """Gets the recommended satoshi per byte fee.

    :param fast: If ``True``, the fee returned will be "The lowest fee (in
                 satoshis per byte) that will currently result in the fastest
                 transaction confirmations (usually 0 to 1 block delay)".
                 Otherwise, the number returned will be "The lowest fee (in
                 satoshis per byte) that will confirm transactions within an
                 hour (with 90% probability)".
    :type fast: ``bool``
    :rtype: ``int``
    """
    return requests.get(URL).json()['fastestFee' if fast else 'hourFee']


def get_fee_local_cache(f):

    cached_fee_fast = None
    cached_fee_hour = None
    fast_last_update = time()
    hour_last_update = time()

    @wraps(f)
    def wrapper(fast=True):
        now = time()

        if fast:
            nonlocal cached_fee_fast
            nonlocal fast_last_update

            if not cached_fee_fast or now - fast_last_update > DEFAULT_CACHE_TIME:
                try:
                    cached_fee_fast = requests.get(URL).json()['fastestFee']
                    fast_last_update = now
                except (ConnectionError, Timeout):  # pragma: no cover
                    return cached_fee_fast or DEFAULT_FEE_FAST

            return cached_fee_fast

        else:
            nonlocal cached_fee_hour
            nonlocal hour_last_update

            if not cached_fee_hour or now - hour_last_update > DEFAULT_CACHE_TIME:
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


def get_fee_cached(fast=True):
    """Gets the recommended satoshi per byte fee. Results are cached using a
    decorator for 10 minutes by default. See :ref:`cache times`.

    :param fast: If ``True``, the fee returned will be "The lowest fee (in
                 satoshis per byte) that will currently result in the fastest
                 transaction confirmations (usually 0 to 1 block delay)".
                 Otherwise, the number returned will be "The lowest fee (in
                 satoshis per byte) that will confirm transactions within an
                 hour (with 90% probability)".
    :type fast: ``bool``
    :rtype: ``int``
    """
    return get_fee_local_cached(fast)
