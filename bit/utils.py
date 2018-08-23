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


def int_to_varint(val):

    if val < 253:
        return val.to_bytes(1, 'little')
    elif val <= 65535:
        return b'\xfd'+val.to_bytes(2, 'little')
    elif val <= 4294967295:
        return b'\xfe'+val.to_bytes(4, 'little')
    else:
        return b'\xff'+val.to_bytes(8, 'little')


def script_push(val):

    if val <= 75:
        return int_to_unknown_bytes(val)
    elif val < 256:
        return b'\x4c'+int_to_unknown_bytes(val)
    elif val < 65536:
        return b'\x4d'+val.to_bytes(2, 'little')
    else:
        return b'\x4e'+val.to_bytes(4, 'little')


def get_signatures_from_script(script):
# Expects a (partially)-signed multisig script in bytes and extracts the signatures from it.
    script = script[1:]  # remove the first OP_0

    pos = [0]
    sigs = []

    def read_bytes(bytez):
        pos[0] += bytez
        return script[pos[0]-bytez:pos[0]]

    def read_var_string():
        size = read_var_int()
        return read_bytes(size)

    def read_var_int():
        pos[0] += 1

        if pos[0] > len(script):
            return 0

        val = int(bytes_to_hex(script[pos[0]-1:pos[0]]), base=16)
        if val < 253:
            return val
        return read_as_int(pow(2, val - 252))

    def read_as_int(bytez):
        pos[0] += bytez
        return int(bytes_to_hex(script[pos[0]-bytez:pos[0]][::-1]), base=16)

    val = read_var_int()
    while val <= 72:  # TODO: Make a better check if the data is a signature (using DER rules: https://bitcoin.stackexchange.com/questions/12554/why-the-signature-is-always-65-13232-bytes-long)
        if val != 0:  # For partially-signed scriptSigs the missing signatures are indicated with 0s at the end.
            potential_sig = read_bytes(val)
            if bytes_to_hex(potential_sig[0:1]) == '30':
                sigs.append(potential_sig)
        val = read_var_int()
        if pos[0] > len(script):  # escape if we have run out of the script
            break

    return sigs
