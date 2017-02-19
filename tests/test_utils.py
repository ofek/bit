from bit.utils import (
    Decimal, bytes_to_hex, chunk_data, flip_hex_byte_order, hex_to_bytes,
    hex_to_int, int_to_hex, int_to_unknown_bytes
)

BIG_INT = 123456789 ** 5
BYTES_BIG = b'TH8\xe2\xaaN\xd7^aX7\x93\xe7\xc6\xa3\x02\x85'
BYTES_LITTLE = b'\x85\x02\xa3\xc6\xe7\x937Xa^\xd7N\xaa\xe28HT'
HEX = '544838e2aa4ed75e61583793e7c6a30285'
ODD_HEX = '4fadd1977328c11efc1c1d8a781aa6b9677984d3e0bd0bfc52b9f3b03885a00'
ODD_HEX_BYTES = (b'\x04\xfa\xdd\x19w2\x8c\x11\xef\xc1\xc1\xd8\xa7\x81'
                 b'\xaak\x96w\x98M>\x0b\xd0\xbf\xc5+\x9f;\x03\x88Z\x00')
ODD_HEX_NUM = 2252489133021925628692706218705147644319767320134875440800653003170737838592


def test_decimal():
    assert Decimal(0.8)==Decimal('0.8')


class TestBytesToHex:
    def test_correct(self):
        assert bytes.fromhex(bytes_to_hex(BYTES_BIG)) == BYTES_BIG

    def test_default(self):
        assert bytes_to_hex(BYTES_BIG) == HEX

    def test_upper(self):
        assert bytes_to_hex(BYTES_BIG, upper=True) == HEX.upper()


class TestIntToUnknownBytes:
    def test_default(self):
        assert int_to_unknown_bytes(BIG_INT) == BYTES_BIG

    def test_little(self):
        assert int_to_unknown_bytes(BIG_INT, 'little') == BYTES_LITTLE

    def test_zero(self):
        assert int_to_unknown_bytes(0) == b'\x00'


class TestIntToHex:
    def test_default(self):
        assert int_to_hex(BIG_INT) == HEX

    def test_upper(self):
        assert int_to_hex(BIG_INT, upper=True) == HEX.upper()


def test_hex_to_bytes():
    assert hex_to_bytes(HEX) == BYTES_BIG
    assert hex_to_bytes(ODD_HEX) == ODD_HEX_BYTES


def test_hex_to_int():
    assert hex_to_int(HEX) == BIG_INT


def test_flip_hex_byte_order():
    assert flip_hex_byte_order(bytes_to_hex(BYTES_LITTLE)) == HEX


def test_chunk_data():
    assert list(chunk_data(ODD_HEX, 2)) == [
        '4f', 'ad', 'd1', '97', '73', '28', 'c1', '1e', 'fc', '1c', '1d',
        '8a', '78', '1a', 'a6', 'b9', '67', '79', '84', 'd3', 'e0', 'bd',
        '0b', 'fc', '52', 'b9', 'f3', 'b0', '38', '85', 'a0', '0'
    ]
