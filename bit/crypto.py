from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import (
    SECP256K1, EllipticCurvePrivateKey, derive_private_key as derive_privkey,
    generate_private_key as gen_privkey
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


def double_sha256_checksum(bytestr):
    hashed = Hash(SHA256, DEFAULT_BACKEND)
    hashed.update(bytestr)
    hashed = hashed.finalize()

    checksum = Hash(SHA256, DEFAULT_BACKEND)
    checksum.update(hashed)
    checksum = checksum.finalize()[:4]

    return checksum
