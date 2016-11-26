import pytest

from bit.base58 import b58decode, b58decode_check, b58encode, b58encode_check
from .samples import BINARY_ADDRESS, BITCOIN_ADDRESS, PUBKEY_HASH_MAIN


def test_b58encode():
    assert b58encode(BINARY_ADDRESS) == BITCOIN_ADDRESS
    assert b58encode(BINARY_ADDRESS[:1]) == BITCOIN_ADDRESS[:1]


def test_b58encode_check():
    assert b58encode_check(PUBKEY_HASH_MAIN) == BITCOIN_ADDRESS


class TestB58Decode:
    def test_b58decode_success(self):
        assert b58decode(BITCOIN_ADDRESS) == BINARY_ADDRESS
        assert b58decode(BITCOIN_ADDRESS[:1]) == BINARY_ADDRESS[:1]

    def test_b58decode_failure(self):
        with pytest.raises(ValueError):
            b58decode('l')


class TestB58DecodeCheck:
    def test_b58decode_check_success(self):
        assert b58decode_check(BITCOIN_ADDRESS) == PUBKEY_HASH_MAIN

    def test_b58decode_check_failure(self):
        with pytest.raises(ValueError):
            b58decode_check(BITCOIN_ADDRESS[:-1])
