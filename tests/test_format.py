import pytest

from bit.format import (
    address_to_public_key_hash, coords_to_public_key, make_compliant_sig,
    point_to_public_key, private_key_hex_to_wif, public_key_to_coords,
    public_key_to_address, wif_checksum_check, wif_to_private_key_hex
)
from .samples import (
    BITCOIN_ADDRESS, BITCOIN_ADDRESS_COMPRESSED, BITCOIN_ADDRESS_TEST_COMPRESSED,
    BITCOIN_ADDRESS_TEST, PRIVATE_KEY_BYTES, PRIVATE_KEY_HEX, PUBKEY_HASH,
    PUBKEY_HASH_COMPRESSED, PUBLIC_KEY_COMPRESSED, PUBLIC_KEY_UNCOMPRESSED,
    PUBLIC_KEY_X, PUBLIC_KEY_Y, WALLET_FORMAT_COMPRESSED_MAIN,
    WALLET_FORMAT_COMPRESSED_TEST, WALLET_FORMAT_MAIN, WALLET_FORMAT_TEST
)


class TestMakeCompliantDer:
    def test_normal(self):
        # (r = 32, s = 32)
        signature = b'0\x06\x02\x01 \x02\x01 '
        assert signature == make_compliant_sig(signature)

    def test_r_greater_than_or_equal_to_128(self):
        # (r = 128, s = 32)
        signature = b'0\x07\x02\x02\x00\x80\x02\x01 '
        assert b'0\x07\x02\x02\x00\x80\x02\x01 ' == make_compliant_sig(signature)

    def test_s_greater_than_or_equal_to_128(self):
        # (r = 32, s = 128)
        signature = b'0\x07\x02\x01 \x02\x02\x00\x80'
        assert b'0\x07\x02\x01 \x02\x02\x00\x80' == make_compliant_sig(signature)


class TestPrivateKeyToWIF:
    def test_private_key_hex_to_wif_bytes(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_BYTES) == WALLET_FORMAT_MAIN

    def test_private_key_hex_to_wif_hex(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_HEX) == WALLET_FORMAT_MAIN

    def test_private_key_hex_to_wif_test(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_BYTES, version='test') == WALLET_FORMAT_TEST

    def test_private_key_hex_to_wif_compressed(self):
        assert private_key_hex_to_wif(PRIVATE_KEY_BYTES, compressed=True) == WALLET_FORMAT_COMPRESSED_MAIN

    def test_private_key_hex_to_wif_compressed_test(self):
        assert private_key_hex_to_wif(
            PRIVATE_KEY_BYTES, version='test', compressed=True) == WALLET_FORMAT_COMPRESSED_TEST


class TestWIFToPrivateKeyHex:
    def test_wif_to_private_key_hex_main(self):
        assert wif_to_private_key_hex(WALLET_FORMAT_MAIN) == (PRIVATE_KEY_HEX, False)

    def test_wif_to_private_key_hex_test(self):
        assert wif_to_private_key_hex(WALLET_FORMAT_TEST) == (PRIVATE_KEY_HEX, False)

    def test_wif_to_private_key_hex_compressed(self):
        assert wif_to_private_key_hex(WALLET_FORMAT_COMPRESSED_MAIN) == (PRIVATE_KEY_HEX, True)

    def test_wif_to_private_key_hex_invalid_network(self):
        with pytest.raises(ValueError):
            wif_to_private_key_hex(BITCOIN_ADDRESS)


class TestWIFChecksumCheck:
    def test_wif_checksum_check_main_success(self):
        assert wif_checksum_check(WALLET_FORMAT_MAIN)

    def test_wif_checksum_check_test_success(self):
        assert wif_checksum_check(WALLET_FORMAT_TEST)

    def test_wif_checksum_check_compressed_success(self):
        assert wif_checksum_check(WALLET_FORMAT_COMPRESSED_MAIN)

    def test_wif_checksum_check_decode_failure(self):
        assert not wif_checksum_check(BITCOIN_ADDRESS[:-1])

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
        assert public_key_to_address(PUBLIC_KEY_COMPRESSED) == BITCOIN_ADDRESS_COMPRESSED

    def test_public_key_to_address_uncompressed(self):
        assert public_key_to_address(PUBLIC_KEY_UNCOMPRESSED) == BITCOIN_ADDRESS

    def test_public_key_to_address_incorrect_length(self):
        with pytest.raises(ValueError):
            public_key_to_address(PUBLIC_KEY_COMPRESSED[:-1])

    def test_public_key_to_address_test_compressed(self):
        assert public_key_to_address(PUBLIC_KEY_COMPRESSED, version='test') == BITCOIN_ADDRESS_TEST_COMPRESSED

    def test_public_key_to_address_test_uncompressed(self):
        assert public_key_to_address(PUBLIC_KEY_UNCOMPRESSED, version='test') == BITCOIN_ADDRESS_TEST


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


def test_address_to_public_key_hash():
    assert address_to_public_key_hash(BITCOIN_ADDRESS) == PUBKEY_HASH
    assert address_to_public_key_hash(BITCOIN_ADDRESS_COMPRESSED) == PUBKEY_HASH_COMPRESSED
