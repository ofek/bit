import pytest

from bit.format import (
    address_to_public_key_hash, bytes_to_wif, coords_to_public_key,
    get_version, point_to_public_key, public_key_to_coords,
    public_key_to_address, verify_sig, wif_checksum_check, wif_to_bytes,
    public_key_to_segwit_address, multisig_to_redeemscript
)
from .samples import (
    BITCOIN_ADDRESS, BITCOIN_ADDRESS_COMPRESSED, BITCOIN_ADDRESS_PAY2SH,
    BITCOIN_ADDRESS_TEST_COMPRESSED, BITCOIN_ADDRESS_TEST,
    BITCOIN_ADDRESS_TEST_PAY2SH, PAY2SH_HASH, PAY2SH_TEST_HASH,
    PRIVATE_KEY_BYTES, PUBKEY_HASH,
    PUBKEY_HASH_COMPRESSED, PUBLIC_KEY_COMPRESSED, PUBLIC_KEY_UNCOMPRESSED,
    PUBLIC_KEY_X, PUBLIC_KEY_Y,
    WALLET_FORMAT_COMPRESSED_MAIN, WALLET_FORMAT_COMPRESSED_TEST,
    WALLET_FORMAT_MAIN, WALLET_FORMAT_TEST,
    BITCOIN_ADDRESS_NP2WKH, BITCOIN_ADDRESS_TEST_NP2WKH
)

VALID_SIGNATURE = (b'0E\x02!\x00\xd7y\xe0\xa4\xfc\xea\x88\x18sDit\x9d\x01\xf3'
                   b'\x03\xa0\xceO\xab\x80\xe8PY.*\xda\x11w|\x9fq\x02 u\xdaR'
                   b'\xd8\x84a\xad\xfamN\xae&\x91\xfd\xd6\xbd\xe1\xb0e\xfe\xf4'
                   b'\xc5S\xd9\x02D\x1d\x0b\xba\xe0=@')
INVALID_SIGNATURE = (b'0D\x02 `\x03D^\xa7\xab\xdc\xa6_\xb6&\xcbN\xc8S\xa4\xcf'
                     b'\x9a8\x02\x99\xc4\xe9\x02\xb3\x14k\xfa\x15J\xb9\x03\x02'
                     b' !\xfd\xb2\xa0:\xb3\xba\xb1\xdc\x1a]ZWb\xa5\x9d\x8a5\x1c'
                     b'\xaeQ.\xa7`\xf6V\x11\xf1\xe0iJ7')
SIGNATURE_HIGH_S = (b'0E\x02 \x18NeS,"r\x1e\x01?\xa5\xa8C\xe4\xba\x07x \xc9\xf6'
                    b'\x8fe\x17\xa3\x03\'\xac\xd8\x97\x97\x1b\xd0\x02!\x00\xdc^'
                    b'\xf2M\xe7\x0e\xbaz\xd3\xa3\x94\xcc\xef\x17\x04\xb2\xfb0!'
                    b'\n\xc3\x1fa3\x83\x01\xc9\xbf\xbd\r)\x82')
DATA = b'data'


class TestGetVersion:
    def test_mainnet(self):
        assert get_version(BITCOIN_ADDRESS) == 'main'
        assert get_version(BITCOIN_ADDRESS_COMPRESSED) == 'main'

    def test_testnet(self):
        assert get_version(BITCOIN_ADDRESS_TEST) == 'test'
        assert get_version(BITCOIN_ADDRESS_TEST_COMPRESSED) == 'test'

    def test_invalid(self):
        with pytest.raises(ValueError):
            get_version('dg2dNAjuezub6iJVPNML5pW5ZQvtA9ocL')

    def test_mainnet_pay2sh(self):
        assert get_version(BITCOIN_ADDRESS_PAY2SH) == 'main'

    def test_testnet_pay2sh(self):
        assert get_version(BITCOIN_ADDRESS_TEST_PAY2SH) == 'test'


class TestVerifySig:
    def test_valid(self):
        assert verify_sig(VALID_SIGNATURE, DATA, PUBLIC_KEY_COMPRESSED)

    def test_invalid(self):
        assert not verify_sig(INVALID_SIGNATURE, DATA, PUBLIC_KEY_COMPRESSED)


class TestBytesToWIF:
    def test_mainnet(self):
        assert bytes_to_wif(PRIVATE_KEY_BYTES) == WALLET_FORMAT_MAIN

    def test_testnet(self):
        assert bytes_to_wif(PRIVATE_KEY_BYTES, version='test') == WALLET_FORMAT_TEST

    def test_compressed(self):
        assert bytes_to_wif(PRIVATE_KEY_BYTES, compressed=True) == WALLET_FORMAT_COMPRESSED_MAIN

    def test_compressed_testnet(self):
        assert bytes_to_wif(
            PRIVATE_KEY_BYTES, version='test', compressed=True
        ) == WALLET_FORMAT_COMPRESSED_TEST


class TestWIFToBytes:
    def test_mainnet(self):
        assert wif_to_bytes(WALLET_FORMAT_MAIN) == (PRIVATE_KEY_BYTES, False, 'main')

    def test_testnet(self):
        assert wif_to_bytes(WALLET_FORMAT_TEST) == (PRIVATE_KEY_BYTES, False, 'test')

    def test_compressed(self):
        assert wif_to_bytes(WALLET_FORMAT_COMPRESSED_MAIN) == (PRIVATE_KEY_BYTES, True, 'main')

    def test_invalid_network(self):
        with pytest.raises(ValueError):
            wif_to_bytes(BITCOIN_ADDRESS)


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


class TestPublicKeyToSegwitAddress:
    def test_public_key_to_segwit_address(self):
        assert public_key_to_segwit_address(PUBLIC_KEY_COMPRESSED) == BITCOIN_ADDRESS_NP2WKH

    def test_public_key_to_segwit_address_incorrect_length(self):
        with pytest.raises(ValueError):
            public_key_to_segwit_address(PUBLIC_KEY_COMPRESSED[:-1])
        with pytest.raises(ValueError):
            public_key_to_segwit_address(PUBLIC_KEY_UNCOMPRESSED)

    def test_public_key_to_segwit_address_test(self):
        assert public_key_to_segwit_address(PUBLIC_KEY_COMPRESSED, version='test') == BITCOIN_ADDRESS_TEST_NP2WKH


class TestMultiSigToRedeemScript:
    def test_multisig_to_redeemscript(self):
        public_keys = [b'\x00'*33, b'\x00'*33]
        assert multisig_to_redeemscript(public_keys, 2) == b'R!' + b'!'.join(public_keys) + b'R\xae'

        public_keys = [b'\x00'*65, b'\x00'*65]
        assert multisig_to_redeemscript(public_keys, 2) == b'RA' + b'A'.join(public_keys) + b'R\xae'

    def test_multisig_to_redeemscript_wrong_m(self):
        public_keys_invalid = [b'\x00'*33, b'\x00'*33]
        with pytest.raises(ValueError):
            multisig_to_redeemscript(public_keys_invalid, 3)

    def test_multisig_to_redeemscript_incorrect_length(self):
        public_keys_invalid = [b'\x00'*32, b'\x00'*33]
        with pytest.raises(ValueError):
            multisig_to_redeemscript(public_keys_invalid, 2)

        public_keys_invalid = [b'\x00'*66, b'\x00'*65]
        with pytest.raises(ValueError):
            multisig_to_redeemscript(public_keys_invalid, 2)

    def test_multisig_to_redeemscript_too_long(self):
        # Maximum is 15 compressed keys in a multisig:
        try:
            public_keys = [b'\x00'*33]*15
            multisig_to_redeemscript(public_keys, 1)
        except ValueError:  # pragma: no cover
            pytest.fail("multisig_to_redeemscript did not accept 15 compressed public keys.")

        public_keys = [b'\x00'*33]*16
        with pytest.raises(ValueError):
            multisig_to_redeemscript(public_keys, 1)

        # Maximum is 7 uncompressed keys in a multisig
        try:
            public_keys = [b'\x00'*65]*7
            multisig_to_redeemscript(public_keys, 1)
        except ValueError:  # pragma: no cover
            pytest.fail("multisig_to_redeemscript did not accept 7 uncompressed public keys.")

        public_keys = [b'\x00'*65]*8
        with pytest.raises(ValueError):
            multisig_to_redeemscript(public_keys, 1)


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
    assert address_to_public_key_hash(BITCOIN_ADDRESS_PAY2SH) == PAY2SH_HASH
    assert address_to_public_key_hash(BITCOIN_ADDRESS_TEST_PAY2SH) == PAY2SH_TEST_HASH
