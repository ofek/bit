from hashlib import algorithms_available, new
from hashlib import sha256 as _sha256

from coincurve import PrivateKey as ECPrivateKey
from coincurve import PublicKey as ECPublicKey

from .ripemd160 import ripemd160 as r160


def sha256(bytestr):
    return _sha256(bytestr).digest()


def double_sha256(bytestr):
    return _sha256(_sha256(bytestr).digest()).digest()


def double_sha256_checksum(bytestr):
    return double_sha256(bytestr)[:4]


def ripemd160_sha256(bytestr):
    return new('ripemd160', sha256(bytestr)).digest() if "ripemd160" in algorithms_available else r160(sha256(bytestr))


hash160 = ripemd160_sha256
