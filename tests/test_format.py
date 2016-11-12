import pytest

from bit.format import (
    coords_to_public_key, der_to_private_key, pem_to_private_key,
    point_to_public_key, private_key_to_der, private_key_to_hex,
    private_key_to_pem, private_key_hex_to_wif, public_key_to_coords,
    public_key_to_address, wif_checksum_check, wif_to_private_key_hex
)
from .samples import (
    BITCOIN_ADDRESS, BITCOIN_ADDRESS_CHECK, BITCOIN_ADDRESS_TEST,
    PRIVATE_KEY_BYTES, PRIVATE_KEY_DER, PRIVATE_KEY_HEX, PRIVATE_KEY_PEM,
    PUBLIC_KEY_COMPRESSED, PUBLIC_KEY_UNCOMPRESSED, PUBLIC_KEY_X,
    PUBLIC_KEY_Y, WALLET_FORMAT_COMPRESSED, WALLET_FORMAT_MAIN,
    WALLET_FORMAT_TEST
)


class TestPrivateKeyToWIF:
    def test_private_key_hex_to_wif_bytes(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_BYTES) == WALLET_FORMAT_MAIN

    def test_private_key_hex_to_wif_hex(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_HEX) == WALLET_FORMAT_MAIN

    def test_private_key_hex_to_wif_test(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_BYTES, version='test') == WALLET_FORMAT_TEST

    def test_private_key_hex_to_wif_compressed(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_BYTES, compressed=True) == WALLET_FORMAT_COMPRESSED


class TestWIFToPrivateKeyHex:
    def test_wif_to_private_key_hex_main(self):
        assert wif_to_private_key_hex(WALLET_FORMAT_MAIN) == PRIVATE_KEY_HEX

    def test_wif_to_private_key_hex_test(self):
        assert wif_to_private_key_hex(WALLET_FORMAT_TEST) == PRIVATE_KEY_HEX

    def test_wif_to_private_key_hex_compressed(self):
        assert wif_to_private_key_hex(WALLET_FORMAT_COMPRESSED) == PRIVATE_KEY_HEX

    def test_wif_to_private_key_hex_invalid_network(self):
        with pytest.raises(ValueError):
            wif_to_private_key_hex(BITCOIN_ADDRESS)


class TestWIFChecksumCheck:
    def test_wif_checksum_check_main_success(self):
        assert wif_checksum_check(WALLET_FORMAT_MAIN)

    def test_wif_checksum_check_test_success(self):
        assert wif_checksum_check(WALLET_FORMAT_TEST)

    def test_wif_checksum_check_compressed_success(self):
        assert wif_checksum_check(WALLET_FORMAT_COMPRESSED)

    def test_wif_checksum_check_decode_failure(self):
        assert not wif_checksum_check(BITCOIN_ADDRESS_CHECK[:-1])

    def test_wif_checksum_check_other_failure(self):
        assert not wif_checksum_check(BITCOIN_ADDRESS)


class TestPublicKeyToCoords:
    def test_public_key_to_coords_compressed(self):
        assert public_key_to_coords(PUBLIC_KEY_COMPRESSED) == (PUBLIC_KEY_X, PUBLIC_KEY_Y)

    def test_public_key_to_coords_uncompressed(self):
        assert public_key_to_coords(PUBLIC_KEY_UNCOMPRESSED) == (PUBLIC_KEY_X, PUBLIC_KEY_Y)

    def test_public_key_to_coords_incorrect_length(self):
        with pytest.raises(ValueError):
            public_key_to_coords(PUBLIC_KEY_COMPRESSED[1:])


class TestPublicKeyToAddress:
    def test_public_key_to_address_compressed(self):
        assert public_key_to_address(PUBLIC_KEY_COMPRESSED) == BITCOIN_ADDRESS

    def test_public_key_to_address_uncompressed(self):
        assert public_key_to_address(PUBLIC_KEY_UNCOMPRESSED) == BITCOIN_ADDRESS

    def test_public_key_to_address_incorrect_length(self):
        with pytest.raises(ValueError):
            public_key_to_address(PUBLIC_KEY_COMPRESSED[:-1])

    def test_public_key_to_address_test(self):
        assert public_key_to_address(PUBLIC_KEY_COMPRESSED, version='test') == BITCOIN_ADDRESS_TEST


class TestCoordsToPublicKey:
    def test_coords_to_public_key_compressed(self):
        assert coords_to_public_key(PUBLIC_KEY_X, PUBLIC_KEY_Y) == PUBLIC_KEY_COMPRESSED

    def test_coords_to_public_key_uncompressed(self):
        assert coords_to_public_key(PUBLIC_KEY_X, PUBLIC_KEY_Y, compressed=False) == PUBLIC_KEY_UNCOMPRESSED


def test_point_to_public_key():
    class Point:
        x = PUBLIC_KEY_X
        y = PUBLIC_KEY_Y
    assert point_to_public_key(Point) == coords_to_public_key(Point.x, Point.y)


def test_der():
    assert private_key_to_der(der_to_private_key(PRIVATE_KEY_DER)) == PRIVATE_KEY_DER


def test_pem():
    assert private_key_to_pem(pem_to_private_key(PRIVATE_KEY_PEM)) == PRIVATE_KEY_PEM


def test_private_key_to_hex():
    assert private_key_to_hex(der_to_private_key(PRIVATE_KEY_DER)) == PRIVATE_KEY_HEX
