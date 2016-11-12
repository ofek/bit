from bit.utils import bytes_to_hex, int_to_hex, int_to_unknown_bytes

BIG_INT = 123456789 ** 5
BYTES = b'TH8\xe2\xaaN\xd7^aX7\x93\xe7\xc6\xa3\x02\x85'
HEX = '544838E2AA4ED75E61583793E7C6A30285'


class TestBytesToHex:
    def test_bytes_to_hex_default(self):
        assert bytes.fromhex(bytes_to_hex(BYTES)) == BYTES

    def test_bytes_to_hex_normal(self):
        assert bytes_to_hex(BYTES, upper=False) == HEX.lower()


def test_int_to_unknown_bytes():
    assert int_to_unknown_bytes(BIG_INT) == BYTES


def test_int_to_hex():
    assert int_to_hex(BIG_INT) == HEX
