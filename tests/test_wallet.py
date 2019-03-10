import os
import sys
import time

import pytest

from bit.crypto import ECPrivateKey
from bit.curve import Point
from bit.format import verify_sig
from bit.network import NetworkAPI
from bit.wallet import (
    BaseKey, Key, PrivateKey, PrivateKeyTestnet, MultiSig, MultiSigTestnet,
    wif_to_key
)
from .samples import (
    BITCOIN_ADDRESS, BITCOIN_ADDRESS_TEST, BITCOIN_ADDRESS_P2SH_MULTISIG,
    BITCOIN_ADDRESS_NP2SH_MULTISIG, BITCOIN_ADDRESS_TEST_P2SH_MULTISIG,
    BITCOIN_ADDRESS_TEST_NP2SH_MULTISIG, PRIVATE_KEY_BYTES, PRIVATE_KEY_DER,
    PRIVATE_KEY_HEX, PRIVATE_KEY_NUM, PRIVATE_KEY_PEM,
    PUBLIC_KEY_COMPRESSED, PUBLIC_KEY_UNCOMPRESSED, PUBLIC_KEY_X,
    PUBLIC_KEY_Y, WALLET_FORMAT_COMPRESSED_MAIN, WALLET_FORMAT_COMPRESSED_TEST,
    WALLET_FORMAT_MAIN, WALLET_FORMAT_MAIN_1, WALLET_FORMAT_MAIN_2,
    WALLET_FORMAT_TEST, WALLET_FORMAT_TEST_1, WALLET_FORMAT_TEST_2
)

TRAVIS = 'TRAVIS' in os.environ


class TestWIFToKey:
    def test_compressed_main(self):
        key = wif_to_key(WALLET_FORMAT_COMPRESSED_MAIN)
        assert isinstance(key, PrivateKey)
        assert key.is_compressed()

    def test_uncompressed_main(self):
        key = wif_to_key(WALLET_FORMAT_MAIN)
        assert isinstance(key, PrivateKey)
        assert not key.is_compressed()

    def test_compressed_test(self):
        key = wif_to_key(WALLET_FORMAT_COMPRESSED_TEST)
        assert isinstance(key, PrivateKeyTestnet)
        assert key.is_compressed()

    def test_uncompressed_test(self):
        key = wif_to_key(WALLET_FORMAT_TEST)
        assert isinstance(key, PrivateKeyTestnet)
        assert not key.is_compressed()


class TestBaseKey:
    def test_init_default(self):
        base_key = BaseKey()

        assert isinstance(base_key._pk, ECPrivateKey)
        assert len(base_key.public_key) == 33

    def test_init_from_key(self):
        pk = ECPrivateKey()
        base_key = BaseKey(pk)
        assert base_key._pk == pk

    def test_init_wif_error(self):
        with pytest.raises(TypeError):
            BaseKey(b'\x00')

    def test_public_key_compressed(self):
        base_key = BaseKey(WALLET_FORMAT_COMPRESSED_MAIN)
        assert base_key.public_key == PUBLIC_KEY_COMPRESSED

    def test_public_key_uncompressed(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.public_key == PUBLIC_KEY_UNCOMPRESSED

    def test_public_point(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.public_point == Point(PUBLIC_KEY_X, PUBLIC_KEY_Y)
        assert base_key.public_point == Point(PUBLIC_KEY_X, PUBLIC_KEY_Y)

    def test_sign(self):
        base_key = BaseKey()
        data = os.urandom(200)
        signature = base_key.sign(data)
        assert verify_sig(signature, data, base_key.public_key)

    def test_verify_success(self):
        base_key = BaseKey()
        data = os.urandom(200)
        signature = base_key.sign(data)
        assert base_key.verify(signature, data)

    def test_verify_failure(self):
        base_key = BaseKey()
        data = os.urandom(200)
        signature = base_key.sign(data)
        assert not base_key.verify(signature, data[::-1])

    def test_to_hex(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_hex() == PRIVATE_KEY_HEX

    def test_to_bytes(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_bytes() == PRIVATE_KEY_BYTES

    def test_to_der(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_der() == PRIVATE_KEY_DER

    def test_to_pem(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_pem() == PRIVATE_KEY_PEM

    def test_to_int(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_int() == PRIVATE_KEY_NUM

    def test_is_compressed(self):
        assert BaseKey(WALLET_FORMAT_COMPRESSED_MAIN).is_compressed() is True
        assert BaseKey(WALLET_FORMAT_MAIN).is_compressed() is False

    def test_equal(self):
        assert BaseKey(WALLET_FORMAT_COMPRESSED_MAIN) == BaseKey(WALLET_FORMAT_COMPRESSED_MAIN)


class TestPrivateKey:
    def test_alias(self):
        assert Key == PrivateKey

    def test_init_default(self):
        private_key = PrivateKey()

        assert private_key._address is None
        assert private_key.balance == 0
        assert private_key.unspents == []
        assert private_key.transactions == []

    def test_address(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        assert private_key.address == BITCOIN_ADDRESS
        assert private_key.segwit_address is None

    def test_to_wif(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        assert private_key.to_wif() == WALLET_FORMAT_MAIN

        private_key = PrivateKey(WALLET_FORMAT_COMPRESSED_MAIN)
        assert private_key.to_wif() == WALLET_FORMAT_COMPRESSED_MAIN

    def test_get_balance(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        balance = int(private_key.get_balance())
        assert balance == private_key.balance

    def test_get_unspent(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        unspent = private_key.get_unspents()
        assert unspent == private_key.unspents

    def test_get_transactions(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        transactions = private_key.get_transactions()
        assert transactions == private_key.transactions

    def test_from_hex(self):
        key = PrivateKey.from_hex(PRIVATE_KEY_HEX)
        assert isinstance(key, PrivateKey)
        assert key.to_hex() == PRIVATE_KEY_HEX

    def test_from_der(self):
        key = PrivateKey.from_der(PRIVATE_KEY_DER)
        assert isinstance(key, PrivateKey)
        assert key.to_der() == PRIVATE_KEY_DER

    def test_from_pem(self):
        key = PrivateKey.from_pem(PRIVATE_KEY_PEM)
        assert isinstance(key, PrivateKey)
        assert key.to_pem() == PRIVATE_KEY_PEM

    def test_from_int(self):
        key = PrivateKey.from_int(PRIVATE_KEY_NUM)
        assert isinstance(key, PrivateKey)
        assert key.to_int() == PRIVATE_KEY_NUM

    def test_repr(self):
        assert repr(PrivateKey(WALLET_FORMAT_MAIN)) == '<PrivateKey: 1ELReFsTCUY2mfaDTy32qxYiT49z786eFg>'


class TestPrivateKeyTestnet:
    def test_init_default(self):
        private_key = PrivateKeyTestnet()

        assert private_key._address is None
        assert private_key.balance == 0
        assert private_key.unspents == []
        assert private_key.transactions == []

    def test_address(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        assert private_key.address == BITCOIN_ADDRESS_TEST
        assert private_key.segwit_address is None

    def test_to_wif(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        assert private_key.to_wif() == WALLET_FORMAT_TEST

        private_key = PrivateKeyTestnet(WALLET_FORMAT_COMPRESSED_TEST)
        assert private_key.to_wif() == WALLET_FORMAT_COMPRESSED_TEST

    def test_get_balance(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        balance = int(private_key.get_balance())
        assert balance == private_key.balance

    def test_get_unspent(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        unspent = private_key.get_unspents()
        assert unspent == private_key.unspents

    def test_get_transactions(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        transactions = private_key.get_transactions()
        assert transactions == private_key.transactions

    def test_send(self):
        if TRAVIS and sys.version_info[:2] != (3, 7):
            return

        private_key = PrivateKeyTestnet(WALLET_FORMAT_COMPRESSED_TEST)
        private_key.get_unspents()

        initial = len(private_key.get_transactions())
        current = initial
        tries = 0

        private_key.send([('mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt', 1, 'jpy')])

        while tries < 180:  # pragma: no cover
            current = len(private_key.get_transactions())
            if current > initial:
                break
            time.sleep(6)
            tries += 1

        assert current > initial

    def test_cold_storage(self):
        if TRAVIS and sys.version_info[:2] != (3, 7):
            return

        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        address = private_key.address

        prepared = PrivateKeyTestnet.prepare_transaction(
            address, [('mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt', 1, 'jpy')]
        )
        tx_hex = private_key.sign_transaction(prepared)

        initial = len(private_key.get_transactions())
        current = initial
        tries = 0

        NetworkAPI.broadcast_tx_testnet(tx_hex)

        while tries < 15:  # pragma: no cover
            current = len(private_key.get_transactions())
            if current > initial:
                break
            time.sleep(5)
            tries += 1

        assert current > initial

    def test_from_hex(self):
        key = PrivateKeyTestnet.from_hex(PRIVATE_KEY_HEX)
        assert isinstance(key, PrivateKeyTestnet)
        assert key.to_hex() == PRIVATE_KEY_HEX

    def test_from_der(self):
        key = PrivateKeyTestnet.from_der(PRIVATE_KEY_DER)
        assert isinstance(key, PrivateKeyTestnet)
        assert key.to_der() == PRIVATE_KEY_DER

    def test_from_pem(self):
        key = PrivateKeyTestnet.from_pem(PRIVATE_KEY_PEM)
        assert isinstance(key, PrivateKeyTestnet)
        assert key.to_pem() == PRIVATE_KEY_PEM

    def test_from_int(self):
        key = PrivateKeyTestnet.from_int(PRIVATE_KEY_NUM)
        assert isinstance(key, PrivateKeyTestnet)
        assert key.to_int() == PRIVATE_KEY_NUM

    def test_repr(self):
        assert repr(PrivateKeyTestnet(WALLET_FORMAT_MAIN)) == '<PrivateKeyTestnet: mtrNwJxS1VyHYn3qBY1Qfsm3K3kh1mGRMS>'


class TestMultiSig:
    def test_init_default(self):
        key1 = PrivateKey()
        key2 = PrivateKey()
        multisig = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        assert multisig._address is None
        assert multisig.balance == 0
        assert multisig.unspents == []
        assert multisig.transactions == []
        assert multisig.m == 2

    def test_address(self):
        key1 = PrivateKey(WALLET_FORMAT_MAIN_1)
        key2 = PrivateKey(WALLET_FORMAT_MAIN_2)
        multisig = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        assert multisig.address == BITCOIN_ADDRESS_P2SH_MULTISIG
        assert multisig.segwit_address == BITCOIN_ADDRESS_NP2SH_MULTISIG

    def test_get_balance(self):
        key1 = PrivateKey(WALLET_FORMAT_MAIN_1)
        key2 = PrivateKey(WALLET_FORMAT_MAIN_2)
        multisig = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        balance = int(multisig.get_balance())
        assert balance == multisig.balance

    def test_get_unspent(self):
        key1 = PrivateKey(WALLET_FORMAT_MAIN_1)
        key2 = PrivateKey(WALLET_FORMAT_MAIN_2)
        multisig = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        unspent = multisig.get_unspents()
        assert unspent == multisig.unspents

    def test_get_transactions(self):
        key1 = PrivateKey(WALLET_FORMAT_MAIN_1)
        key2 = PrivateKey(WALLET_FORMAT_MAIN_2)
        multisig = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        transactions = multisig.get_transactions()
        assert transactions == multisig.transactions

    def test_repr(self):
        key1 = PrivateKey(WALLET_FORMAT_MAIN_1)
        key2 = PrivateKey(WALLET_FORMAT_MAIN_2)
        multisig = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        assert repr(multisig) == '<MultiSig: {}>'.format(BITCOIN_ADDRESS_P2SH_MULTISIG)


class TestMultiSigTestnet:
    def test_init_default(self):
        key1 = PrivateKeyTestnet()
        key2 = PrivateKeyTestnet()
        multisig = MultiSigTestnet(key1, [key1.public_key, key2.public_key], 2)
        assert multisig._address is None
        assert multisig.balance == 0
        assert multisig.unspents == []
        assert multisig.transactions == []
        assert multisig.m == 2

    def test_address(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        multisig = MultiSigTestnet(key1, [key1.public_key, key2.public_key], 2)
        assert multisig.address == BITCOIN_ADDRESS_TEST_P2SH_MULTISIG
        assert multisig.segwit_address == BITCOIN_ADDRESS_TEST_NP2SH_MULTISIG

    def test_get_balance(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        multisig = MultiSigTestnet(key1, [key1.public_key, key2.public_key], 2)
        balance = int(multisig.get_balance())
        assert balance == multisig.balance

    def test_get_unspent(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        multisig = MultiSigTestnet(key1, [key1.public_key, key2.public_key], 2)
        unspent = multisig.get_unspents()
        assert unspent == multisig.unspents

    def test_get_transactions(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        multisig = MultiSigTestnet(key1, [key1.public_key, key2.public_key], 2)
        transactions = multisig.get_transactions()
        assert transactions == multisig.transactions

    def test_repr(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        multisig = MultiSigTestnet(key1, [key1.public_key, key2.public_key], 2)
        assert repr(multisig) == '<MultiSigTestnet: {}>'.format(BITCOIN_ADDRESS_TEST_P2SH_MULTISIG)
