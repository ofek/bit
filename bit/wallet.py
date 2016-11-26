from bit.crypto import (
    DEFAULT_BACKEND, NOENCRYPTION, EllipticCurvePrivateKey, Encoding,
    PrivateFormat, load_der_private_key, load_pem_private_key
)
from bit.curve import Point
from bit.format import (
    point_to_public_key, private_key_hex_to_wif, public_key_to_address,
    wif_to_private_key_hex
)
from bit.keygen import derive_private_key, generate_private_key
from bit.network import MultiBackend
from bit.utils import hex_to_int, int_to_hex


class PrivateKey:
    def __init__(self, wif=None, sync=False):
        if wif:
            if isinstance(wif, str):
                num = hex_to_int(wif_to_private_key_hex(wif))
                self._pk = derive_private_key(num)
            elif isinstance(wif, EllipticCurvePrivateKey):
                self._pk = wif
            else:
                raise ValueError('Wallet Import Format must be a string.')
        else:
            self._pk = generate_private_key()

        public_point = self._pk.public_key().public_numbers()
        pubkey = point_to_public_key(public_point, compressed=False)

        self._public_point = Point(public_point.x, public_point.y)
        self._address = public_key_to_address(pubkey)
        self._test_address = public_key_to_address(pubkey, version='test')

        self._balance = None
        self._utxo = []
        self._transactions = []

        self._test_balance = None
        self._test_utxo = []
        self._test_transactions = []

        if sync:
            self.sync()

    def public_key(self, compressed=True):
        return point_to_public_key(self._public_point, compressed=compressed)

    def get_balance(self):
        self._balance = MultiBackend.get_balance(self._address)
        return self._balance

    def get_utxo(self):
        self._utxo[:] = MultiBackend.get_utxo_list(self._address)
        return self._utxo.copy()

    def get_transactions(self):
        self._transactions[:] = MultiBackend.get_tx_list(self._address)
        return self._transactions.copy()

    def sync(self):
        self._balance = MultiBackend.get_balance(self._address)
        self._utxo[:] = MultiBackend.get_utxo_list(self._address)
        self._transactions[:] = MultiBackend.get_tx_list(self._address)

    def get_test_balance(self):
        self._test_balance = MultiBackend.get_test_balance(self._test_address)
        return self._test_balance

    def get_test_utxo(self):
        self._test_utxo[:] = MultiBackend.get_test_utxo_list(self._test_address)
        return self._test_utxo.copy()

    def get_test_transactions(self):
        self._test_transactions[:] = MultiBackend.get_test_tx_list(self._test_address)
        return self._test_transactions.copy()

    def test_sync(self):
        self._test_balance = MultiBackend.get_test_balance(self._test_address)
        self._test_utxo[:] = MultiBackend.get_test_utxo_list(self._test_address)
        self._test_transactions[:] = MultiBackend.get_test_tx_list(self._test_address)

    def to_wif(self, version='main', compressed=False):
        return private_key_hex_to_wif(self.to_hex(), version, compressed)

    def to_hex(self):
        return int_to_hex(self._pk.private_numbers().private_value)

    def to_der(self):
        return self._pk.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NOENCRYPTION
        )

    def to_pem(self):
        return self._pk.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NOENCRYPTION
        )

    @classmethod
    def from_hex(cls, hexed):
        return PrivateKey(derive_private_key(hex_to_int(hexed)))

    @classmethod
    def from_der(cls, der):
        return PrivateKey(load_der_private_key(
            der,
            password=None,
            backend=DEFAULT_BACKEND
        ))

    @classmethod
    def from_pem(cls, pem):
        return PrivateKey(load_pem_private_key(
            pem,
            password=None,
            backend=DEFAULT_BACKEND
        ))

    @property
    def public_point(self):
        return self._public_point

    @property
    def address(self):
        return self._address

    @property
    def balance(self):
        return self._balance

    @property
    def utxo(self):
        return self._utxo.copy()

    @property
    def transactions(self):
        return self._transactions.copy()

    @property
    def test_address(self):
        return self._test_address

    @property
    def test_balance(self):
        return self._test_balance

    @property
    def test_utxo(self):
        return self._test_utxo.copy()

    @property
    def test_transactions(self):
        return self._test_transactions.copy()

Key = PrivateKey








