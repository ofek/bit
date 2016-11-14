from binascii import hexlify


def int_to_unknown_bytes(num, endian='big'):
    """Converts an int to the least number of bytes as possible."""

    if endian not in ('big', 'little'):
        raise ValueError('{} is an unrecognized endianness.'.format(endian))

    # Round up bit length required to represent number as it is
    # unknown at this point. Doing (bit_length // 8) + 1 is
    # incorrect when length is a multiple of 8.
    return num.to_bytes((num.bit_length() + 7) // 8, endian)


def bytes_to_hex(bytestr, upper=True):
    hexlified = hexlify(bytestr).decode()
    return hexlified.upper() if upper else hexlified


def int_to_hex(num, upper=True):
    hexlified = hex(num)[2:]
    return hexlified.upper() if upper else hexlified
