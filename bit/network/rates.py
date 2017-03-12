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
        rate = requests.get(cls.SINGLE_RATE + currency).json()['rate']
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
        rate = requests.get(cls.SINGLE_RATE.format(currency)).json()
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


class RatesApi:
    IGNORED_ERRORS = (requests.exceptions.ConnectionError,
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
    'usd': RatesApi.usd_to_satoshi,
    'eur': RatesApi.eur_to_satoshi,
    'gbp': RatesApi.gbp_to_satoshi,
    'jpy': RatesApi.jpy_to_satoshi,
    'cny': RatesApi.cny_to_satoshi,
    'cad': RatesApi.cad_to_satoshi,
    'aud': RatesApi.aud_to_satoshi,
    'nzd': RatesApi.nzd_to_satoshi,
    'rub': RatesApi.rub_to_satoshi,
    'brl': RatesApi.brl_to_satoshi,
    'chf': RatesApi.chf_to_satoshi,
    'sek': RatesApi.sek_to_satoshi,
    'dkk': RatesApi.dkk_to_satoshi,
    'isk': RatesApi.isk_to_satoshi,
    'pln': RatesApi.pln_to_satoshi,
    'hkd': RatesApi.hkd_to_satoshi,
    'krw': RatesApi.krw_to_satoshi,
    'sgd': RatesApi.sgd_to_satoshi,
    'thb': RatesApi.thb_to_satoshi,
    'twd': RatesApi.twd_to_satoshi,
    'clp': RatesApi.clp_to_satoshi
}


def currency_to_satoshi(amount, currency):
    satoshis = EXCHANGE_RATES[currency]()
    return int(satoshis * Decimal(amount))


class CachedRate:
    __slots__ = ('satoshis', 'last_update')

    def __init__(self, satoshis, last_update):
        self.satoshis = satoshis
        self.last_update = last_update


def currency_to_satoshi_local_cache(f):
    expiry_time = DEFAULT_CACHE_TIME
    start_time = time()

    cached_rates = dict([
        (currency, CachedRate(None, start_time)) for currency in EXCHANGE_RATES.keys()
    ])

    @wraps(f)
    def wrapper(amount, currency, expires=None):
        now = time()

        if expires is not None:
            nonlocal expiry_time
            expiry_time = expires

        cached_rate = cached_rates[currency]

        if not cached_rate.satoshis or now - cached_rate.last_update > expiry_time:
            cached_rate.satoshis = EXCHANGE_RATES[currency]()
            cached_rate.last_update = now

        return int(cached_rate.satoshis * Decimal(amount))

    return wrapper


@currency_to_satoshi_local_cache
def currency_to_satoshi_local_cached():
    pass  # pragma: no cover


def currency_to_satoshi_cached(*args, **kwargs):
    return currency_to_satoshi_local_cached(*args, **kwargs)


def satoshi_to_currency(amount, currency):
    return '{:f}'.format(
        Decimal(
            amount / Decimal(EXCHANGE_RATES[currency]())
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )


def satoshi_to_currency_cached(amount, currency):
    return '{:f}'.format(
        Decimal(
            amount / Decimal(currency_to_satoshi_cached(1, currency))
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )
