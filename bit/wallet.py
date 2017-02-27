from bit.crypto import (
    DEFAULT_BACKEND, ECDSA_SHA256, NOENCRYPTION, EllipticCurvePrivateKey,
    Encoding, PrivateFormat, load_der_private_key, load_pem_private_key
)
from bit.curve import Point
from bit.exceptions import InvalidSignature
from bit.format import (
    make_compliant_sig, point_to_public_key, private_key_hex_to_wif,
    public_key_to_address, wif_to_private_key_hex
)
from bit.keygen import derive_private_key, generate_private_key
from bit.network import NetworkApi, get_fee_cached, satoshi_to_currency_cached
from bit.transaction import calc_txid, create_p2pkh_transaction, sanitize_tx_data
from bit.utils import hex_to_int, int_to_hex


class BaseKey:
    def __init__(self, wif=None):
        if wif:
            if isinstance(wif, str):
                private_key_hex, compressed = wif_to_private_key_hex(wif)
                self._pk = derive_private_key(hex_to_int(private_key_hex))
            elif isinstance(wif, EllipticCurvePrivateKey):
                self._pk = wif
                compressed = True
            else:
                raise ValueError('Wallet Import Format must be a string.')
        else:
            self._pk = generate_private_key()
            compressed = True

        self._public_point = self._pk.public_key().public_numbers()
        self._public_key = point_to_public_key(
            self._public_point, compressed=compressed
        )

    @property
    def public_key(self):
        return self._public_key

    def public_point(self):
        return Point(self._public_point.x, self._public_point.y)

    def sign(self, data):
        return make_compliant_sig(self._pk.sign(data, ECDSA_SHA256))

    def verify(self, signature, data):
        try:
            return self._pk.public_key().verify(signature, data, ECDSA_SHA256)
        except InvalidSignature:
            return False

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

    def to_int(self):
        return self._pk.private_numbers().private_value

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

    @classmethod
    def from_int(cls, num):
        return PrivateKey(derive_private_key(num))

    def is_compressed(self):
        return True if len(self.public_key) == 33 else False

    def __eq__(self, other):
        return self.to_int() == other.to_int()


class PrivateKey(BaseKey):
    def __init__(self, wif=None):
        super().__init__(wif=wif)

        self._address = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        if self._address is None:
            self._address = public_key_to_address(self._public_key, version='main')
        return self._address

    def to_wif(self):
        return private_key_hex_to_wif(
            self.to_hex(),
            version='main',
            compressed=True if len(self._public_key) == 33 else False
        )

    def balance_as(self, currency):
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        balance = 0
        for unspent in self.get_unspents():
            balance += unspent.amount
        self.balance = balance
        return self.balance_as(currency)

    def get_unspents(self):
        self.unspents[:] = NetworkApi.get_unspent(self.address)
        return self.unspents

    def get_transactions(self):
        self.transactions[:] = NetworkApi.get_transactions(self.address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True,
                           message=None, unspents=None):  # pragma: no cover

        unspents, outputs = sanitize_tx_data(
            unspents or self.unspents,
            outputs,
            fee or get_fee_cached(),
            leftover or self.address,
            combine=combine,
            message=message,
            compressed=self.is_compressed()
        )

        return create_p2pkh_transaction(self, unspents, outputs)

    def send(self, outputs, fee=None, leftover=None, combine=True,
             message=None, unspents=None):  # pragma: no cover

        tx_hex = self.create_transaction(
            outputs, fee=fee, leftover=leftover, combine=combine, message=message, unspents=unspents
        )

        NetworkApi.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    def __repr__(self):
        return '<PrivateKey: {}>'.format(self.address)


class PrivateKeyTestnet(BaseKey):
    def __init__(self, wif=None):
        super().__init__(wif=wif)

        self._address = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        if self._address is None:
            self._address = public_key_to_address(self._public_key, version='test')
        return self._address

    def to_wif(self):
        return private_key_hex_to_wif(
            self.to_hex(),
            version='test',
            compressed=True if len(self._public_key) == 33 else False
        )

    def balance_as(self, currency):
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        balance = 0
        for unspent in self.get_unspents():
            balance += unspent.amount
        self.balance = balance
        return self.balance_as(currency)

    def get_unspents(self):
        self.unspents[:] = NetworkApi.get_test_unspent(self.address)
        return self.unspents

    def get_transactions(self):
        self.transactions[:] = NetworkApi.get_test_transactions(self.address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True, message=None, unspents=None):

        unspents, outputs = sanitize_tx_data(
            unspents or self.unspents,
            outputs,
            fee or get_fee_cached(),
            leftover or self.address,
            combine=combine,
            message=message,
            compressed=self.is_compressed()
        )

        return create_p2pkh_transaction(self, unspents, outputs)

    def send(self, outputs, fee=None, leftover=None, combine=True, message=None, unspents=None):

        tx_hex = self.create_transaction(
            outputs, fee=fee, leftover=leftover, combine=combine, message=message, unspents=unspents
        )

        NetworkApi.broadcast_test_tx(tx_hex)

        return calc_txid(tx_hex)

    def __repr__(self):
        return '<PrivateKeyTestnet: {}>'.format(self.address)


Key = PrivateKey
