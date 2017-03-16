from hashlib import new, sha256 as _sha256

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import (
    SECP256K1, ECDSA, EllipticCurvePrivateKey,
    derive_private_key as derive_privkey,
    generate_private_key as gen_privkey
)
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature
)
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (
    Encoding, NoEncryption, PrivateFormat, load_der_private_key, load_pem_private_key
)

# Memoize instances across application
DEFAULT_BACKEND = default_backend()
NOENCRYPTION = NoEncryption()
SECP256K1 = SECP256K1()
ECDSA_SHA256 = ECDSA(SHA256())


def sha256(bytestr):
    return _sha256(bytestr).digest()


def double_sha256(bytestr):
    return _sha256(_sha256(bytestr).digest()).digest()


def double_sha256_checksum(bytestr):
    return double_sha256(bytestr)[:4]


def ripemd160_sha256(bytestr):
    return new('ripemd160', sha256(bytestr)).digest()

hash160 = ripemd160_sha256
