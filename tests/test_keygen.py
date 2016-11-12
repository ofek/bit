import pytest

from bit.keygen import generate_key_address_pair, generate_matching_address


def test_generate_key_address_pair_unique():
    assert generate_key_address_pair() != generate_key_address_pair()


class TestGenerateMatchingAddress:
    def test_generate_matching_address_success(self):
        private_key, address = generate_matching_address('1k')
        assert address.startswith('1k')

    def test_generate_matching_address_invalid_base58(self):
        with pytest.raises(ValueError):
            generate_matching_address('l')

    def test_generate_matching_address_empty(self):
        assert generate_matching_address('')

    def test_generate_matching_address_no_leading_byte(self):
        private_key, address = generate_matching_address('k')
        assert address.startswith('1k')

    def test_generate_matching_address_cores(self):
        assert generate_matching_address('', 'all')
        assert generate_matching_address('', cores=None)
        assert generate_matching_address('', cores=1)
        assert generate_matching_address('', cores=-1)
