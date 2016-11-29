import pytest

from bit.crypto import ECDSA_SHA256, EllipticCurvePrivateKey
from bit.curve import Point
from bit.keygen import generate_private_key
from bit.wallet import BaseKey, Key, PrivateKey, PrivateKeyTestnet
from .samples import (
    BITCOIN_ADDRESS, BITCOIN_ADDRESS_TEST, PRIVATE_KEY_DER,
    PRIVATE_KEY_HEX, PRIVATE_KEY_NUM, PRIVATE_KEY_PEM,
    PUBLIC_KEY_COMPRESSED, PUBLIC_KEY_UNCOMPRESSED, PUBLIC_KEY_X,
    PUBLIC_KEY_Y, WALLET_FORMAT_COMPRESSED_MAIN, WALLET_FORMAT_COMPRESSED_TEST,
    WALLET_FORMAT_MAIN, WALLET_FORMAT_TEST
)


class TestBaseKey:
    def test_init_default(self):
        base_key = BaseKey()

        assert isinstance(base_key._pk, EllipticCurvePrivateKey)
        assert isinstance(base_key.public_point(), Point)
        assert len(base_key.public_key()) == 33

    def test_init_from_key(self):
        pk = generate_private_key()
        base_key = BaseKey(pk)
        assert base_key._pk == pk

    def test_init_wif_error(self):
        with pytest.raises(ValueError):
            BaseKey(b'\x00')

    def test_public_key_compressed(self):
        base_key = BaseKey(WALLET_FORMAT_COMPRESSED_MAIN)
        assert base_key.public_key() == PUBLIC_KEY_COMPRESSED

    def test_public_key_uncompressed(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.public_key() == PUBLIC_KEY_UNCOMPRESSED

    def test_public_point(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.public_point() == Point(PUBLIC_KEY_X, PUBLIC_KEY_Y)

    def test_sign(self):
        base_key = BaseKey()
        signature = base_key.sign(PUBLIC_KEY_COMPRESSED)
        public_key = base_key._pk.public_key()
        assert public_key.verify(signature, PUBLIC_KEY_COMPRESSED, ECDSA_SHA256)

    def test_verify_success(self):
        base_key = BaseKey()
        signature = base_key.sign(PUBLIC_KEY_COMPRESSED)
        assert base_key.verify(signature, PUBLIC_KEY_COMPRESSED)

    def test_verify_failure(self):
        base_key = BaseKey()
        signature = base_key.sign(PUBLIC_KEY_COMPRESSED)
        assert not base_key.verify(signature, PUBLIC_KEY_UNCOMPRESSED)

    def test_to_hex(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_hex() == PRIVATE_KEY_HEX

    def test_to_der(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_der() == PRIVATE_KEY_DER

    def test_to_pem(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_pem() == PRIVATE_KEY_PEM

    def test_to_int(self):
        base_key = BaseKey(WALLET_FORMAT_MAIN)
        assert base_key.to_int() == PRIVATE_KEY_NUM

    def test_from_hex(self):
        assert BaseKey.from_hex(PRIVATE_KEY_HEX).to_hex() == PRIVATE_KEY_HEX

    def test_from_der(self):
        assert BaseKey.from_der(PRIVATE_KEY_DER).to_der() == PRIVATE_KEY_DER

    def test_from_pem(self):
        assert BaseKey.from_pem(PRIVATE_KEY_PEM).to_pem() == PRIVATE_KEY_PEM

    def test_from_int(self):
        assert BaseKey.from_int(PRIVATE_KEY_NUM).to_int() == PRIVATE_KEY_NUM


class TestPrivateKey:
    def test_alias(self):
        assert Key == PrivateKey

    def test_init_default(self):
        private_key = PrivateKey()

        assert private_key._balance is None
        assert private_key._utxos == []
        assert private_key._transactions == []

    def test_init_sync(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN, sync=True)
        assert len(private_key.transactions()) > 0

    def test_address(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        assert private_key.address == BITCOIN_ADDRESS

    def test_to_wif(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        assert private_key.to_wif() == WALLET_FORMAT_MAIN

        private_key = PrivateKey(WALLET_FORMAT_COMPRESSED_MAIN)
        assert private_key.to_wif() == WALLET_FORMAT_COMPRESSED_MAIN

    def test_get_balance(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        balance = private_key.get_balance()
        assert balance == private_key.balance()

    def test_get_utxo(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        utxo = private_key.get_utxos()
        assert utxo == private_key.utxos()

    def test_get_transactions(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        transactions = private_key.get_transactions()
        assert transactions == private_key.transactions()

    def test_sync(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        private_key.sync()
        assert len(private_key.transactions()) > 0

    def test_repr(self):
        assert repr(PrivateKey(WALLET_FORMAT_MAIN)) == '<PrivateKey: 1ELReFsTCUY2mfaDTy32qxYiT49z786eFg>'


class TestPrivateKeyTestnet:
    def test_init_default(self):
        private_key = PrivateKeyTestnet()

        assert private_key._balance is None
        assert private_key._utxos == []
        assert private_key._transactions == []

    def test_init_sync(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST, sync=True)
        assert len(private_key.transactions()) > 0

    def test_address(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        assert private_key.address == BITCOIN_ADDRESS_TEST

    def test_to_wif(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        assert private_key.to_wif() == WALLET_FORMAT_TEST

        private_key = PrivateKeyTestnet(WALLET_FORMAT_COMPRESSED_TEST)
        assert private_key.to_wif() == WALLET_FORMAT_COMPRESSED_TEST

    def test_get_balance(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        balance = private_key.get_balance()
        assert balance == private_key.balance()

    def test_get_utxo(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        utxo = private_key.get_utxos()
        assert utxo == private_key.utxos()

    def test_get_transactions(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        transactions = private_key.get_transactions()
        assert transactions == private_key.transactions()

    def test_sync(self):
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST)
        private_key.sync()
        assert len(private_key.transactions()) > 0

    def test_repr(self):
        assert repr(PrivateKeyTestnet(WALLET_FORMAT_MAIN)) == '<PrivateKeyTestnet: mtrNwJxS1VyHYn3qBY1Qfsm3K3kh1mGRMS>'
