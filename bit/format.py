from coincurve import verify_signature as _vs

from bit.base58 import b58decode_check, b58encode_check
from bit.crypto import ripemd160_sha256, sha256
from bit.curve import x_to_y

from bit.utils import int_to_unknown_bytes, hex_to_bytes, script_push
from bit.base32 import bech32_decode
from bit.constants import (
    BECH32_MAIN_VERSION_SET, BECH32_TEST_VERSION_SET, MAIN_PUBKEY_HASH,
    MAIN_SCRIPT_HASH, MAIN_PRIVATE_KEY, TEST_PUBKEY_HASH, TEST_SCRIPT_HASH,
    TEST_PRIVATE_KEY, PUBLIC_KEY_UNCOMPRESSED, PUBLIC_KEY_COMPRESSED_EVEN_Y,
    PUBLIC_KEY_COMPRESSED_ODD_Y, PRIVATE_KEY_COMPRESSED_PUBKEY
)


def verify_sig(signature, data, public_key):
    """Verifies some data was signed by the owner of a public key.

    :param signature: The signature to verify.
    :type signature: ``bytes``
    :param data: The data that was supposedly signed.
    :type data: ``bytes``
    :param public_key: The public key.
    :type public_key: ``bytes``
    :returns: ``True`` if all checks pass, ``False`` otherwise.
    """
    return _vs(signature, data, public_key)


def address_to_public_key_hash(address):
    # Raise ValueError if we cannot identify the address.
    get_version(address)
    return b58decode_check(address)[1:]


def get_version(address):
    version, _ = bech32_decode(address)
    if version is None:
            version = b58decode_check(address)[:1]
    if (version in (MAIN_PUBKEY_HASH, MAIN_SCRIPT_HASH) or
        version in BECH32_MAIN_VERSION_SET):
        return 'main'
    elif (version in (TEST_PUBKEY_HASH, TEST_SCRIPT_HASH) or
          version in BECH32_TEST_VERSION_SET):
        return 'test'
    else:
        raise ValueError('{} does not correspond to a mainnet nor '
                         'testnet address.'.format(version))


def bytes_to_wif(private_key, version='main', compressed=False):

    if version == 'test':
        prefix = TEST_PRIVATE_KEY
    else:
        prefix = MAIN_PRIVATE_KEY

    if compressed:
        suffix = PRIVATE_KEY_COMPRESSED_PUBKEY
    else:
        suffix = b''

    private_key = prefix + private_key + suffix

    return b58encode_check(private_key)


def wif_to_bytes(wif):

    private_key = b58decode_check(wif)

    version = private_key[:1]

    if version == MAIN_PRIVATE_KEY:
        version = 'main'
    elif version == TEST_PRIVATE_KEY:
        version = 'test'
    else:
        raise ValueError('{} does not correspond to a mainnet nor '
                         'testnet address.'.format(version))

    # Remove version byte and, if present, compression flag.
    if len(wif) == 52 and private_key[-1] == 1:
        private_key, compressed = private_key[1:-1], True
    else:
        private_key, compressed = private_key[1:], False

    return private_key, compressed, version


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

    if length not in (33, 65):
        raise ValueError('{} is an invalid length for a public key.'.format(length))

    return b58encode_check(version + ripemd160_sha256(public_key))


def public_key_to_segwit_address(public_key, version='main'):

    if version == 'test':
        version = TEST_SCRIPT_HASH
    else:
        version = MAIN_SCRIPT_HASH

    length = len(public_key)

    if length != 33:
        raise ValueError('{} is an invalid length for a public key. Segwit only uses compressed public keys'.format(length))

    return b58encode_check(version + ripemd160_sha256(b'\x00\x14' + ripemd160_sha256(public_key)))


def multisig_to_redeemscript(public_keys, m):

    if m > len(public_keys):
        raise ValueError('Required signatures cannot be more than the total number of public keys.')

    redeemscript = int_to_unknown_bytes(m + 80)

    for key in public_keys:
        length = len(key)

        if length not in (33, 65):
            raise ValueError('At least one of the provided public keys is of invalid length {}.'.format(length))

        redeemscript += script_push(length) + key

    redeemscript += int_to_unknown_bytes(len(public_keys) + 80) + b'\xae'  # Only works for n = len(public_keys) < 17. OK due to P2SH script-length limitation.

    if len(redeemscript) > 520:
        raise ValueError('The redeemScript exceeds the allowed 520-byte limitation with the number of public keys.')

    return redeemscript


def multisig_to_address(public_keys, m, version='main'):
    if version == 'test':
        version = TEST_SCRIPT_HASH
    else:
        version = MAIN_SCRIPT_HASH

    return b58encode_check(version + ripemd160_sha256(multisig_to_redeemscript(public_keys, m)))


def multisig_to_segwit_address(public_keys, m, version='main'):
    if version == 'test':
        version = TEST_SCRIPT_HASH
    else:
        version = MAIN_SCRIPT_HASH

    return b58encode_check(version + ripemd160_sha256(b'\x00\x20' + sha256(multisig_to_redeemscript(public_keys, m))))


def segwit_scriptpubkey(witver, witprog):
    """Construct a Segwit scriptPubKey for a given witness program."""
    return bytes([witver + 0x50 if witver else 0, len(witprog)] + witprog)


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
