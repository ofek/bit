from bit.crypto import EllipticCurvePrivateKey
from bit.keygen import (
    derive_private_key, generate_private_key, generate_key_address_pair
)
from .samples import PRIVATE_KEY_NUM, PUBLIC_KEY_X, PUBLIC_KEY_Y


def test_derive_private_key():
    private_key = derive_private_key(PRIVATE_KEY_NUM)
    public_point = private_key.public_key().public_numbers()
    assert public_point.x == PUBLIC_KEY_X
    assert public_point.y == PUBLIC_KEY_Y


def test_generate_private_key():
    assert isinstance(generate_private_key(), EllipticCurvePrivateKey)


def test_generate_key_address_pair_unique():
    assert generate_key_address_pair() != generate_key_address_pair()
