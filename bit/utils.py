from binascii import hexlify


def int_to_unknown_bytes(num, byteorder='big'):
    """Converts an int to the least number of bytes as possible."""

    if byteorder not in ('big', 'little'):
        raise ValueError('{} is an unrecognized endianness.'.format(byteorder))

    # Round up bit length required to represent number as it is
    # unknown at this point. Doing (bit_length // 8) + 1 is
    # incorrect when length is a multiple of 8.
    return num.to_bytes((num.bit_length() + 7) // 8, byteorder)


def bytes_to_hex(bytestr, upper=True):
    hexed = hexlify(bytestr).decode()
    return hexed.upper() if upper else hexed


def hex_to_bytes(hexed):

    if len(hexed) & 1:
        hexed = '0' + hexed

    return bytes.fromhex(hexed)


def int_to_hex(num, upper=True):
    hexed = hex(num)[2:]
    return hexed.upper() if upper else hexed


def hex_to_int(hexed):
    return int(hexed, 16)


def flip_hex_byte_order(string):
    return bytes_to_hex(hex_to_bytes(string)[::-1])
