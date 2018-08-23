import json

from bit.crypto import ECPrivateKey
from bit.curve import Point
from bit.format import (
    bytes_to_wif, public_key_to_address, public_key_to_coords, wif_to_bytes, address_to_public_key_hash, multisig_to_address, multisig_to_redeemscript,
)
from bit.network import NetworkAPI, get_fee_cached, satoshi_to_currency_cached
from bit.network.meta import Unspent
from bit.transaction import (
    calc_txid, create_new_transaction, sanitize_tx_data, sign_legacy_tx,
    OP_CHECKSIG, OP_DUP, OP_EQUALVERIFY, OP_HASH160, OP_PUSH_20
    )

from bit.utils import bytes_to_hex

def wif_to_key(wif):
    private_key_bytes, compressed, version = wif_to_bytes(wif)

    if version == 'main':
        if compressed:
            return PrivateKey.from_bytes(private_key_bytes)
        else:
            return PrivateKey(wif)
    else:
        if compressed:
            return PrivateKeyTestnet.from_bytes(private_key_bytes)
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
                private_key_bytes, compressed, version = wif_to_bytes(wif)
                self._pk = ECPrivateKey(private_key_bytes)
            elif isinstance(wif, ECPrivateKey):
                self._pk = wif
                compressed = True
            else:
                raise TypeError('Wallet Import Format must be a string.')
        else:
            self._pk = ECPrivateKey()
            compressed = True

        self._public_point = None
        self._public_key = self._pk.public_key.format(compressed=compressed)

    @property
    def public_key(self):
        """The public point serialized to bytes."""
        return self._public_key

    @property
    def public_point(self):
        """The public point (x, y)."""
        if self._public_point is None:
            self._public_point = Point(*public_key_to_coords(self._public_key))
        return self._public_point

    def sign(self, data):
        """Signs some data which can be verified later by others using
        the public key.

        :param data: The message to sign.
        :type data: ``bytes``
        :returns: A signature compliant with BIP-62.
        :rtype: ``bytes``
        """
        return self._pk.sign(data)

    def verify(self, signature, data):
        """Verifies some data was signed by this private key.

        :param signature: The signature to verify.
        :type signature: ``bytes``
        :param data: The data that was supposedly signed.
        :type data: ``bytes``
        :rtype: ``bool``
        """
        return self._pk.public_key.verify(signature, data)

    def pub_to_hex(self):
        """:rtype: ``str`` """
        return bytes_to_hex(self.public_key)

    def to_hex(self):
        """:rtype: ``str``"""
        return self._pk.to_hex()

    def to_bytes(self):
        """:rtype: ``bytes``"""
        return self._pk.secret

    def to_der(self):
        """:rtype: ``bytes``"""
        return self._pk.to_der()

    def to_pem(self):
        """:rtype: ``bytes``"""
        return self._pk.to_pem()

    def to_int(self):
        """:rtype: ``int``"""
        return self._pk.to_int()

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
        self._scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

        self.instance = 'PrivateKey'

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key, version='main')
        return self._address

    @property
    def scriptcode(self):
        self._scriptcode = (OP_DUP + OP_HASH160 + OP_PUSH_20 +
                            address_to_public_key_hash(self.address) +
                            OP_EQUALVERIFY + OP_CHECKSIG)
        return self._scriptcode

    def to_wif(self):
        return bytes_to_wif(
            self._pk.secret,
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
        self.get_unspents()
        return self.balance_as(currency)

    def get_unspents(self):
        """Fetches all available unspent transaction outputs.

        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """
        self.unspents[:] = NetworkAPI.get_unspent(self.address)
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkAPI.get_transactions(self.address)
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
                    Bit will poll `<https://bitcoinfees.earn.com>`_ and use a fee
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

        return create_new_transaction(self, unspents, outputs)

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
                    Bit will poll `<https://bitcoinfees.earn.com>`_ and use a fee
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

        NetworkAPI.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None, leftover=None,
                            combine=True, message=None, unspents=None):  # pragma: no cover
        """Prepares a P2PKH transaction for offline signing.

        :param address: The address the funds will be sent from.
        :type address: ``str``
        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param compressed: Whether or not the ``address`` corresponds to a
                           compressed public key. This influences the fee.
        :type compressed: ``bool``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    Bit will poll `<https://bitcoinfees.earn.com>`_ and use a fee
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
        :returns: JSON storing data required to create an offline transaction.
        :rtype: ``str``
        """
        unspents, outputs = sanitize_tx_data(
            unspents or NetworkAPI.get_unspent(address),
            outputs,
            fee or get_fee_cached(),
            leftover or address,
            combine=combine,
            message=message,
            compressed=compressed
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data):  # pragma: no cover
        """Creates a signed P2PKH transaction using previously prepared
        transaction data.

        :param tx_data: Output of :func:`~bit.PrivateKey.prepare_transaction`.
        :type tx_data: ``str``
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        data = json.loads(tx_data)

        unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
        outputs = data['outputs']

        return create_new_transaction(self, unspents, outputs)

    @classmethod
    def from_hex(cls, hexed):
        """
        :param hexed: A private key previously encoded as hex.
        :type hexed: ``str``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_hex(hexed))

    @classmethod
    def from_bytes(cls, bytestr):
        """
        :param bytestr: A private key previously encoded as hex.
        :type bytestr: ``bytes``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(ECPrivateKey(bytestr))

    @classmethod
    def from_der(cls, der):
        """
        :param der: A private key previously encoded as DER.
        :type der: ``bytes``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_der(der))

    @classmethod
    def from_pem(cls, pem):
        """
        :param pem: A private key previously encoded as PEM.
        :type pem: ``bytes``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_pem(pem))

    @classmethod
    def from_int(cls, num):
        """
        :param num: A private key in raw integer form.
        :type num: ``int``
        :rtype: :class:`~bit.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_int(num))

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

        self.instance = 'PrivateKeyTestnet'

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key, version='test')
        return self._address

    @property
    def scriptcode(self):
        self._scriptcode = (OP_DUP + OP_HASH160 + OP_PUSH_20 +
                            address_to_public_key_hash(self.address) +
                            OP_EQUALVERIFY + OP_CHECKSIG)
        return self._scriptcode

    def to_wif(self):
        return bytes_to_wif(
            self._pk.secret,
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
        self.get_unspents()
        return self.balance_as(currency)

    def get_unspents(self):
        """Fetches all available unspent transaction outputs.

        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """
        self.unspents[:] = NetworkAPI.get_unspent_testnet(self.address)
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkAPI.get_transactions_testnet(self.address)
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
                    Bit will poll `<https://bitcoinfees.earn.com>`_ and use a fee
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

        return create_new_transaction(self, unspents, outputs)

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
                    Bit will poll `<https://bitcoinfees.earn.com>`_ and use a fee
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

        NetworkAPI.broadcast_tx_testnet(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None, leftover=None,
                            combine=True, message=None, unspents=None):
        """Prepares a P2PKH transaction for offline signing.

        :param address: The address the funds will be sent from.
        :type address: ``str``
        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param compressed: Whether or not the ``address`` corresponds to a
                           compressed public key. This influences the fee.
        :type compressed: ``bool``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    Bit will poll `<https://bitcoinfees.earn.com>`_ and use a fee
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
        :returns: JSON storing data required to create an offline transaction.
        :rtype: ``str``
        """
        unspents, outputs = sanitize_tx_data(
            unspents or NetworkAPI.get_unspent_testnet(address),
            outputs,
            fee or get_fee_cached(),
            leftover or address,
            combine=combine,
            message=message,
            compressed=compressed
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data):
        """Creates a signed P2PKH transaction using previously prepared
        transaction data.

        :param tx_data: Output of :func:`~bit.PrivateKeyTestnet.prepare_transaction`.
        :type tx_data: ``str``
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        data = json.loads(tx_data)

        unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
        outputs = data['outputs']

        return create_new_transaction(self, unspents, outputs)

    @classmethod
    def from_hex(cls, hexed):
        """
        :param hexed: A private key previously encoded as hex.
        :type hexed: ``str``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(ECPrivateKey.from_hex(hexed))

    @classmethod
    def from_bytes(cls, bytestr):
        """
        :param bytestr: A private key previously encoded as hex.
        :type bytestr: ``bytes``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(ECPrivateKey(bytestr))

    @classmethod
    def from_der(cls, der):
        """
        :param der: A private key previously encoded as DER.
        :type der: ``bytes``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(ECPrivateKey.from_der(der))

    @classmethod
    def from_pem(cls, pem):
        """
        :param pem: A private key previously encoded as PEM.
        :type pem: ``bytes``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(ECPrivateKey.from_pem(pem))

    @classmethod
    def from_int(cls, num):
        """
        :param num: A private key in raw integer form.
        :type num: ``int``
        :rtype: :class:`~bit.PrivateKeyTestnet`
        """
        return PrivateKeyTestnet(ECPrivateKey.from_int(num))

    def __repr__(self):
        return '<PrivateKeyTestnet: {}>'.format(self.address)


Key = PrivateKey

class MultiSig:
    """This class represents a Bitcoin multisignature contract.
    **Note:** coins on the test network have no monetary value!

    :param private_key: A class representing a private key.
    :type private_key: ``PrivateKey``
    :raises TypeError: If ``private_key`` is not a ``PrivateKey``.
    :param public_keys: A list of public keys encoded as hex assigned
                        to the multi-signature contract.
    :type public_keys: ``list`` of ``str``
    :raises TypeError: When the list ``public_keys`` does not include the public
                       key corresponding to the private key used in this class.
    :param m: The number of required signatures to spend from this multi-
              signature contract.
    :type m: ``int``
    """

    def __init__(self, private_key, public_keys, m):

        if private_key.instance != 'PrivateKey':
            raise TypeError('MultiSig only accepts a PrivateKey class to assign a private key.')

        self._pk = private_key

        self.version = 'main'
        self._address = None
        self._scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

        self.instance = 'MultiSig'

        if bytes_to_hex(private_key.public_key) not in public_keys:
            raise TypeError('Private key does not match any provided public key.')
        else:
            self.public_key = private_key.public_key
            self.public_keys = public_keys
            self.m = m
            self.redeemscript = multisig_to_redeemscript(public_keys, self.m)

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = multisig_to_address(self.public_keys, self.m, version=self.version)
        return self._address

    @property
    def scriptcode(self):
        self._scriptcode = self.redeemscript
        return self._scriptcode

    def sign(self, data):
        """Signs some data which can be verified later by others using
        the public key.

        :param data: The message to sign.
        :type data: ``bytes``
        :returns: A signature compliant with BIP-62.
        :rtype: ``bytes``
        """
        return self._pk.sign(data)

    def balance_as(self, currency):
        """Returns your balance as a formatted string in a particular currency.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        """Fetches the current balance by calling
        :func:`~bit.MultiSig.get_unspents` and returns it using
        :func:`~bit.MultiSig.balance_as`.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        self.get_unspents()
        return self.balance_as(currency)

    def get_unspents(self):
        """Fetches all available unspent transaction outputs.

        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """
        if self.version == 'test':
            self.unspents[:] = NetworkAPI.get_unspent_testnet(self.address)
        else:
            self.unspents[:] = NetworkAPI.get_unspent(self.address)
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        if self.version == 'test':
            self.transactions[:] = NetworkAPI.get_transactions_testnet(self.address)
        else:
            self.transactions[:] = NetworkAPI.get_transactions(self.address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True,
                           message=None, unspents=None):
        """Creates a signed P2SH transaction.

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
            compressed=self._pk.is_compressed()
        )

        return create_new_transaction(self, unspents, outputs)

    def send(self, outputs, fee=None, leftover=None, combine=True,
             message=None, unspents=None):  # pragma: no cover
        """Creates a signed P2SH transaction and attempts to broadcast it on
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

        NetworkAPI.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None, leftover=None,
                            combine=True, message=None, unspents=None):  # pragma: no cover
        """Prepares a P2SH transaction for offline signing.

        :param address: The address the funds will be sent from.
        :type address: ``str``
        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param compressed: Whether or not the ``address`` corresponds to a
                           compressed public key. This influences the fee.
        :type compressed: ``bool``
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
        :returns: JSON storing data required to create an offline transaction.
        :rtype: ``str``
        """
        unspents, outputs = sanitize_tx_data(
            unspents or NetworkAPI.get_unspent(address),
            outputs,
            fee or get_fee_cached(),
            leftover or address,
            combine=combine,
            message=message,
            compressed=compressed
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data):  # pragma: no cover
        """Creates a signed P2SH transaction using previously prepared
        transaction data.

        :param tx_data: Hex-encoded transaction or output of :func:`~bit.PrivateKey.prepare_transaction`.
        :type tx_data: ``str``
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        if isinstance(tx_data, str) and tx_data[0] == '{':  # Json-tx-data
            data = json.loads(tx_data)

            unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
            outputs = data['outputs']

            return create_new_transaction(self, unspents, outputs)
        else:  # May be partially-signed multisig transaction:
            return sign_legacy_tx(self, tx_data)


class MultiSigTestnet:
    """This class represents a testnet Bitcoin multisignature contract.
    **Note:** coins on the test network have no monetary value!

    :param private_key: A class representing a testnet private key.
    :type private_key: ``PrivateKeyTestnet``
    :raises TypeError: If ``private_key`` is not a ``PrivateKeyTestnet``.
    :param public_keys: A list of public keys encoded as hex assigned
                        to the multi-signature contract.
    :type public_keys: ``list`` of ``str``
    :raises TypeError: When the list ``public_keys`` does not include the public
                       key corresponding to the private key used in this class.
    :param m: The number of required signatures to spend from this multi-
              signature contract.
    :type m: ``int``
    """

    def __init__(self, private_key, public_keys, m):

        if private_key.instance != 'PrivateKeyTestnet':
            raise TypeError('MultiSigTesnet only accepts PrivateKeyTestnet class to assign a private key.')

        self._pk = private_key

        self.version = 'test'
        self._address = None
        self._scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

        self.instance = 'MultiSigTestnet'

        if bytes_to_hex(private_key.public_key) not in public_keys:
            raise TypeError('Private key does not match any provided public key.')
        else:
            self.public_key = private_key.public_key
            self.public_keys = public_keys
            self.m = m
            self.redeemscript = multisig_to_redeemscript(public_keys, self.m)

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = multisig_to_address(self.public_keys, self.m, version=self.version)
        return self._address

    @property
    def scriptcode(self):
        self._scriptcode = self.redeemscript
        return self._scriptcode

    def sign(self, data):
        """Signs some data which can be verified later by others using
        the public key.

        :param data: The message to sign.
        :type data: ``bytes``
        :returns: A signature compliant with BIP-62.
        :rtype: ``bytes``
        """
        return self._pk.sign(data)

    def balance_as(self, currency):
        """Returns your balance as a formatted string in a particular currency.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        """Fetches the current balance by calling
        :func:`~bit.MultiSig.get_unspents` and returns it using
        :func:`~bit.MultiSig.balance_as`.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        self.get_unspents()
        return self.balance_as(currency)

    def get_unspents(self):
        """Fetches all available unspent transaction outputs.

        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """
        if self.version == 'test':
            self.unspents[:] = NetworkAPI.get_unspent_testnet(self.address)
        else:
            self.unspents[:] = NetworkAPI.get_unspent(self.address)
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        if self.version == 'test':
            self.transactions[:] = NetworkAPI.get_transactions_testnet(self.address)
        else:
            self.transactions[:] = NetworkAPI.get_transactions(self.address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True,
                           message=None, unspents=None):
        """Creates a signed P2SH transaction.

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
            compressed=self._pk.is_compressed()
        )

        return create_new_transaction(self, unspents, outputs)

    def send(self, outputs, fee=None, leftover=None, combine=True,
             message=None, unspents=None):  # pragma: no cover
        """Creates a signed P2SH transaction and attempts to broadcast it on
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

        NetworkAPI.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None, leftover=None,
                            combine=True, message=None, unspents=None):  # pragma: no cover
        """Prepares a P2SH transaction for offline signing.

        :param address: The address the funds will be sent from.
        :type address: ``str``
        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param compressed: Whether or not the ``address`` corresponds to a
                           compressed public key. This influences the fee.
        :type compressed: ``bool``
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
        :returns: JSON storing data required to create an offline transaction.
        :rtype: ``str``
        """
        unspents, outputs = sanitize_tx_data(
            unspents or NetworkAPI.get_unspent(address),
            outputs,
            fee or get_fee_cached(),
            leftover or address,
            combine=combine,
            message=message,
            compressed=compressed
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data):  # pragma: no cover
        """Creates a signed P2SH transaction using previously prepared
        transaction data.

        :param tx_data: Hex-encoded transaction or output of :func:`~bit.PrivateKey.prepare_transaction`.
        :type tx_data: ``str``
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        if isinstance(tx_data, str) and tx_data[0] == '{':  # Json-tx-data
            data = json.loads(tx_data)

            unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
            outputs = data['outputs']

            return create_new_transaction(self, unspents, outputs)
        else:  # May be partially-signed multisig tx:
            return sign_legacy_tx(self, tx_data)
