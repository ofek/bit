from bit.base58 import b58decode_check, b58encode_check
from bit.crypto import (
    DEFAULT_BACKEND, NOENCRYPTION, RIPEMD160, SHA256, Encoding, Hash,
    PrivateFormat, load_der_private_key, load_pem_private_key
)
from bit.curve import x_to_y
from bit.utils import bytes_to_hex

SATOSHI = 1
uBTC = SATOSHI * 100
mBTC = uBTC * 1000
BTC = mBTC * 1000

MAIN_PUBKEY_HASH = b'\x00'
MAIN_SCRIPT_HASH = b'\x05'
MAIN_PRIVATE_KEY = b'\x80'
MAIN_BIP32_PUBKEY = b'\x04\x88\xb2\x1e'
MAIN_BIP32_PRIVKEY = b'\x04\x88\xad\xe4'
TEST_PUBKEY_HASH = b'\x6f'
TEST_SCRIPT_HASH = b'\xc4'
TEST_PRIVATE_KEY = b'\xef'
TEST_BIP32_PUBKEY = b'\x045\x87\xcf'
TEST_BIP32_PRIVKEY = b'\x045\x83\x94'
PUBLIC_KEY_UNCOMPRESSED = b'\x04'
PUBLIC_KEY_COMPRESSED_EVEN_Y = b'\x02'
PUBLIC_KEY_COMPRESSED_ODD_Y = b'\x03'
PRIVATE_KEY_COMPRESSED_PUBKEY = b'\x01'


def private_key_hex_to_wif(private_key, version='main', compressed=False):

    if version == 'test':
        prefix = TEST_PRIVATE_KEY
    else:
        prefix = MAIN_PRIVATE_KEY

    if compressed:
        suffix = PRIVATE_KEY_COMPRESSED_PUBKEY
    else:
        suffix = b''

    if not isinstance(private_key, bytes):
        private_key = bytes.fromhex(private_key)

    private_key = prefix + private_key + suffix

    return b58encode_check(private_key)


def wif_to_private_key_hex(wif):

    private_key = b58decode_check(wif)

    if private_key[:1] not in (MAIN_PRIVATE_KEY, TEST_PRIVATE_KEY):
        raise ValueError('{} does not correspond to a mainnet nor '
                         'testnet address.'.format(private_key[:1]))

    # Remove version byte and, if present, compression flag.
    if len(wif) == 52 and private_key[-1] == 1:
        private_key = private_key[1:-1]
    else:
        private_key = private_key[1:]

    return bytes_to_hex(private_key)


def wif_checksum_check(wif):

    try:
        decoded = b58decode_check(wif)
    except ValueError:
        return False

    if decoded[:1] in (MAIN_PRIVATE_KEY, TEST_PRIVATE_KEY):
        return True

    return False


def public_key_to_address(public_key, version='main'):

    if version == 'test':
        version = TEST_PUBKEY_HASH
    else:
        version = MAIN_PUBKEY_HASH

    length = len(public_key)

    if length == 33:
        flag, x = int.from_bytes(public_key[:1], 'big'), public_key[1:]
        y = x_to_y(int.from_bytes(x, 'big'), flag & 1)
        y = y.to_bytes(32, 'big')
        public_key = PUBLIC_KEY_UNCOMPRESSED + x + y
    elif length != 65:
        raise ValueError('{} is an invalid length for a public key.'.format(length))

    public_key_digest = Hash(SHA256, DEFAULT_BACKEND)
    public_key_digest.update(public_key)
    public_key_digest = public_key_digest.finalize()

    ripemd160 = Hash(RIPEMD160, DEFAULT_BACKEND)
    ripemd160.update(public_key_digest)
    ripemd160 = version + ripemd160.finalize()

    return b58encode_check(ripemd160)


def public_key_to_coords(public_key):

    length = len(public_key)

    if length == 33:
        flag, x = int.from_bytes(public_key[:1], 'big'), int.from_bytes(public_key[1:], 'big')
        y = x_to_y(x, flag & 1)
    elif length == 65:
        x, y = int.from_bytes(public_key[1:33], 'big'), int.from_bytes(public_key[33:], 'big')
    else:
        raise ValueError('{} is an invalid length for a public key.'.format(length))

    return x, y


def coords_to_public_key(x, y, compressed=True):

    if compressed:
        y = PUBLIC_KEY_COMPRESSED_ODD_Y if y & 1 else PUBLIC_KEY_COMPRESSED_EVEN_Y
        return y + x.to_bytes(32, 'big')

    return PUBLIC_KEY_UNCOMPRESSED + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')


def point_to_public_key(point, compressed=True):
    return coords_to_public_key(point.x, point.y, compressed)
