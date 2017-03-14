from bit.crypto import (
    DEFAULT_BACKEND, ECDSA_SHA256, NOENCRYPTION, EllipticCurvePrivateKey,
    Encoding, PrivateFormat, load_der_private_key, load_pem_private_key
)
from bit.curve import Point
from bit.exceptions import InvalidSignature
from bit.format import (
    make_compliant_sig, point_to_public_key, hex_to_wif,
    public_key_to_address, wif_to_hex
)
from bit.keygen import derive_private_key, generate_private_key
from bit.network import NetworkApi, get_fee_cached, satoshi_to_currency_cached
from bit.transaction import calc_txid, create_p2pkh_transaction, sanitize_tx_data
from bit.utils import hex_to_int, int_to_hex


def wif_to_key(wif):
    private_key_hex, compressed, version = wif_to_hex(wif)

    if version == 'main':
        if compressed:
            return PrivateKey.from_hex(private_key_hex)
        else:
            return PrivateKey(wif)
    else:
        if compressed:
            return PrivateKeyTestnet.from_hex(private_key_hex)
        else:
            return PrivateKeyTestnet(wif)


class BaseKey:
    """This class represents a point on the elliptic curve secp256k1 and
    provides all necessary cryptographic functionality. You shouldn't use
    this class directly.

    :param wif: A private key serialized to the Wallet Import Format. If the
                argument is not supplied, a new private key will be created.
                The WIF compression flag will be adhered to, but the version
                byte is disregarded. Compression will be used by all new keys.
    :type wif: ``str``
    :raises TypeError: If ``wif`` is not a ``str``.
    """

    def __init__(self, wif=None):
        if wif:
            if isinstance(wif, str):
                private_key_hex, compressed, version = wif_to_hex(wif)
                self._pk = derive_private_key(hex_to_int(private_key_hex))
            elif isinstance(wif, EllipticCurvePrivateKey):
                self._pk = wif
                compressed = True
            else:
                raise TypeError('Wallet Import Format must be a string.')
        else:
            self._pk = generate_private_key()
            compressed = True

        self._public_point = None
        self._public_key = point_to_public_key(
            self._pk.public_key().public_numbers(), compressed=compressed
        )

    @property
    def public_key(self):
        """The public point serialized to bytes."""
        return self._public_key

    @property
    def public_point(self):
        """The public point (x, y)."""
        if self._public_point is None:
            point = self._pk.public_key().public_numbers()
            self._public_point = Point(point.x, point.y)
        return self._public_point

    def sign(self, data):
        """Signs some data which can be verified later by others using
        the public key.

        :param data: The message to sign.
        :type data: ``bytes``
        :returns: A signature compliant with BIP-62.
        :rtype: ``bytes``
        """
        return make_compliant_sig(self._pk.sign(data, ECDSA_SHA256))

    def verify(self, signature, data):
        """Verifies some data was signed by this private key.

        :param signature: The signature to verify.
        :type signature: ``bytes``
        :param data: The data that was supposedly signed.
        :type data: ``bytes``
        :rtype: ``bool``
        """
        try:
            return self._pk.public_key().verify(signature, data, ECDSA_SHA256)
        except InvalidSignature:
            return False

    def to_hex(self):
        """:rtype: ``str``"""
        return int_to_hex(self._pk.private_numbers().private_value)

    def to_der(self):
        """:rtype: ``bytes``"""
        return self._pk.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NOENCRYPTION
        )

    def to_pem(self):
        """:rtype: ``bytes``"""
        return self._pk.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NOENCRYPTION
        )

    def to_int(self):
        """:rtype: ``int``"""
        return self._pk.private_numbers().private_value

    def is_compressed(self):
        """Returns whether or not this private key corresponds to a compressed
        public key.

        :rtype: ``bool``
        """
        return True if len(self.public_key) == 33 else False

    def __eq__(self, other):
        return self.to_int() == other.to_int()


class PrivateKey(BaseKey):
    """This class represents a Bitcoin private key. ``Key`` is an alias.

    :param wif: A private key serialized to the Wallet Import Format. If the
                argument is not supplied, a new private key will be created.
                The WIF compression flag will be adhered to, but the version
                byte is disregarded. Compression will be used by all new keys.
    :type wif: ``str``
    :raises TypeError: If ``wif`` is not a ``str``.
    """

    def __init__(self, wif=None):
        super().__init__(wif=wif)

        self._address = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key, version='main')
        return self._address

    def to_wif(self):
        return hex_to_wif(
            self.to_hex(),
            version='main',
            compressed=self.is_compressed()
        )

    def balance_as(self, currency):
        """Returns your balance as a formatted string in a particular currency.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        """Fetches the current balance by calling
        :func:`~bit.PrivateKey.get_unspents` and returns it using
        :func:`~bit.PrivateKey.balance_as`.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        self.balance = sum(unspent.amount for unspent in self.get_unspents())
        return self.balance_as(currency)

    def get_unspents(self):
        """Fetches all available unspent transaction outputs.

        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """
        self.unspents[:] = NetworkApi.get_unspent(self.address)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkApi.get_transactions(self.address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True,
                           message=None, unspents=None):  # pragma: no cover
        """Creates a signed P2PKH transaction.

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    Bit will poll `<https://bitcoinfees.21.co>`_ and use a fee
                    that will allow your transaction to be confirmed as soon as
                    possible.
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default Bit will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not Bit should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default Bit will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 40 bytes.
        :type message: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """

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
        """Creates a signed P2PKH transaction and attempts to broadcast it on
        the blockchain. This accepts the same arguments as
        :func:`~bit.PrivateKey.create_transaction`.

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    Bit will poll `<https://bitcoinfees.21.co>`_ and use a fee
                    that will allow your transaction to be confirmed as soon as
                    possible.
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default Bit will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not Bit should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default Bit will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 40 bytes.
        :type message: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The transaction ID.
        :rtype: ``str``
        """

        tx_hex = self.create_transaction(
            outputs, fee=fee, leftover=leftover, combine=combine, message=message, unspents=unspents
        )

        NetworkApi.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def from_hex(cls, hexed):
        """
        :param hexed: A private key previously encoded as hex.
        :type hexed: ``str``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(derive_private_key(hex_to_int(hexed)))

    @classmethod
    def from_der(cls, der):
        """
        :param der: A private key previously encoded as DER.
        :type der: ``bytes``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(load_der_private_key(
            der,
            password=None,
            backend=DEFAULT_BACKEND
        ))

    @classmethod
    def from_pem(cls, pem):
        """
        :param pem: A private key previously encoded as PEM.
        :type pem: ``bytes``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(load_pem_private_key(
            pem,
            password=None,
            backend=DEFAULT_BACKEND
        ))

    @classmethod
    def from_int(cls, num):
        """
        :param num: A private key in raw integer form.
        :type num: ``int``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(derive_private_key(num))

    def __repr__(self):
        return '<PrivateKey: {}>'.format(self.address)


class PrivateKeyTestnet(BaseKey):
    """This class represents a testnet Bitcoin private key. **Note:** coins
    on the test network have no monetary value!

    :param wif: A private key serialized to the Wallet Import Format. If the
                argument is not supplied, a new private key will be created.
                The WIF compression flag will be adhered to, but the version
                byte is disregarded. Compression will be used by all new keys.
    :type wif: ``str``
    :raises TypeError: If ``wif`` is not a ``str``.
    """

    def __init__(self, wif=None):
        super().__init__(wif=wif)

        self._address = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key, version='test')
        return self._address

    def to_wif(self):
        return hex_to_wif(
            self.to_hex(),
            version='test',
            compressed=self.is_compressed()
        )

    def balance_as(self, currency):
        """Returns your balance as a formatted string in a particular currency.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        """Fetches the current balance by calling
        :func:`~bit.PrivateKeyTestnet.get_unspents` and returns it using
        :func:`~bit.PrivateKeyTestnet.balance_as`.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        self.balance = sum(unspent.amount for unspent in self.get_unspents())
        return self.balance_as(currency)

    def get_unspents(self):
        """Fetches all available unspent transaction outputs.

        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """
        self.unspents[:] = NetworkApi.get_unspent_testnet(self.address)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkApi.get_transactions_testnet(self.address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True,
                           message=None, unspents=None):
        """Creates a signed P2PKH transaction.

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    Bit will poll `<https://bitcoinfees.21.co>`_ and use a fee
                    that will allow your transaction to be confirmed as soon as
                    possible.
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default Bit will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not Bit should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default Bit will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 40 bytes.
        :type message: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the testnet blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """

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
             message=None, unspents=None):
        """Creates a signed P2PKH transaction and attempts to broadcast it on
        the testnet blockchain. This accepts the same arguments as
        :func:`~bit.PrivateKeyTestnet.create_transaction`.

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    Bit will poll `<https://bitcoinfees.21.co>`_ and use a fee
                    that will allow your transaction to be confirmed as soon as
                    possible.
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default Bit will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not Bit should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default Bit will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 40 bytes.
        :type message: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the testnet blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The transaction ID.
        :rtype: ``str``
        """

        tx_hex = self.create_transaction(
            outputs, fee=fee, leftover=leftover, combine=combine, message=message, unspents=unspents
        )

        NetworkApi.broadcast_tx_testnet(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def from_hex(cls, hexed):
        """
        :param hexed: A private key previously encoded as hex.
        :type hexed: ``str``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(derive_private_key(hex_to_int(hexed)))

    @classmethod
    def from_der(cls, der):
        """
        :param der: A private key previously encoded as DER.
        :type der: ``bytes``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(load_der_private_key(
            der,
            password=None,
            backend=DEFAULT_BACKEND
        ))

    @classmethod
    def from_pem(cls, pem):
        """
        :param pem: A private key previously encoded as PEM.
        :type pem: ``bytes``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(load_pem_private_key(
            pem,
            password=None,
            backend=DEFAULT_BACKEND
        ))

    @classmethod
    def from_int(cls, num):
        """
        :param num: A private key in raw integer form.
        :type num: ``int``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(derive_private_key(num))

    def __repr__(self):
        return '<PrivateKeyTestnet: {}>'.format(self.address)


Key = PrivateKey
