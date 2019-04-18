from collections import OrderedDict
from decimal import ROUND_DOWN
from functools import wraps
from time import time

import requests

from bit.utils import Decimal

DEFAULT_CACHE_TIME = 60

# Constant for use in deriving exchange
# rates when given in terms of 1 BTC.
ONE = Decimal(1)

# https://en.bitcoin.it/wiki/Units
SATOSHI = 1
uBTC = 10 ** 2
mBTC = 10 ** 5
BTC = 10 ** 8

SUPPORTED_CURRENCIES = OrderedDict([
    ('satoshi', 'Satoshi'),
    ('ubtc', 'Microbitcoin'),
    ('mbtc', 'Millibitcoin'),
    ('btc', 'Bitcoin'),
    ('usd', 'United States Dollar'),
    ('eur', 'Eurozone Euro'),
    ('gbp', 'Pound Sterling'),
    ('jpy', 'Japanese Yen'),
    ('cny', 'Chinese Yuan'),
    ('cad', 'Canadian Dollar'),
    ('aud', 'Australian Dollar'),
    ('nzd', 'New Zealand Dollar'),
    ('rub', 'Russian Ruble'),
    ('brl', 'Brazilian Real'),
    ('chf', 'Swiss Franc'),
    ('sek', 'Swedish Krona'),
    ('dkk', 'Danish Krone'),
    ('isk', 'Icelandic Krona'),
    ('pln', 'Polish Zloty'),
    ('hkd', 'Hong Kong Dollar'),
    ('krw', 'South Korean Won'),
    ('sgd', 'Singapore Dollar'),
    ('thb', 'Thai Baht'),
    ('twd', 'New Taiwan Dollar'),
    ('clp', 'Chilean Peso')
])

# https://en.wikipedia.org/wiki/ISO_4217
CURRENCY_PRECISION = {
    'satoshi': 0,
    'ubtc': 2,
    'mbtc': 5,
    'btc': 8,
    'usd': 2,
    'eur': 2,
    'gbp': 2,
    'jpy': 0,
    'cny': 2,
    'cad': 2,
    'aud': 2,
    'nzd': 2,
    'rub': 2,
    'brl': 2,
    'chf': 2,
    'sek': 2,
    'dkk': 2,
    'isk': 2,
    'pln': 2,
    'hkd': 2,
    'krw': 0,
    'sgd': 2,
    'thb': 2,
    'twd': 2,
    'clp': 0
}


def set_rate_cache_time(seconds):
    global DEFAULT_CACHE_TIME
    DEFAULT_CACHE_TIME = seconds


def satoshi_to_satoshi():
    return SATOSHI


def ubtc_to_satoshi():
    return uBTC


def mbtc_to_satoshi():
    return mBTC


def btc_to_satoshi():
    return BTC


class BitpayRates:
    SINGLE_RATE = 'https://bitpay.com/api/rates/'

    @classmethod
    def currency_to_satoshi(cls, currency):
        r = requests.get(cls.SINGLE_RATE + currency)
        r.raise_for_status()
        rate = r.json()['rate']
        return int(ONE / Decimal(rate) * BTC)

    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('usd')

    @classmethod
    def eur_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('eur')

    @classmethod
    def gbp_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('gbp')

    @classmethod
    def jpy_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('jpy')

    @classmethod
    def cny_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('cny')

    @classmethod
    def hkd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('hkd')

    @classmethod
    def cad_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('cad')

    @classmethod
    def aud_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('aud')

    @classmethod
    def nzd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('nzd')

    @classmethod
    def rub_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('rub')

    @classmethod
    def brl_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('brl')

    @classmethod
    def chf_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('chf')

    @classmethod
    def sek_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('sek')

    @classmethod
    def dkk_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('dkk')

    @classmethod
    def isk_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('isk')

    @classmethod
    def pln_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('pln')

    @classmethod
    def krw_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('krw')

    @classmethod
    def clp_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('clp')

    @classmethod
    def sgd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('sgd')

    @classmethod
    def thb_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('thb')

    @classmethod
    def twd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('twd')


class BlockchainRates:
    SINGLE_RATE = 'https://blockchain.info/tobtc?currency={}&value=1'

    @classmethod
    def currency_to_satoshi(cls, currency):
        r = requests.get(cls.SINGLE_RATE.format(currency))
        r.raise_for_status()
        rate = r.text
        return int(Decimal(rate) * BTC)

    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('USD')

    @classmethod
    def eur_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('EUR')

    @classmethod
    def gbp_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('GBP')

    @classmethod
    def jpy_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('JPY')

    @classmethod
    def cny_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('CNY')

    @classmethod
    def hkd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('HKD')

    @classmethod
    def cad_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('CAD')

    @classmethod
    def aud_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('AUD')

    @classmethod
    def nzd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('NZD')

    @classmethod
    def rub_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('RUB')

    @classmethod
    def brl_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('BRL')

    @classmethod
    def chf_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('CHF')

    @classmethod
    def sek_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('SEK')

    @classmethod
    def dkk_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('DKK')

    @classmethod
    def isk_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('ISK')

    @classmethod
    def pln_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('PLN')

    @classmethod
    def krw_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('KRW')

    @classmethod
    def clp_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('CLP')

    @classmethod
    def sgd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('SGD')

    @classmethod
    def thb_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('THB')

    @classmethod
    def twd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('TWD')


class RatesAPI:
    """Each method converts exactly 1 unit of the currency to the equivalent
    number of satoshi.
    """
    IGNORED_ERRORS = (requests.exceptions.ConnectionError,
                      requests.exceptions.HTTPError,
                      requests.exceptions.Timeout)

    USD_RATES = [BitpayRates.usd_to_satoshi, BlockchainRates.usd_to_satoshi]
    EUR_RATES = [BitpayRates.eur_to_satoshi, BlockchainRates.eur_to_satoshi]
    GBP_RATES = [BitpayRates.gbp_to_satoshi, BlockchainRates.gbp_to_satoshi]
    JPY_RATES = [BitpayRates.jpy_to_satoshi, BlockchainRates.jpy_to_satoshi]
    CNY_RATES = [BitpayRates.cny_to_satoshi, BlockchainRates.cny_to_satoshi]
    HKD_RATES = [BitpayRates.hkd_to_satoshi, BlockchainRates.hkd_to_satoshi]
    CAD_RATES = [BitpayRates.cad_to_satoshi, BlockchainRates.cad_to_satoshi]
    AUD_RATES = [BitpayRates.aud_to_satoshi, BlockchainRates.aud_to_satoshi]
    NZD_RATES = [BitpayRates.nzd_to_satoshi, BlockchainRates.nzd_to_satoshi]
    RUB_RATES = [BitpayRates.rub_to_satoshi, BlockchainRates.rub_to_satoshi]
    BRL_RATES = [BitpayRates.brl_to_satoshi, BlockchainRates.brl_to_satoshi]
    CHF_RATES = [BitpayRates.chf_to_satoshi, BlockchainRates.chf_to_satoshi]
    SEK_RATES = [BitpayRates.sek_to_satoshi, BlockchainRates.sek_to_satoshi]
    DKK_RATES = [BitpayRates.dkk_to_satoshi, BlockchainRates.dkk_to_satoshi]
    ISK_RATES = [BitpayRates.isk_to_satoshi, BlockchainRates.isk_to_satoshi]
    PLN_RATES = [BitpayRates.pln_to_satoshi, BlockchainRates.pln_to_satoshi]
    KRW_RATES = [BitpayRates.krw_to_satoshi, BlockchainRates.krw_to_satoshi]
    CLP_RATES = [BitpayRates.clp_to_satoshi, BlockchainRates.clp_to_satoshi]
    SGD_RATES = [BitpayRates.sgd_to_satoshi, BlockchainRates.sgd_to_satoshi]
    THB_RATES = [BitpayRates.thb_to_satoshi, BlockchainRates.thb_to_satoshi]
    TWD_RATES = [BitpayRates.twd_to_satoshi, BlockchainRates.twd_to_satoshi]

    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.USD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def eur_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.EUR_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def gbp_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.GBP_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def jpy_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.JPY_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def cny_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CNY_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def hkd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.HKD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def cad_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CAD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def aud_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.AUD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def nzd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.NZD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def rub_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.RUB_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def brl_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.BRL_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def chf_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CHF_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def sek_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.SEK_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def dkk_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.DKK_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def isk_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.ISK_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def pln_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.PLN_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def krw_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.KRW_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def clp_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CLP_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def sgd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.SGD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def thb_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.THB_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def twd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.TWD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')


EXCHANGE_RATES = {
    'satoshi': satoshi_to_satoshi,
    'ubtc': ubtc_to_satoshi,
    'mbtc': mbtc_to_satoshi,
    'btc': btc_to_satoshi,
    'usd': RatesAPI.usd_to_satoshi,
    'eur': RatesAPI.eur_to_satoshi,
    'gbp': RatesAPI.gbp_to_satoshi,
    'jpy': RatesAPI.jpy_to_satoshi,
    'cny': RatesAPI.cny_to_satoshi,
    'cad': RatesAPI.cad_to_satoshi,
    'aud': RatesAPI.aud_to_satoshi,
    'nzd': RatesAPI.nzd_to_satoshi,
    'rub': RatesAPI.rub_to_satoshi,
    'brl': RatesAPI.brl_to_satoshi,
    'chf': RatesAPI.chf_to_satoshi,
    'sek': RatesAPI.sek_to_satoshi,
    'dkk': RatesAPI.dkk_to_satoshi,
    'isk': RatesAPI.isk_to_satoshi,
    'pln': RatesAPI.pln_to_satoshi,
    'hkd': RatesAPI.hkd_to_satoshi,
    'krw': RatesAPI.krw_to_satoshi,
    'sgd': RatesAPI.sgd_to_satoshi,
    'thb': RatesAPI.thb_to_satoshi,
    'twd': RatesAPI.twd_to_satoshi,
    'clp': RatesAPI.clp_to_satoshi
}


def currency_to_satoshi(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    satoshis = EXCHANGE_RATES[currency]()
    return int(satoshis * Decimal(amount))


class CachedRate:
    __slots__ = ('satoshis', 'last_update')

    def __init__(self, satoshis, last_update):
        self.satoshis = satoshis
        self.last_update = last_update


def currency_to_satoshi_local_cache(f):
    start_time = time()

    cached_rates = dict([
        (currency, CachedRate(None, start_time)) for currency in EXCHANGE_RATES.keys()
    ])

    @wraps(f)
    def wrapper(amount, currency):
        now = time()

        cached_rate = cached_rates[currency]

        if not cached_rate.satoshis or now - cached_rate.last_update > DEFAULT_CACHE_TIME:
            cached_rate.satoshis = EXCHANGE_RATES[currency]()
            cached_rate.last_update = now

        return int(cached_rate.satoshis * Decimal(amount))

    return wrapper


@currency_to_satoshi_local_cache
def currency_to_satoshi_local_cached():
    pass  # pragma: no cover


def currency_to_satoshi_cached(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`. Results are cached
    using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    return currency_to_satoshi_local_cached(amount, currency)


def satoshi_to_currency(num, currency):
    """Converts a given number of satoshi to another currency as a formatted
    string rounded down to the proper number of decimal places.

    :param num: The number of satoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(EXCHANGE_RATES[currency]())
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )


def satoshi_to_currency_cached(num, currency):
    """Converts a given number of satoshi to another currency as a formatted
    string rounded down to the proper number of decimal places. Results are
    cached using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param num: The number of satoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(currency_to_satoshi_cached(1, currency))
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )
