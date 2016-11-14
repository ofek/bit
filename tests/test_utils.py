import pytest

from bit.utils import bytes_to_hex, int_to_hex, int_to_unknown_bytes

BIG_INT = 123456789 ** 5
BYTES_BIG = b'TH8\xe2\xaaN\xd7^aX7\x93\xe7\xc6\xa3\x02\x85'
BYTES_LITTLE = b'\x85\x02\xa3\xc6\xe7\x937Xa^\xd7N\xaa\xe28HT'
HEX = '544838E2AA4ED75E61583793E7C6A30285'


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










