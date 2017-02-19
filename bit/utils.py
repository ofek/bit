import decimal
from binascii import hexlify


class Decimal(decimal.Decimal):
    def __new__(cls, value):
        return super().__new__(cls, str(value))


def chunk_data(data, size):
    return (data[i:i + size] for i in range(0, len(data), size))


def int_to_unknown_bytes(num, byteorder='big'):
    """Converts an int to the least number of bytes as possible."""
    return num.to_bytes((num.bit_length() + 7) // 8 or 1, byteorder)


def bytes_to_hex(bytestr, upper=False):
    hexed = hexlify(bytestr).decode()
    return hexed.upper() if upper else hexed


def hex_to_bytes(hexed):

    if len(hexed) & 1:
        hexed = '0' + hexed

    return bytes.fromhex(hexed)


def int_to_hex(num, upper=False):
    hexed = hex(num)[2:]
    return hexed.upper() if upper else hexed


def hex_to_int(hexed):
    return int(hexed, 16)


def flip_hex_byte_order(string):
    return bytes_to_hex(hex_to_bytes(string)[::-1])
