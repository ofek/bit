from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import (
    SECP256K1, ECDSA, EllipticCurvePrivateKey,
    derive_private_key as derive_privkey,
    generate_private_key as gen_privkey
)
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature
)
from cryptography.hazmat.primitives.hashes import RIPEMD160, SHA256, Hash
from cryptography.hazmat.primitives.serialization import (
    Encoding, NoEncryption, PrivateFormat, load_der_private_key, load_pem_private_key
)

# Memoize instances across application
DEFAULT_BACKEND = default_backend()
NOENCRYPTION = NoEncryption()
RIPEMD160 = RIPEMD160()
SECP256K1 = SECP256K1()
SHA256 = SHA256()
ECDSA_SHA256 = ECDSA(SHA256)


def sha256(bytestr):
    hash = Hash(SHA256, DEFAULT_BACKEND)
    hash.update(bytestr)
    hash = hash.finalize()

    return hash


def double_sha256(bytestr):
    hash1 = Hash(SHA256, DEFAULT_BACKEND)
    hash1.update(bytestr)
    hash1 = hash1.finalize()

    hash2 = Hash(SHA256, DEFAULT_BACKEND)
    hash2.update(hash1)
    hash2 = hash2.finalize()

    return hash2


def double_sha256_checksum(bytestr):
    return double_sha256(bytestr)[:4]
