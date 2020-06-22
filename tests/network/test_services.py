import pytest
import requests
import json
import unittest
import requests_mock

import bit
from bit.network.services import (
    RPCHost,
    RPCMethod,
    NetworkAPI,
    BitcoreAPI,
    BlockchainAPI,
    SmartbitAPI,
    BlockstreamAPI,
    BlockchairAPI,
    set_service_timeout,
)
from tests.utils import (
    catch_errors_raise_warnings,
    decorate_methods,
    raise_connection_error,
    check_not_all_raise_errors,
)

from bit.transaction import calc_txid

MAIN_ADDRESS_USED1 = '1L2JsXHPMYuAa9ugvHGLwkdstCPUDemNCf'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_USED3 = '1CounterpartyXXXXXXXXXXXXXXXUWLpVr'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_USED3 = 'mpnrLMH4m4e6dS8Go84P1r2hWwTiFTXmtW'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'

MAIN_TX_VALID = '6e05c708d88cc5bf0f1533938c969de2cc48f438b0ae28ce89fefbaa1938185a'
TEST_TX_VALID = 'ff2b4641481f1ee553ba2c9f02f413a86f70240c35b5aee554f84e3efee93292'
TX_INVALID = 'ff2b4641481f1ee553ba2c9f02f413a86f70240c35b5aee554f84e3efee93290'

set_service_timeout(30)


def all_items_common(seq):
    initial_set = set(seq[0])
    intersection_lengths = [len(set(s) & initial_set) for s in seq]
    return all_items_equal(intersection_lengths)


def all_items_equal(seq):
    initial_item = seq[0]
    return all(item == initial_item for item in seq if item is not None)


def both_rpchosts_equal(host1, host2):
    return host1._url == host2._url and host1._headers == host2._headers


def test_set_service_timeout():
    original = bit.network.services.DEFAULT_TIMEOUT
    set_service_timeout(3)
    updated = bit.network.services.DEFAULT_TIMEOUT

    assert original != updated
    assert updated == 3

    set_service_timeout(original)


class MockBackend(NetworkAPI):
    IGNORED_ERRORS = NetworkAPI.IGNORED_ERRORS
    GET_BALANCE_MAIN = [raise_connection_error]
    GET_TRANSACTIONS_MAIN = [raise_connection_error]
    GET_TRANSACTION_BY_ID_MAIN = [raise_connection_error]
    GET_UNSPENT_MAIN = [raise_connection_error]
    GET_BALANCE_TEST = [raise_connection_error]
    GET_TRANSACTIONS_TEST = [raise_connection_error]
    GET_TRANSACTION_BY_ID_TEST = [raise_connection_error]
    GET_UNSPENT_TEST = [raise_connection_error]


class MockRPCHost(RPCHost):
    def __getattr__(self, rpc_method):
        return MockRPCMethod(rpc_method, None)


class MockRPCMethod(RPCMethod):
    def __call__(self, *args):
        if self._rpc_method == "getreceivedbyaddress":
            assert (
                args[0] == MAIN_ADDRESS_USED1
                or args[0] == TEST_ADDRESS_USED2
                or args[0] == MAIN_ADDRESS_UNUSED
                or args[0] == TEST_ADDRESS_UNUSED
            )
            assert args[1] == 0

            if args[0] in (MAIN_ADDRESS_USED1, TEST_ADDRESS_USED2):
                return 1.23456789
            return 0

        if self._rpc_method == "listreceivedbyaddress":
            assert args[0] == 0
            assert args[1] is True
            assert args[2] is True
            assert (
                args[3] == MAIN_ADDRESS_USED1
                or args[3] == TEST_ADDRESS_USED2
                or args[3] == MAIN_ADDRESS_UNUSED
                or args[3] == TEST_ADDRESS_UNUSED
            )

            if args[3] == MAIN_ADDRESS_USED1:
                return [
                    {
                        "involvesWatchonly": True,
                        "address": "1L2JsXHPMYuAa9ugvHGLwkdstCPUDemNCf",
                        "amount": 1.23456789,
                        "confirmations": 0,
                        "label": "",
                        "txids": [
                            "381f1605dd927151fbfac2e88608464414fa5b01bd6298cd1e2d9d991907aa9e",
                            "6e05c708d88cc5bf0f1533938c969de2cc48f438b0ae28ce89fefbaa1938185a",
                        ],
                    }
                ]
            elif args[3] == TEST_ADDRESS_USED2:
                return [
                    {
                        "involvesWatchonly": True,
                        "address": "mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5",
                        "amount": 1.23456789,
                        "confirmations": 0,
                        "label": "",
                        "txids": [
                            "ff2b4641481f1ee553ba2c9f02f413a86f70240c35b5aee554f84e3efee93292",
                            "ef9bd3ac4eacc60a16117eaca0631bbef673eb8a71084de4b9ada3317f7895e9",
                            "ff2b4641481f1ee553ba2c9f02f413a86f70240c35b5aee554f84e3efee93290",
                        ],
                    }
                ]
            return []

        if self._rpc_method == "getrawtransaction":
            assert args[0] == MAIN_TX_VALID or args[0] == TEST_TX_VALID
            assert args[1] is False
            return True

        if self._rpc_method == "listunspent":
            assert args[0] == 0
            assert args[1] == 9999999
            assert (
                args[2] == [MAIN_ADDRESS_USED1]
                or args[2] == [TEST_ADDRESS_USED2]
                or args[2] == [MAIN_ADDRESS_UNUSED]
                or args[2] == [TEST_ADDRESS_UNUSED]
            )

            if args[2][0] in (MAIN_ADDRESS_UNUSED, TEST_ADDRESS_UNUSED):
                return []
            return [
                {
                    "txid": "381f1605dd927151fbfac2e88608464414fa5b01bd6298cd1e2d9d991907aa9e",
                    "vout": 0,
                    "address": MAIN_ADDRESS_USED1,
                    "label": "",
                    "scriptPubKey": "a9142df37714a79eacad089a41481a6a3e400d39a54687",
                    "amount": 1.23456789,
                    "confirmations": 0,
                    "spendable": False,
                    "solvable": False,
                    "safe": True,
                },
                {
                    "txid": "ef9bd3ac4eacc60a16117eaca0631bbef673eb8a71084de4b9ada3317f7895e9",
                    "vout": 1,
                    "address": MAIN_ADDRESS_USED1,
                    "label": "",
                    "scriptPubKey": "a9142df37714a79eacad089a41481a6a3e400d39a54687",
                    "amount": 1.23456789,
                    "confirmations": 0,
                    "spendable": False,
                    "solvable": False,
                    "safe": True,
                },
            ]

        if self._rpc_method == "sendrawtransaction":
            assert args[0] == "01000000000000000000" or args[0] == "00000000000000000000"

            if args[0] == "00000000000000000000":
                raise bit.exceptions.BitcoinNodeException()

            return ""

        raise AttributeError('called unsupported RPC method %s', self._rpc_method)  # pragma: no cover


class TestNetworkAPI:
    def test_get_balance_main_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_BALANCE_MAIN, NetworkAPI.IGNORED_ERRORS)(MAIN_ADDRESS_USED2)
        assert all(result == results[0] for result in results)

    def test_get_balance_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_balance(MAIN_ADDRESS_USED2)

    def test_get_balance_test_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_BALANCE_TEST, NetworkAPI.IGNORED_ERRORS)(TEST_ADDRESS_USED2)
        assert all(result == results[0] for result in results)

    def test_get_balance_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_balance_testnet(TEST_ADDRESS_USED2)

    def test_get_transactions_main_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_TRANSACTIONS_MAIN, NetworkAPI.IGNORED_ERRORS)(
            MAIN_ADDRESS_USED1
        )
        assert all_items_common([r[:100] for r in results])

    def test_get_transactions_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_transactions(MAIN_ADDRESS_USED1)

    def test_get_transactions_test_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_TRANSACTIONS_TEST, NetworkAPI.IGNORED_ERRORS)(
            TEST_ADDRESS_USED2
        )
        assert all_items_common([r[:100] for r in results])

    def test_get_transactions_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_transactions_testnet(TEST_ADDRESS_USED2)

    def test_get_transaction_by_id_main_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_TRANSACTION_BY_ID_MAIN, NetworkAPI.IGNORED_ERRORS)(
            MAIN_TX_VALID
        )
        assert all_items_equal([calc_txid(r) for r in results])

    def test_get_transaction_by_id_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_transaction_by_id(MAIN_TX_VALID)

    def test_get_transaction_by_id_test_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_TRANSACTION_BY_ID_TEST, NetworkAPI.IGNORED_ERRORS)(
            TEST_TX_VALID
        )
        assert all_items_equal([calc_txid(r) for r in results])

    def test_get_transaction_by_id_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_transaction_by_id_testnet(TEST_TX_VALID)

    def test_get_unspent_main_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_UNSPENT_MAIN, NetworkAPI.IGNORED_ERRORS)(MAIN_ADDRESS_USED2)
        assert all_items_equal(results)

    def test_get_unspent_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_unspent(MAIN_ADDRESS_USED1)

    def test_get_unspent_test_equal(self):
        results = check_not_all_raise_errors(NetworkAPI.GET_UNSPENT_TEST, NetworkAPI.IGNORED_ERRORS)(TEST_ADDRESS_USED3)
        assert all_items_equal(results)

    def test_get_unspent_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_unspent_testnet(TEST_ADDRESS_USED2)

    def test_connect_to_node_main(self):
        # Copy the NetworkAPI class as to not override it
        class n(NetworkAPI):
            pass

        n.connect_to_node(user="user", password="password")
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("user", "password", "localhost", 8332, False))
                for call in n.GET_BALANCE_MAIN
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_BALANCE_MAIN)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("user", "password", "localhost", 8332, False))
                for call in n.GET_TRANSACTIONS_MAIN
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTIONS_MAIN)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("user", "password", "localhost", 8332, False))
                for call in n.GET_TRANSACTION_BY_ID_MAIN
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTION_BY_ID_MAIN)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("user", "password", "localhost", 8332, False))
                for call in n.GET_UNSPENT_MAIN
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_UNSPENT_MAIN)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("user", "password", "localhost", 8332, False))
                for call in n.BROADCAST_TX_MAIN
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.BROADCAST_TX_MAIN)

        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_BALANCE_TEST)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTIONS_TEST)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTION_BY_ID_TEST)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_UNSPENT_TEST)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.BROADCAST_TX_TEST)

    def test_connect_to_node_test(self):
        # Copy the NetworkAPI class as to not override it
        class n(NetworkAPI):
            pass

        n.connect_to_node(user="usr", password="pass", host="host", port=18443, use_https=True, testnet=True)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("usr", "pass", "host", 18443, True))
                for call in n.GET_BALANCE_TEST
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_BALANCE_TEST)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("usr", "pass", "host", 18443, True))
                for call in n.GET_TRANSACTIONS_TEST
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTIONS_TEST)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("usr", "pass", "host", 18443, True))
                for call in n.GET_TRANSACTION_BY_ID_TEST
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTION_BY_ID_TEST)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("usr", "pass", "host", 18443, True))
                for call in n.GET_UNSPENT_TEST
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.GET_UNSPENT_TEST)
        assert (
            sum(
                both_rpchosts_equal(call.__self__, RPCHost("usr", "pass", "host", 18443, True))
                for call in n.BROADCAST_TX_TEST
            )
            == 1
        )
        assert all(isinstance(call.__self__, RPCHost) for call in n.BROADCAST_TX_TEST)

        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_BALANCE_MAIN)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTIONS_MAIN)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_TRANSACTION_BY_ID_MAIN)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.GET_UNSPENT_MAIN)
        assert all(not isinstance(call.__self__, RPCHost) for call in n.BROADCAST_TX_MAIN)


@decorate_methods(catch_errors_raise_warnings, NetworkAPI.IGNORED_ERRORS)
class TestBitcoreAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BitcoreAPI.get_balance(MAIN_ADDRESS_USED1), int)

    def test_get_balance_main_used(self):
        assert BitcoreAPI.get_balance(MAIN_ADDRESS_USED3) > 0

    def test_get_balance_main_unused(self):
        assert BitcoreAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BitcoreAPI.get_balance_testnet(TEST_ADDRESS_USED2) > 0

    def test_get_balance_test_unused(self):
        assert BitcoreAPI.get_balance_testnet(TEST_ADDRESS_UNUSED) == 0

    def test_get_unspent_return_type(self):
        assert iter(BitcoreAPI.get_unspent(MAIN_ADDRESS_USED1))

    def test_get_unspent_main_used(self):
        assert len(BitcoreAPI.get_unspent(MAIN_ADDRESS_USED3)) >= 2783

    def test_get_unspent_main_unused(self):
        assert len(BitcoreAPI.get_unspent(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_unspent_test_used(self):
        assert len(BitcoreAPI.get_unspent_testnet(TEST_ADDRESS_USED2)) >= 196

    def test_get_unspent_test_unused(self):
        assert len(BitcoreAPI.get_unspent_testnet(TEST_ADDRESS_UNUSED)) == 0


@decorate_methods(catch_errors_raise_warnings, NetworkAPI.IGNORED_ERRORS)
class TestBlockchainAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockchainAPI.get_balance(MAIN_ADDRESS_USED1), int)

    def test_get_balance_used(self):
        assert BlockchainAPI.get_balance(MAIN_ADDRESS_USED3) > 0

    def test_get_balance_unused(self):
        assert BlockchainAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_transactions_return_type(self):
        assert iter(BlockchainAPI.get_transactions(MAIN_ADDRESS_USED1))

    def test_get_transactions_used(self):
        assert len(BlockchainAPI.get_transactions(MAIN_ADDRESS_USED1)) >= 236

    def test_get_transactions_unused(self):
        assert len(BlockchainAPI.get_transactions(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_transaction_by_id_valid(self):
        tx = BlockchainAPI.get_transaction_by_id(MAIN_TX_VALID)
        assert calc_txid(tx) == MAIN_TX_VALID

    def test_get_transaction_by_id_invalid(self):
        assert BlockchainAPI.get_transaction_by_id(TX_INVALID) == None

    def test_get_unspent_return_type(self):
        assert iter(BlockchainAPI.get_unspent(MAIN_ADDRESS_USED1))

    # ! BlockchainAPI only supports up to 1000 UTXOs
    def test_get_unspent_main_used(self):
        assert len(BlockchainAPI.get_unspent(MAIN_ADDRESS_USED2)) > 1

    def test_get_unspent_main_used_too_many(self):
        with pytest.raises(bit.exceptions.ExcessiveAddress):
            BlockchainAPI.get_unspent(MAIN_ADDRESS_USED3)

    def test_get_unspent_main_unused(self):
        assert len(BlockchainAPI.get_unspent(MAIN_ADDRESS_UNUSED)) == 0


@decorate_methods(catch_errors_raise_warnings, NetworkAPI.IGNORED_ERRORS)
class TestBlockchairAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockchairAPI.get_balance(MAIN_ADDRESS_USED1), int)

    def test_get_balance_main_used(self):
        assert BlockchairAPI.get_balance(MAIN_ADDRESS_USED3) > 0

    def test_get_balance_main_unused(self):
        assert BlockchairAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BlockchairAPI.get_balance_testnet(TEST_ADDRESS_USED2) > 0

    def test_get_balance_test_unused(self):
        assert BlockchairAPI.get_balance_testnet(TEST_ADDRESS_UNUSED) == 0

    def test_get_transactions_return_type(self):
        assert iter(BlockchairAPI.get_transactions(MAIN_ADDRESS_USED1))

    def test_get_transactions_main_used(self):
        assert len(BlockchairAPI.get_transactions(MAIN_ADDRESS_USED1)) >= 236

    def test_get_transactions_main_unused(self):
        assert len(BlockchairAPI.get_transactions(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_transactions_test_used(self):
        assert len(BlockchairAPI.get_transactions_testnet(TEST_ADDRESS_USED2)) >= 444

    def test_get_transactions_test_unused(self):
        assert len(BlockchairAPI.get_transactions_testnet(TEST_ADDRESS_UNUSED)) == 0

    def test_get_transaction_by_id_valid(self):
        tx = BlockchairAPI.get_transaction_by_id(MAIN_TX_VALID)
        assert calc_txid(tx) == MAIN_TX_VALID

    def test_get_transaction_by_id_invalid(self):
        assert BlockchairAPI.get_transaction_by_id(TX_INVALID) == None

    def test_get_transaction_by_id_test_valid(self):
        tx = BlockchairAPI.get_transaction_by_id_testnet(TEST_TX_VALID)
        assert calc_txid(tx) == TEST_TX_VALID

    def test_get_transaction_by_id_test_invalid(self):
        assert BlockchairAPI.get_transaction_by_id_testnet(TX_INVALID) == None

    def test_get_unspent_return_type(self):
        assert iter(BlockchairAPI.get_unspent(MAIN_ADDRESS_USED1))

    def test_get_unspent_main_used(self):
        assert len(BlockchairAPI.get_unspent(MAIN_ADDRESS_USED3)) >= 2783

    def test_get_unspent_main_unused(self):
        assert len(BlockchairAPI.get_unspent(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_unspent_test_used(self):
        assert len(BlockchairAPI.get_unspent_testnet(TEST_ADDRESS_USED2)) >= 196

    def test_get_unspent_test_unused(self):
        assert len(BlockchairAPI.get_unspent_testnet(TEST_ADDRESS_UNUSED)) == 0


@decorate_methods(catch_errors_raise_warnings, NetworkAPI.IGNORED_ERRORS)
class TestBlockstreamAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockstreamAPI.get_balance(MAIN_ADDRESS_USED1), int)

    def test_get_balance_main_used(self):
        assert BlockstreamAPI.get_balance(MAIN_ADDRESS_USED3) > 0

    def test_get_balance_main_unused(self):
        assert BlockstreamAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BlockstreamAPI.get_balance_testnet(TEST_ADDRESS_USED2) > 0

    def test_get_balance_test_unused(self):
        assert BlockstreamAPI.get_balance_testnet(TEST_ADDRESS_UNUSED) == 0

    def test_get_transactions_return_type(self):
        assert iter(BlockstreamAPI.get_transactions(MAIN_ADDRESS_USED1))

    def test_get_transactions_main_used(self):
        assert len(BlockstreamAPI.get_transactions(MAIN_ADDRESS_USED1)) >= 236

    def test_get_transactions_main_unused(self):
        assert len(BlockstreamAPI.get_transactions(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_transactions_test_used(self):
        assert len(BlockstreamAPI.get_transactions_testnet(TEST_ADDRESS_USED2)) >= 444

    def test_get_transactions_test_unused(self):
        assert len(BlockstreamAPI.get_transactions_testnet(TEST_ADDRESS_UNUSED)) == 0

    def test_get_transaction_by_id_valid(self):
        tx = BlockstreamAPI.get_transaction_by_id(MAIN_TX_VALID)
        assert calc_txid(tx) == MAIN_TX_VALID

    def test_get_transaction_by_id_invalid(self):
        assert BlockstreamAPI.get_transaction_by_id(TX_INVALID) == None

    def test_get_transaction_by_id_test_valid(self):
        tx = BlockstreamAPI.get_transaction_by_id_testnet(TEST_TX_VALID)
        assert calc_txid(tx) == TEST_TX_VALID

    def test_get_transaction_by_id_test_invalid(self):
        assert BlockstreamAPI.get_transaction_by_id_testnet(TX_INVALID) == None

    def test_get_unspent_return_type(self):
        assert iter(BlockstreamAPI.get_unspent(MAIN_ADDRESS_USED1))

    #! BlockstreamAPI blocks addresses with "too many history entries" for UTXOs.
    #! Using an address with fewer UTXOs instead.
    def test_get_unspent_main_used(self):
        assert len(BlockstreamAPI.get_unspent(MAIN_ADDRESS_USED2)) >= 1

    def test_get_unspent_main_too_many(self):
        with pytest.raises(bit.exceptions.ExcessiveAddress):
            BlockstreamAPI.get_unspent(MAIN_ADDRESS_USED3)

    def test_get_unspent_main_unused(self):
        assert len(BlockstreamAPI.get_unspent(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_unspent_test_used(self):
        assert len(BlockstreamAPI.get_unspent_testnet(TEST_ADDRESS_USED2)) >= 196

    def test_get_unspent_test_unused(self):
        assert len(BlockstreamAPI.get_unspent_testnet(TEST_ADDRESS_UNUSED)) == 0


@decorate_methods(catch_errors_raise_warnings, NetworkAPI.IGNORED_ERRORS)
class TestSmartbitAPI:
    def test_get_balance_return_type(self):
        assert isinstance(SmartbitAPI.get_balance(MAIN_ADDRESS_USED1), int)

    def test_get_balance_main_used(self):
        assert SmartbitAPI.get_balance(MAIN_ADDRESS_USED3) > 0

    def test_get_balance_main_unused(self):
        assert SmartbitAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert SmartbitAPI.get_balance_testnet(TEST_ADDRESS_USED2) > 0

    def test_get_balance_test_unused(self):
        assert SmartbitAPI.get_balance_testnet(TEST_ADDRESS_UNUSED) == 0

    def test_get_transactions_return_type(self):
        assert iter(SmartbitAPI.get_transactions(MAIN_ADDRESS_USED1))

    def test_get_transactions_main_used(self):
        assert len(SmartbitAPI.get_transactions(MAIN_ADDRESS_USED1)) >= 236

    def test_get_transactions_main_unused(self):
        assert len(SmartbitAPI.get_transactions(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_transactions_test_used(self):
        assert len(SmartbitAPI.get_transactions_testnet(TEST_ADDRESS_USED2)) >= 444

    def test_get_transactions_test_unused(self):
        assert len(SmartbitAPI.get_transactions_testnet(TEST_ADDRESS_UNUSED)) == 0

    def test_get_transaction_by_id_valid(self):
        tx = SmartbitAPI.get_transaction_by_id(MAIN_TX_VALID)
        assert calc_txid(tx) == MAIN_TX_VALID

    def test_get_transaction_by_id_invalid(self):
        assert SmartbitAPI.get_transaction_by_id(TX_INVALID) == None

    def test_get_transaction_by_id_test_valid(self):
        tx = SmartbitAPI.get_transaction_by_id_testnet(TEST_TX_VALID)
        assert calc_txid(tx) == TEST_TX_VALID

    def test_get_transaction_by_id_test_invalid(self):
        assert SmartbitAPI.get_transaction_by_id_testnet(TX_INVALID) == None

    def test_get_unspent_return_type(self):
        assert iter(SmartbitAPI.get_unspent(MAIN_ADDRESS_USED1))

    def test_get_unspent_main_used(self):
        assert len(SmartbitAPI.get_unspent(MAIN_ADDRESS_USED3)) >= 2783

    def test_get_unspent_main_unused(self):
        assert len(SmartbitAPI.get_unspent(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_unspent_test_used(self):
        assert len(SmartbitAPI.get_unspent_testnet(TEST_ADDRESS_USED2)) >= 196

    def test_get_unspent_test_unused(self):
        assert len(SmartbitAPI.get_unspent_testnet(TEST_ADDRESS_UNUSED)) == 0


class TestRPCHost:
    def test_init(self):
        node = RPCHost("user", "password", "host", 8333, True)
        assert node._url == "https://user:password@host:8333/"
        assert isinstance(node._session, requests.Session)
        assert node._session.verify is True
        assert node._headers == {"content-type": "application/json"}

        node = RPCHost("usr", "pass", "other", 18443, False)
        assert node._url == "http://usr:pass@other:18443/"
        assert isinstance(node._session, requests.Session)
        assert node._session.verify is False
        assert node._headers == {"content-type": "application/json"}

    def test_rpc_method_call(self):
        assert isinstance(RPCHost.__getattr__(None, "rpc_method"), RPCMethod)
        assert RPCHost.__getattr__(None, "rpc_method")._rpc_method == "rpc_method"
        assert RPCHost.__getattr__(None, "rpc_method")._host is None

    def test_get_balance_return_type(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert isinstance(node.get_balance(MAIN_ADDRESS_USED1), int)

    def test_get_balance_main_unused(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert node.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_unused(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert node.get_balance_testnet(TEST_ADDRESS_UNUSED) == 0

    def test_get_balance_main_used(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert node.get_balance(MAIN_ADDRESS_USED1) == 123456789

    def test_get_balance_test_used(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert node.get_balance_testnet(TEST_ADDRESS_USED2) == 123456789

    def test_get_transactions_return_type(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert iter(node.get_transactions(MAIN_ADDRESS_USED1))

    def test_get_transactions_main_used(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert len(node.get_transactions(MAIN_ADDRESS_USED1)) == 2

    def test_get_transactions_main_unused(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert len(node.get_transactions(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_transactions_test_used(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert len(node.get_transactions_testnet(TEST_ADDRESS_USED2)) == 3

    def test_get_transactions_test_unused(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert len(node.get_transactions_testnet(TEST_ADDRESS_UNUSED)) == 0

    def test_get_transaction_by_id_main(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert node.get_transaction_by_id(MAIN_TX_VALID)

    def test_get_transaction_by_id_test(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert node.get_transaction_by_id_testnet(TEST_TX_VALID)

    def test_get_unspent_return_type(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert iter(node.get_unspent(MAIN_ADDRESS_USED1))

    def test_get_unspent_used(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert len(node.get_unspent(MAIN_ADDRESS_USED1)) == 2

    def test_get_unspent_unused(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert len(node.get_unspent(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_unspent_test_used(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert len(node.get_unspent_testnet(TEST_ADDRESS_USED2)) == 2

    def test_get_unspent_test_unused(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert len(node.get_unspent_testnet(TEST_ADDRESS_UNUSED)) == 0

    def test_broadcast_tx(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert node.broadcast_tx("01000000000000000000") is True

    def test_broadcast_tx_fail(self):
        node = MockRPCHost("user", "password", "host", 8333, True)
        assert node.broadcast_tx("00000000000000000000") is False

    def test_broadcast_tx_test(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert node.broadcast_tx_testnet("01000000000000000000") is True

    def test_broadcast_tx_test_fail(self):
        node = MockRPCHost("user", "password", "host", 18443, False)
        assert node.broadcast_tx_testnet("00000000000000000000") is False


class TestRPCMethod(unittest.TestCase):
    def test_init(self):
        method = RPCMethod("some_rpc_method", None)
        assert method._rpc_method == "some_rpc_method"
        assert method._host is None

    @requests_mock.mock()
    def test_call_success(self, m):
        method = RPCMethod("some_rpc_method", RPCHost("user", "password", "host", 18443, False))
        m.register_uri(
            'POST',
            'http://user:password@host:18443/',
            request_headers={"content-type": "application/json"},
            additional_matcher=lambda req: req.text
            == json.dumps({"method": "some_rpc_method", "params": ["arg1", 2], "jsonrpc": "2.0"}),
            json=json.loads('{"result": true, "error": null}'),
            status_code=200,
        )
        self.assertEqual(method("arg1", 2), True)

        method = RPCMethod("other_rpc_method", RPCHost("user", "password", "host", 18443, False))
        m.register_uri(
            'POST',
            'http://user:password@host:18443/',
            request_headers={"content-type": "application/json"},
            additional_matcher=lambda req: req.text
            == json.dumps({"method": "other_rpc_method", "params": [[0], "arg2", "arg3"], "jsonrpc": "2.0"}),
            json=json.loads('{"result": true, "error": null}'),
            status_code=500,
        )
        self.assertEqual(method([0], "arg2", "arg3"), True)

    @requests_mock.mock()
    def test_call_fails_status_code(self, m):
        method = RPCMethod("some_rpc_method", RPCHost("user", "password", "host", 18443, False))
        m.register_uri(
            'POST', 'http://user:password@host:18443/', status_code=201, reason="testing failing status code"
        )
        with pytest.raises(bit.exceptions.BitcoinNodeException):
            method()

    @requests_mock.mock()
    def test_call_fails_unsupported_command(self, m):
        method = RPCMethod("some_rpc_method", RPCHost("user", "password", "host", 18443, False))
        m.register_uri(
            'POST',
            'http://user:password@host:18443/',
            json=json.loads('{"result": false, "error": true}'),
            status_code=200,
            reason="testing failing return value",
        )
        with pytest.raises(bit.exceptions.BitcoinNodeException):
            method()

    def test_call_fails_connection(self):
        method = RPCMethod("some_rpc_method", RPCHost("user", "password", "some_invalid_host", 18443, False))
        with pytest.raises(ConnectionError):
            method()

    def test_subcall(self):
        method = RPCMethod("some_rpc_method", None)
        sub_method = method.sub_cmd
        assert sub_method._rpc_method == "some_rpc_method.sub_cmd"
        assert sub_method._host is None
