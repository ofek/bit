from bit.crypto import double_sha256_checksum
from bit.utils import int_to_unknown_bytes

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def b58encode(bytestr):

    alphabet = BASE58_ALPHABET

    num = int.from_bytes(bytestr, 'big')
    encoded = []

    while num > 0:
        num, rem = divmod(num, 58)
        encoded.append(alphabet[rem])

    # Reverse to order by significance of bits
    encoded = ''.join(reversed(encoded))

    pad = 0
    for byte in bytestr:
        if byte == 0:
            pad += 1
        else:
            break

    return '1' * pad + encoded


def b58encode_check(bytestr):
    return b58encode(bytestr + double_sha256_checksum(bytestr))


def b58decode(string):

    alphabet = BASE58_ALPHABET

    num = 0
    for char in string:
        num *= 58

        try:
            index = alphabet.index(char)
        except ValueError:
            raise ValueError('"{}" is an invalid base58 encoded '
                             'character.'.format(char)) from None
        num += index

    bytestr = int_to_unknown_bytes(num)

    pad = 0
    for char in string:
        if char == '1':
            pad += 1
        else:
            break

    return b'\x00' * pad + bytestr


def b58decode_check(string):

    decoded = b58decode(string)
    shortened = decoded[:-4]
    decoded_checksum = decoded[-4:]
    hash_checksum = double_sha256_checksum(shortened)

    if decoded_checksum != hash_checksum:
        raise ValueError('Decoded checksum {} derived from "{}" is not equal to hash '
                         'checksum {}.'.format(decoded_checksum, string, hash_checksum))

    return shortened
