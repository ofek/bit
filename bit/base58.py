from collections import deque

from bit.crypto import double_sha256_checksum
from bit.utils import int_to_unknown_bytes

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
BASE58_ALPHABET_LIST = list(BASE58_ALPHABET)
BASE58_ALPHABET_INDEX = {char: index for index, char in enumerate(BASE58_ALPHABET)}


def b58encode(bytestr):

    alphabet = BASE58_ALPHABET_LIST

    encoded = deque()
    append = encoded.appendleft
    _divmod = divmod

    num = int.from_bytes(bytestr, 'big')

    while num > 0:
        num, rem = _divmod(num, 58)
        append(alphabet[rem])

    encoded = ''.join(encoded)

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

    alphabet_index = BASE58_ALPHABET_INDEX

    num = 0

    try:
        for char in string:
            num *= 58
            num += alphabet_index[char]
    except KeyError:
        raise ValueError('"{}" is an invalid base58 encoded '
                         'character.'.format(char)) from None

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
