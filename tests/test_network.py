import sys
import warnings
from decimal import Decimal

import requests
from requests.compat import json
from requests.exceptions import ConnectionError, Timeout

from bit.network import (
    BitpayAPI, BlockchainAPI, BlockexplorerAPI, BlockrAPI,
    MultiBackend, SmartbitAPI
)

MAIN_ADDRESS_USED1 = '1L2JsXHPMYuAa9ugvHGLwkdstCPUDemNCf'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'


def decorate_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


def catch_errors_raise_warnings(f):  # pragma: no cover
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except MultiBackend.IGNORED_ERRORS:
            warnings.warn('Unreachable API', Warning)
            assert True
    return wrapper


def all_items_common(seq):
    initial_set = set(seq[0])
    intersection_lengths = [len(set(s) & initial_set) for s in seq]
    return all_items_equal(intersection_lengths)


def all_items_equal(seq):
    initial_item = seq[0]
    return all(item == initial_item for item in seq if item is not None)


def throw_connection_error(address):
    return address, requests.get('https://jibber.ish', timeout=0.01)


class MockBackend(MultiBackend):
    IGNORED_ERRORS = (ConnectionError,
                      ValueError if sys.version_info < (3, 5)
                      else json.decoder.JSONDecodeError,
                      Timeout)
    GET_BALANCE_MAIN = [throw_connection_error]
    GET_BALANCES_MAIN = [throw_connection_error]
    GET_TX_LIST_MAIN = [throw_connection_error]
    GET_TX_LISTS_MAIN = [throw_connection_error]
    GET_UTXO_LIST_MAIN = [throw_connection_error]
    GET_UTXO_LISTS_MAIN = [throw_connection_error]
    GET_BALANCE_TEST = [throw_connection_error]
    GET_BALANCES_TEST = [throw_connection_error]
    GET_TX_LIST_TEST = [throw_connection_error]
    GET_TX_LISTS_TEST = [throw_connection_error]
    GET_UTXO_LIST_TEST = [throw_connection_error]
    GET_UTXO_LISTS_TEST = [throw_connection_error]


class TestMultiBackend:
    def test_get_balance_main_equal(self):
        results = [call(MAIN_ADDRESS_USED2) for call in MultiBackend.GET_BALANCE_MAIN]
        assert all(result == results[0] for result in results)

    def test_get_balance_main_failure(self):
        assert MockBackend.get_balance(MAIN_ADDRESS_USED2) is None

    def test_get_balance_test_equal(self):
        results = [call(TEST_ADDRESS_USED2) for call in MultiBackend.GET_BALANCE_TEST]
        assert all(result == results[0] for result in results)

    def test_get_balance_test_failure(self):
        assert MockBackend.get_test_balance(TEST_ADDRESS_USED2) is None

    def test_get_balances_main_equal(self):
        results = [call([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED])
                   for call in MultiBackend.GET_BALANCES_MAIN]
        assert all(result == results[0] for result in results)

    def test_get_balances_main_failure(self):
        assert MockBackend.get_balances([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED]) is None

    def test_get_balances_test_equal(self):
        results = [call([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
                   for call in MultiBackend.GET_BALANCES_TEST]
        assert all(result == results[0] for result in results)

    def test_get_balances_test_failure(self):
        assert MockBackend.get_test_balances([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED]) is None

    def test_get_tx_list_main_equal(self):
        results = [call(MAIN_ADDRESS_USED1)[:200] for call in MultiBackend.GET_TX_LIST_MAIN]
        assert all_items_common(results)

    def test_get_tx_list_main_failure(self):
        assert MockBackend.get_tx_list(MAIN_ADDRESS_USED1) is None

    def test_get_tx_list_test_equal(self):
        results = [call(TEST_ADDRESS_USED2)[:200] for call in MultiBackend.GET_TX_LIST_TEST]
        assert all_items_common(results)

    def test_get_tx_list_test_failure(self):
        assert MockBackend.get_test_tx_list(TEST_ADDRESS_USED2) is None

    def test_get_tx_lists_main_equal(self):
        results = [call([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
                   for call in MultiBackend.GET_TX_LISTS_MAIN]
        assert all_items_common([result[0][:200] for result in results])
        assert all_items_common([result[1][:200] for result in results])

    def test_get_tx_lists_main_failure(self):
        assert MockBackend.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED]) is None

    def test_get_tx_lists_test_equal(self):
        results = [call([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
                   for call in MultiBackend.GET_TX_LISTS_TEST]
        assert all_items_common([result[0][:200] for result in results])
        assert all_items_common([result[1][:200] for result in results])

    def test_get_tx_lists_test_failure(self):
        assert MockBackend.get_test_tx_lists([TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED]) is None

    def test_get_utxo_list_main_equal(self):
        results = [call(MAIN_ADDRESS_USED1) for call in MultiBackend.GET_UTXO_LIST_MAIN]
        assert all_items_equal(results)

    def test_get_utxo_list_main_failure(self):
        assert MockBackend.get_utxo_list(MAIN_ADDRESS_USED1) is None

    def test_get_utxo_list_test_equal(self):
        results = [call(TEST_ADDRESS_USED2) for call in MultiBackend.GET_UTXO_LIST_TEST]
        assert all_items_equal(results)

    def test_get_utxo_list_test_failure(self):
        assert MockBackend.get_test_utxo_list(TEST_ADDRESS_USED2) is None

    def test_get_utxo_lists_main_equal(self):
        results = [call([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
                   for call in MultiBackend.GET_UTXO_LISTS_MAIN]
        assert all_items_equal(results)
        assert all_items_equal(results)

    def test_get_utxo_lists_main_failure(self):
        assert MockBackend.get_utxo_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED]) is None

    def test_get_utxo_lists_test_equal(self):
        results = [call([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
                   for call in MultiBackend.GET_UTXO_LISTS_TEST]
        assert all_items_equal(results)
        assert all_items_equal(results)

    def test_get_utxo_lists_test_failure(self):
        assert MockBackend.get_test_utxo_lists([TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED]) is None


@decorate_methods(catch_errors_raise_warnings)
class TestBitpayAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BitpayAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_main_used(self):
        assert BitpayAPI.get_balance(MAIN_ADDRESS_USED1) > 0

    def test_get_balance_main_unused(self):
        assert BitpayAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BitpayAPI.get_test_balance(TEST_ADDRESS_USED1) > 0

    def test_get_balance_test_unused(self):
        assert BitpayAPI.get_test_balance(TEST_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BitpayAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances_main(self):
        balance1, balance2 = BitpayAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_balances_test(self):
        balance1, balance2 = BitpayAPI.get_test_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BitpayAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_main_used(self):
        assert len(BitpayAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 218

    def test_get_tx_list_main_unused(self):
        assert len(BitpayAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_list_test_used(self):
        assert len(BitpayAPI.get_test_tx_list(TEST_ADDRESS_USED2)) >= 444

    def test_get_tx_list_test_unused(self):
        assert len(BitpayAPI.get_test_tx_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BitpayAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists_main(self):
        txl1, txl2 = BitpayAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 218
        assert len(txl2) == 0

    def test_get_tx_lists_test_used(self):
        txl1, txl2 = BitpayAPI.get_test_tx_lists([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 444
        assert len(txl2) == 0

    def test_get_utxo_list_return_type(self):
        assert iter(BitpayAPI.get_utxo_list(MAIN_ADDRESS_USED1))

    def test_get_utxo_list_main_used(self):
        assert len(BitpayAPI.get_utxo_list(MAIN_ADDRESS_USED2)) >= 1

    def test_get_utxo_list_main_unused(self):
        assert len(BitpayAPI.get_utxo_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_utxo_list_test_used(self):
        assert len(BitpayAPI.get_test_utxo_list(TEST_ADDRESS_USED2)) >= 194

    def test_get_utxo_list_test_unused(self):
        assert len(BitpayAPI.get_test_utxo_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_utxo_lists_return_type(self):
        assert iter(BitpayAPI.get_utxo_lists([MAIN_ADDRESS_USED1]))

    def test_get_utxo_lists_main(self):
        txl1, txl2 = BitpayAPI.get_utxo_lists([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1
        assert len(txl2) == 0

    def test_get_utxo_lists_test_used(self):
        txl1, txl2 = BitpayAPI.get_test_utxo_lists([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 194
        assert len(txl2) == 0


@decorate_methods(catch_errors_raise_warnings)
class TestBlockexplorerAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockexplorerAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_used(self):
        assert BlockexplorerAPI.get_balance(MAIN_ADDRESS_USED1) > 0

    def test_get_balance_unused(self):
        assert BlockexplorerAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BlockexplorerAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances(self):
        balance1, balance2 = BlockexplorerAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BlockexplorerAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_used(self):
        assert len(BlockexplorerAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 218

    def test_get_tx_list_unused(self):
        assert len(BlockexplorerAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BlockexplorerAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists(self):
        txl1, txl2 = BlockexplorerAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 218
        assert len(txl2) == 0

    def test_get_utxo_list_return_type(self):
        assert iter(BlockexplorerAPI.get_utxo_list(MAIN_ADDRESS_USED1))

    def test_get_utxo_list_main_used(self):
        assert len(BlockexplorerAPI.get_utxo_list(MAIN_ADDRESS_USED2)) >= 1

    def test_get_utxo_list_main_unused(self):
        assert len(BlockexplorerAPI.get_utxo_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_utxo_lists_return_type(self):
        assert iter(BlockexplorerAPI.get_utxo_lists([MAIN_ADDRESS_USED1]))

    def test_get_utxo_lists_main(self):
        txl1, txl2 = BlockexplorerAPI.get_utxo_lists([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1
        assert len(txl2) == 0


@decorate_methods(catch_errors_raise_warnings)
class TestBlockrAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockrAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)
        assert isinstance(BlockrAPI.get_test_balance(TEST_ADDRESS_USED1), Decimal)

    def test_get_balance_main_used(self):
        assert BlockrAPI.get_balance(MAIN_ADDRESS_USED1) > 0

    def test_get_balance_main_unused(self):
        assert BlockrAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BlockrAPI.get_test_balance(TEST_ADDRESS_USED1) > 0

    def test_get_balance_test_unused(self):
        assert BlockrAPI.get_test_balance(TEST_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BlockrAPI.get_balances([
            MAIN_ADDRESS_USED1
        ]))
        assert all(isinstance(a, Decimal) for a in BlockrAPI.get_test_balances([
            TEST_ADDRESS_USED1
        ]))

    def test_get_balances_main(self):
        balance1, balance2 = BlockrAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_balances_test(self):
        balance1, balance2 = BlockrAPI.get_test_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BlockrAPI.get_tx_list(MAIN_ADDRESS_USED1))
        assert iter(BlockrAPI.get_test_tx_list(TEST_ADDRESS_USED1))

    def test_get_tx_list_main_used(self):
        assert len(BlockrAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 200

    def test_get_tx_list_main_unused(self):
        assert len(BlockrAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_list_test_used(self):
        assert len(BlockrAPI.get_test_tx_list(TEST_ADDRESS_USED1)) >= 200

    def test_get_tx_list_test_unused(self):
        assert len(BlockrAPI.get_test_tx_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BlockrAPI.get_tx_lists([MAIN_ADDRESS_USED1]))
        assert iter(BlockrAPI.get_test_tx_lists([TEST_ADDRESS_USED1]))

    def test_get_tx_lists_main(self):
        txl1, txl2 = BlockrAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 200
        assert len(txl2) == 0

    def test_get_tx_lists_test_used(self):
        txl1, txl2 = BlockrAPI.get_test_tx_lists([TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 200
        assert len(txl2) == 0

    def test_get_utxo_list_return_type(self):
        assert iter(BlockrAPI.get_utxo_list(MAIN_ADDRESS_USED1))

    def test_get_utxo_list_main_used(self):
        assert len(BlockrAPI.get_utxo_list(MAIN_ADDRESS_USED2)) >= 1

    def test_get_utxo_list_main_unused(self):
        assert len(BlockrAPI.get_utxo_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_utxo_list_test_used(self):
        assert len(BlockrAPI.get_test_utxo_list(TEST_ADDRESS_USED2)) >= 194

    def test_get_utxo_list_test_unused(self):
        assert len(BlockrAPI.get_test_utxo_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_utxo_lists_return_type(self):
        assert iter(BlockrAPI.get_utxo_lists([MAIN_ADDRESS_USED1]))
        assert iter(BlockrAPI.get_test_utxo_lists([TEST_ADDRESS_USED1]))

    def test_get_utxo_lists_main(self):
        txl1, txl2 = BlockrAPI.get_utxo_lists([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1
        assert len(txl2) == 0

    def test_get_utxo_lists_test_used(self):
        txl1, txl2 = BlockrAPI.get_test_utxo_lists([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 194
        assert len(txl2) == 0


@decorate_methods(catch_errors_raise_warnings)
class TestBlockchainAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockchainAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_used(self):
        assert BlockchainAPI.get_balance(MAIN_ADDRESS_USED1) > 0

    def test_get_balance_unused(self):
        assert BlockchainAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BlockchainAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances(self):
        balance1, balance2 = BlockchainAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BlockchainAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_used(self):
        assert len(BlockchainAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 218

    def test_get_tx_list_unused(self):
        assert len(BlockchainAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BlockchainAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists(self):
        txl1, txl2 = BlockchainAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 218
        assert len(txl2) == 0

    def test_get_utxo_list_return_type(self):
        assert iter(BlockchainAPI.get_utxo_list(MAIN_ADDRESS_USED1))

    def test_get_utxo_list_main_used(self):
        assert len(BlockchainAPI.get_utxo_list(MAIN_ADDRESS_USED2)) >= 1

    def test_get_utxo_list_main_unused(self):
        assert len(BlockchainAPI.get_utxo_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_utxo_lists_return_type(self):
        assert iter(BlockchainAPI.get_utxo_lists([MAIN_ADDRESS_USED1]))

    def test_get_utxo_lists_main(self):
        txl1, txl2 = BlockchainAPI.get_utxo_lists([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1
        assert len(txl2) == 0


@decorate_methods(catch_errors_raise_warnings)
class TestSmartbitAPI:
    def test_get_balance_return_type(self):
        assert isinstance(SmartbitAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_main_used(self):
        assert SmartbitAPI.get_balance(MAIN_ADDRESS_USED1) > 0

    def test_get_balance_main_unused(self):
        assert SmartbitAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert SmartbitAPI.get_test_balance(TEST_ADDRESS_USED1) > 0

    def test_get_balance_test_unused(self):
        assert SmartbitAPI.get_test_balance(TEST_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in SmartbitAPI.get_balances([
            MAIN_ADDRESS_USED1
        ]))
        assert all(isinstance(a, Decimal) for a in SmartbitAPI.get_test_balances([
            TEST_ADDRESS_USED1
        ]))

    def test_get_balances_main(self):
        balance1, balance2 = SmartbitAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_balances_test(self):
        balance1, balance2 = SmartbitAPI.get_test_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(SmartbitAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_main_used(self):
        assert len(SmartbitAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 218

    def test_get_tx_list_main_unused(self):
        assert len(SmartbitAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_list_test_used(self):
        assert len(SmartbitAPI.get_test_tx_list(TEST_ADDRESS_USED2)) >= 444

    def test_get_tx_list_test_unused(self):
        assert len(SmartbitAPI.get_test_tx_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(SmartbitAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists_main(self):
        txl1, txl2 = SmartbitAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 218
        assert len(txl2) == 0

    def test_get_tx_lists_test_used(self):
        txl1, txl2 = SmartbitAPI.get_test_tx_lists([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 444
        assert len(txl2) == 0

    def test_get_utxo_list_return_type(self):
        assert iter(SmartbitAPI.get_utxo_list(MAIN_ADDRESS_USED1))

    def test_get_utxo_list_main_used(self):
        assert len(SmartbitAPI.get_utxo_list(MAIN_ADDRESS_USED2)) >= 1

    def test_get_utxo_list_main_unused(self):
        assert len(SmartbitAPI.get_utxo_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_utxo_list_test_used(self):
        assert len(SmartbitAPI.get_test_utxo_list(TEST_ADDRESS_USED2)) >= 194

    def test_get_utxo_list_test_unused(self):
        assert len(SmartbitAPI.get_test_utxo_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_utxo_lists_return_type(self):
        assert iter(SmartbitAPI.get_utxo_lists([MAIN_ADDRESS_USED1]))

    def test_get_utxo_lists_main(self):
        txl1, txl2 = SmartbitAPI.get_utxo_lists([MAIN_ADDRESS_USED2, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1
        assert len(txl2) == 0

    def test_get_utxo_lists_test_used(self):
        txl1, txl2 = SmartbitAPI.get_test_utxo_lists([TEST_ADDRESS_USED2, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 194
        assert len(txl2) == 0
