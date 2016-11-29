from decimal import Decimal

from bit.crypto import (
    DEFAULT_BACKEND, ECDSA_SHA256, NOENCRYPTION, EllipticCurvePrivateKey,
    Encoding, PrivateFormat, load_der_private_key, load_pem_private_key
)
from bit.curve import Point
from bit.exceptions import InsufficientFunds, InvalidSignature
from bit.format import (
    BTC, point_to_public_key, private_key_hex_to_wif, public_key_to_address,
    wif_to_private_key_hex
)
from bit.keygen import derive_private_key, generate_private_key
from bit.network import MultiBackend
from bit.transaction import create_signed_transaction, estimate_tx_fee
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

        public_point = self._pk.public_key().public_numbers()
        self._public_point = Point(public_point.x, public_point.y)
        self._public_key = point_to_public_key(public_point, compressed=compressed)

    def public_key(self):
        return self._public_key

    def public_point(self):
        return self._public_point

    def sign(self, data):
        return self._pk.sign(data, ECDSA_SHA256)

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


class PrivateKey(BaseKey):
    def __init__(self, wif=None, sync=False):
        super().__init__(wif=wif)

        self._address = public_key_to_address(self._public_key, version='main')

        self._balance = None
        self._utxos = []
        self._transactions = []

        if sync:
            self.sync()

    @property
    def address(self):
        return self._address

    def to_wif(self):
        return private_key_hex_to_wif(
            self.to_hex(),
            version='main',
            compressed=True if len(self._public_key) == 33 else False
        )

    def get_balance(self):
        self._balance = MultiBackend.get_balance(self._address)
        return self._balance

    def get_utxos(self):
        self._utxos[:] = MultiBackend.get_utxo_list(self._address)
        return self._utxos.copy()

    def get_transactions(self):
        self._transactions[:] = MultiBackend.get_tx_list(self._address)
        return self._transactions.copy()

    def sync(self):
        self._balance = MultiBackend.get_balance(self._address)
        self._utxos[:] = MultiBackend.get_utxo_list(self._address)
        self._transactions[:] = MultiBackend.get_tx_list(self._address)

    def create_tx(self, outputs, fee=None, combine=True, extra=None, utxos=None):
        return_address = extra or self.address
        utxos = utxos.copy() if utxos else self.get_utxos()

        fee = Decimal(estimate_tx_fee(
            len(utxos), len(outputs), fee or MultiBackend.get_tx_fee()
        )) / BTC
        total_in = Decimal('0')
        total_out = sum(Decimal(str(out[1])) for out in outputs) + fee

        if not combine:
            utxos.sort(key=lambda x: x['amount'])

            index = 0

            for index, utxo in enumerate(utxos):
                total_in += utxo['amount']

                if total_in >= total_out:
                    break

            utxos[:] = utxos[:index + 1]

        else:
            total_in = sum(utxo['amount'] for utxo in utxos)

        leftover = total_in - total_out

        if leftover:
            outputs.append((return_address, leftover))
        elif leftover < 0:
            raise InsufficientFunds('Balance {} is less than {} (including fee).'
                                    ''.format(total_in, total_out))

        return create_signed_transaction(self, utxos, outputs)

    def balance(self):
        return self._balance

    def utxos(self):
        return self._utxos.copy()

    def transactions(self):
        return self._transactions.copy()

    def __repr__(self):
        return '<PrivateKey: {}>'.format(self.address)


class PrivateKeyTestnet(BaseKey):
    def __init__(self, wif=None, sync=False):
        super().__init__(wif=wif)

        self._address = public_key_to_address(self._public_key, version='test')

        self._balance = None
        self._utxos = []
        self._transactions = []

        if sync:
            self.sync()

    @property
    def address(self):
        return self._address

    def to_wif(self):
        return private_key_hex_to_wif(
            self.to_hex(),
            version='test',
            compressed=True if len(self._public_key) == 33 else False
        )

    def get_balance(self):
        self._balance = MultiBackend.get_test_balance(self._address)
        return self._balance

    def get_utxos(self):
        self._utxos[:] = MultiBackend.get_test_utxo_list(self._address)
        return self._utxos.copy()

    def get_transactions(self):
        self._transactions[:] = MultiBackend.get_test_tx_list(self._address)
        return self._transactions.copy()

    def sync(self):
        self._balance = MultiBackend.get_test_balance(self._address)
        self._utxos[:] = MultiBackend.get_test_utxo_list(self._address)
        self._transactions[:] = MultiBackend.get_test_tx_list(self._address)

    def create_tx(self, outputs, fee=None, combine=True, extra=None, utxos=None):
        return_address = extra or self.address
        utxos = utxos.copy() if utxos else self.get_utxos()

        fee = estimate_tx_fee(
            len(utxos), len(outputs), fee or MultiBackend.get_tx_fee()
        )
        total_in = Decimal('0')
        total_out = sum(Decimal(str(out[1])) for out in outputs) + fee

        if not combine:
            utxos.sort(key=lambda x: x.amount)

            index = 0

            for index, utxo in enumerate(utxos):
                total_in += utxo.amount

                if total_in >= total_out:
                    break

            utxos[:] = utxos[:index + 1]

        else:
            total_in = sum(utxo.amount for utxo in utxos)

        leftover = total_in - total_out

        if leftover:
            outputs.append((return_address, leftover))
        elif leftover < 0:
            raise InsufficientFunds('Balance {} is less than {} (including fee).'
                                    ''.format(total_in, total_out))

        print(outputs, utxos)
        return create_signed_transaction(self, utxos, outputs)

    def send(self, outputs, fee=None, combine=True, extra=None, utxos=None):
        tx_hex = self.create_tx(outputs, fee=fee, combine=combine, extra=extra, utxos=utxos)
        MultiBackend.broadcast_test_tx(tx_hex)

    def balance(self):
        return self._balance

    def utxos(self):
        return self._utxos.copy()

    def transactions(self):
        return self._transactions.copy()

    def __repr__(self):
        return '<PrivateKeyTestnet: {}>'.format(self.address)


Key = PrivateKey
