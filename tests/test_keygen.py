from bit.keygen import generate_key_address_pair


def test_generate_key_address_pair_unique():
    assert generate_key_address_pair() != generate_key_address_pair()
