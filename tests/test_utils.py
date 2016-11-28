import pytest

from bit.utils import (
    bytes_to_hex, flip_hex_byte_order, hex_to_bytes, hex_to_int,
    int_to_hex, int_to_unknown_bytes
)

BIG_INT = 123456789 ** 5
BYTES_BIG = b'TH8\xe2\xaaN\xd7^aX7\x93\xe7\xc6\xa3\x02\x85'
BYTES_LITTLE = b'\x85\x02\xa3\xc6\xe7\x937Xa^\xd7N\xaa\xe28HT'
HEX = '544838E2AA4ED75E61583793E7C6A30285'
ODD_HEX = '4FADD1977328C11EFC1C1D8A781AA6B9677984D3E0BD0BFC52B9F3B03885A00'
ODD_HEX_BYTES = (b'\x04\xfa\xdd\x19w2\x8c\x11\xef\xc1\xc1\xd8\xa7\x81'
                 b'\xaak\x96w\x98M>\x0b\xd0\xbf\xc5+\x9f;\x03\x88Z\x00')
ODD_HEX_NUM = 2252489133021925628692706218705147644319767320134875440800653003170737838592


class TestBytesToHex:
    def test_bytes_to_hex_default(self):
        assert bytes.fromhex(bytes_to_hex(BYTES_BIG)) == BYTES_BIG

    def test_bytes_to_hex_normal(self):
        assert bytes_to_hex(BYTES_BIG, upper=False) == HEX.lower()


class TestIntToUnknownBytes:
    def test_int_to_unknown_bytes_default(self):
        assert int_to_unknown_bytes(BIG_INT) == BYTES_BIG

    def test_int_to_unknown_bytes_little(self):
        assert int_to_unknown_bytes(BIG_INT, 'little') == BYTES_LITTLE

    def test_int_to_unknown_bytes_unknown(self):
        with pytest.raises(ValueError):
            int_to_unknown_bytes(BIG_INT, 'HUGE')


class TestIntToHex:
    def test_int_to_hex_default(self):
        assert int_to_hex(BIG_INT) == HEX

    def test_int_to_hex_normal(self):
        assert int_to_hex(BIG_INT, upper=False) == HEX.lower()


def test_hex_to_bytes():
    assert hex_to_bytes(HEX) == BYTES_BIG
    assert hex_to_bytes(ODD_HEX) == ODD_HEX_BYTES


def test_hex_to_int():
    assert hex_to_int(HEX) == BIG_INT


def test_flip_hex_byte_order():
    assert flip_hex_byte_order(bytes_to_hex(BYTES_LITTLE)) == HEX
