import json

from bit.crypto import ECPrivateKey, ripemd160_sha256, sha256
from bit.curve import Point
from bit.format import (
    bytes_to_wif, public_key_to_address, public_key_to_coords, wif_to_bytes,
    multisig_to_address, multisig_to_redeemscript, public_key_to_segwit_address,
    multisig_to_segwit_address
)
from bit.network import NetworkAPI, get_fee_cached, satoshi_to_currency_cached
from bit.network.meta import Unspent
from bit.transaction import (
    calc_txid, create_new_transaction, sanitize_tx_data, sign_tx,
    deserialize, address_to_scriptpubkey
)
from bit.constants import OP_0, OP_PUSH_20, OP_PUSH_32

from bit.utils import hex_to_bytes, bytes_to_hex, int_to_varint


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

        self.version = 'main'
        self.instance = 'PrivateKey'

        self._address = None
        self._segwit_address = None
        self._scriptcode = None
        self._segwit_scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key,
                                                  version=self.version)
        return self._address

    @property
    def segwit_address(self):
        """The public segwit nested in P2SH address you share with others to
        receive funds."""
        # Only make segwit address if public key is compressed
        if self._segwit_address is None and self.is_compressed():
            self._segwit_address = public_key_to_segwit_address(
                self._public_key, version=self.version)
        return self._segwit_address

    @property
    def scriptcode(self):
        self._scriptcode = address_to_scriptpubkey(self.address)
        return self._scriptcode

    @property
    def segwit_scriptcode(self):
        self._segwit_scriptcode = (OP_0 + OP_PUSH_20
                                   + ripemd160_sha256(self.public_key))
        return self._segwit_scriptcode

    def can_sign_unspent(self, unspent):
        script = bytes_to_hex(address_to_scriptpubkey(self.address))
        if self.segwit_address:
            segwit_script = bytes_to_hex(address_to_scriptpubkey(
                self.segwit_address))
            return unspent.script == script or unspent.script == segwit_script
        else:
            return unspent.script == script

    def to_wif(self):
        return bytes_to_wif(
            self._pk.secret,
            version=self.version,
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
        self.unspents[:] = list(map(
            lambda u: u.set_type('p2pkh' if self.is_compressed() else
                                 'p2pkh-uncompressed'),
            NetworkAPI.get_unspent(self.address)
        ))
        if self.segwit_address:
            self.unspents += list(map(
                lambda u: u.set_type('np2wkh'),
                NetworkAPI.get_unspent(self.segwit_address)
            ))
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkAPI.get_transactions(self.address)
        if self.segwit_address:
            self.transactions += NetworkAPI.get_transactions(self.segwit_address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, absolute_fee=False,
                           leftover=None, combine=True, message=None,
                           unspents=None):  # pragma: no cover
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
        try:
            unspents = unspents or self.get_unspents()
        except ConnectionError:
            raise ConnectionError('All APIs are unreachable. Please provide '
                                  'the unspents to spend from directly.')

        # If at least one input is from segwit the return address is for segwit
        return_address = self.segwit_address if any(
            [u.segwit for u in unspents]) else self.address

        unspents, outputs = sanitize_tx_data(
            unspents,
            outputs,
            fee or get_fee_cached(),
            leftover or return_address,
            combine=combine,
            message=message,
            absolute_fee=absolute_fee,
            version=self.version
        )

        return create_new_transaction(self, unspents, outputs)

    def send(self, outputs, fee=None, absolute_fee=False, leftover=None,
             combine=True, message=None, unspents=None):  # pragma: no cover
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
            outputs,
            fee=fee,
            absolute_fee=absolute_fee,
            leftover=leftover,
            combine=combine,
            message=message,
            unspents=unspents
        )

        NetworkAPI.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None,
                            absolute_fee=False, leftover=None, combine=True,
                            message=None, unspents=None):  # pragma: no cover
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
            absolute_fee=absolute_fee,
            version='main'
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data, unspents=None):  # pragma: no cover
        """Creates a signed P2PKH transaction using previously prepared
        transaction data.

        :param tx_data: Hex-encoded transaction or output of :func:`~bit.Key.prepare_transaction`.
        :type tx_data: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        try:  # Json-tx-data from :func:`~bit.Key.prepare_transaction`
            data = json.loads(tx_data)
            assert(unspents is None)

            unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
            outputs = data['outputs']

            return create_new_transaction(self, unspents, outputs)
        except:  # May be hex-encoded transaction using batching:
            try:
                unspents = unspents or self.get_unspents()
            except ConnectionError:
                raise ConnectionError(
                    'All APIs are unreachable. Please provide the unspent '
                    'inputs as unspents directly to sign this transaction.')

            tx_data = deserialize(tx_data)
            return sign_tx(self, tx_data, unspents=unspents)

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

        self.version = 'test'
        self.instance = 'PrivateKeyTestnet'

        self._address = None
        self._segwit_address = None
        self._scriptcode = None
        self._segwit_scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key,
                                                  version=self.version)
        return self._address

    @property
    def segwit_address(self):
        """The public segwit nested in P2SH address you share with others to
        receive funds."""
        # Only make segwit address if public key is compressed
        if self._segwit_address is None and self.is_compressed():
            self._segwit_address = public_key_to_segwit_address(
                self._public_key, version=self.version)
        return self._segwit_address

    @property
    def scriptcode(self):
        self._scriptcode = address_to_scriptpubkey(self.address)
        return self._scriptcode

    @property
    def segwit_scriptcode(self):
        self._segwit_scriptcode = (OP_0 + OP_PUSH_20
                                   + ripemd160_sha256(self.public_key))
        return self._segwit_scriptcode

    def can_sign_unspent(self, unspent):
        script = bytes_to_hex(address_to_scriptpubkey(self.address))
        if self.segwit_address:
            segwit_script = bytes_to_hex(address_to_scriptpubkey(
                self.segwit_address))
            return unspent.script == script or unspent.script == segwit_script
        else:
            return unspent.script == script

    def to_wif(self):
        return bytes_to_wif(
            self._pk.secret,
            version=self.version,
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
        self.unspents[:] = list(map(
            lambda u: u.set_type('p2pkh' if self.is_compressed() else
                                 'p2pkh-uncompressed'),
            NetworkAPI.get_unspent_testnet(self.address)
        ))
        if self.segwit_address:
            self.unspents += list(map(
                lambda u: u.set_type('np2wkh'),
                NetworkAPI.get_unspent_testnet(self.segwit_address)
            ))
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkAPI.get_transactions_testnet(self.address)
        if self.segwit_address:
            self.transactions += NetworkAPI.get_transactions_testnet(self.segwit_address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, absolute_fee=False,
                           leftover=None, combine=True, message=None,
                           unspents=None):  # pragma: no cover
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
        try:
            unspents = unspents or self.get_unspents()
        except ConnectionError:
            raise ConnectionError('All APIs are unreachable. Please provide '
                                  'the unspents to spend from directly.')

        # If at least one input is from segwit the return address is for segwit
        return_address = self.segwit_address if any(
            [u.segwit for u in unspents]) else self.address

        unspents, outputs = sanitize_tx_data(
            unspents,
            outputs,
            fee or get_fee_cached(),
            leftover or return_address,
            combine=combine,
            message=message,
            absolute_fee=absolute_fee,
            version=self.version
        )

        return create_new_transaction(self, unspents, outputs)

    def send(self, outputs, fee=None, absolute_fee=False, leftover=None,
             combine=True, message=None, unspents=None):  # pragma: no cover
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
            outputs,
            fee=fee,
            absolute_fee=absolute_fee,
            leftover=leftover,
            combine=combine,
            message=message,
            unspents=unspents
        )

        NetworkAPI.broadcast_tx_testnet(tx_hex)

        return calc_txid(tx_hex)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None,
                            absolute_fee=False, leftover=None, combine=True,
                            message=None, unspents=None):  # pragma: no cover
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
            absolute_fee=absolute_fee,
            version='test'
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data, unspents=None):  # pragma: no cover
        """Creates a signed P2PKH transaction using previously prepared
        transaction data.

        :param tx_data: Hex-encoded transaction or output of :func:`~bit.Key.prepare_transaction`.
        :type tx_data: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        try:  # Json-tx-data from :func:`~bit.Key.prepare_transaction`
            data = json.loads(tx_data)
            assert(unspents is None)

            unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
            outputs = data['outputs']

            return create_new_transaction(self, unspents, outputs)
        except:  # May be hex-encoded transaction using batching:
            try:
                unspents = unspents or self.get_unspents()
            except ConnectionError:
                raise ConnectionError(
                    'All APIs are unreachable. Please provide the unspent '
                    'inputs as unspents directly to sign this transaction.')

            tx_data = deserialize(tx_data)
            return sign_tx(self, tx_data, unspents=unspents)

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
    :param public_keys: A list or set of public keys encoded as hex or bytes
                        assigned to the multi-signature contract. If using a
                        list, then the order of the public keys will be used in
                        the contract. If using a set, then Bit will order the
                        public keys according to lexicographical order.
    :type public_keys: ``list`` or ``set`` of ``str`` or ``bytes``
    :raises TypeError: When the list ``public_keys`` does not include the public
                       key corresponding to the private key used in this class.
    :param m: The number of required signatures to spend from this multi-
              signature contract.
    :type m: ``int``
    """

    def __init__(self, private_key, public_keys, m):

        if private_key.instance != 'PrivateKey':
            raise TypeError('MultiSig only accepts a PrivateKey class to '
                            'assign a private key.')

        if (bytes_to_hex(private_key.public_key) not in public_keys
                and private_key.public_key not in public_keys):
            raise ValueError('Private key does not match any provided public key.')

        if type(public_keys) not in (list, set):
            raise TypeError('The public keys must be provided in a list or set.')

        self.version = 'main'
        self.instance = 'MultiSig'

        self._pk = private_key
        self.public_key = private_key.public_key
        if type(public_keys) == set:
            public_keys = sorted(public_keys)
        self.public_keys = list(map(lambda k: k if type(k) == bytes else hex_to_bytes(k), public_keys))
        self.m = m
        self.redeemscript = multisig_to_redeemscript(self.public_keys, self.m)
        self.is_compressed = all(len(p) == 33 for p in self.public_keys)

        self._address = None
        self._segwit_address = None
        self._scriptcode = None
        self._segwit_scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = multisig_to_address(self.public_keys, self.m,
                                                version=self.version)
        return self._address

    @property
    def segwit_address(self):
        """The public segwit nested in P2SH address you share with others to
        receive funds."""
        # Only make segwit-address if all public keys are compressed
        if self._segwit_address is None and self.is_compressed:
            self._segwit_address = multisig_to_segwit_address(self.public_keys,
                self.m, version=self.version)
        return self._segwit_address

    @property
    def scriptcode(self):
        self._scriptcode = self.redeemscript
        return self._scriptcode

    @property
    def segwit_scriptcode(self):
        self._segwit_scriptcode = (OP_0 + OP_PUSH_32
                                   + sha256(self.redeemscript))
        return self._segwit_scriptcode

    def can_sign_unspent(self, unspent):
        script = bytes_to_hex(address_to_scriptpubkey(self.address))
        if self.segwit_address:
            segwit_script = bytes_to_hex(address_to_scriptpubkey(self.segwit_address))
            return unspent.script == script or unspent.script == segwit_script
        else:
            return unspent.script == script

    def sign(self, data):  # pragma: no cover
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
        add_p2sh_vsize = (self.m * 73 + len(int_to_varint(len(self.redeemscript)))
                          + len(self.public_keys) * 34)
        add_np2wsh_vsize = (add_p2sh_vsize + 6) // 4

        self.unspents[:] = list(map(
            lambda u: u.set_type('p2sh', add_p2sh_vsize+46),
            NetworkAPI.get_unspent(self.address)
        ))
        if self.segwit_address:
            self.unspents += list(map(
                lambda u: u.set_type('np2wsh', add_np2wsh_vsize+75),
                NetworkAPI.get_unspent(self.segwit_address)
            ))
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkAPI.get_transactions(self.address)
        if self.segwit_address:
            self.transactions += NetworkAPI.get_transactions(self.segwit_address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, absolute_fee=False,
                           leftover=None, combine=True, message=None,
                           unspents=None):  # pragma: no cover
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
        try:
            unspents = unspents or self.get_unspents()
        except ConnectionError:
            raise ConnectionError('All APIs are unreachable. Please provide '
                                  'the unspents to spend from directly.')

        # If at least one input is from segwit the return address is for segwit
        return_address = self.segwit_address if any(
            [u.segwit for u in unspents]) else self.address

        unspents, outputs = sanitize_tx_data(
            unspents,
            outputs,
            fee or get_fee_cached(),
            leftover or return_address,
            combine=combine,
            message=message,
            absolute_fee=absolute_fee,
            version=self.version
        )

        return create_new_transaction(self, unspents, outputs)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None,
                            absolute_fee=False, leftover=None, combine=True,
                            message=None, unspents=None):  # pragma: no cover
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
            absolute_fee=absolute_fee,
            version='main'
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data, unspents=None):  # pragma: no cover
        """Creates a signed P2SH transaction using previously prepared
        transaction data.

        :param tx_data: Hex-encoded transaction or output of :func:`~bit.Key.prepare_transaction`.
        :type tx_data: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        try:  # Json-tx-data from :func:`~bit.Key.prepare_transaction`
            data = json.loads(tx_data)
            assert(unspents is None)

            unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
            outputs = data['outputs']

            return create_new_transaction(self, unspents, outputs)
        except:  # May be hex-encoded partially-signed transaction or using batching:
            try:
                unspents = unspents or self.get_unspents()
            except ConnectionError:
                raise ConnectionError(
                    'All APIs are unreachable. Please provide the unspent '
                    'inputs as unspents directly to sign this transaction.')

            tx_data = deserialize(tx_data)
            return sign_tx(self, tx_data, unspents=unspents)

    def __repr__(self):
        return '<MultiSig: {}>'.format(self.address)


class MultiSigTestnet:
    """This class represents a testnet Bitcoin multisignature contract.
    **Note:** coins on the test network have no monetary value!

    :param private_key: A class representing a testnet private key.
    :type private_key: ``PrivateKeyTestnet``
    :raises TypeError: If ``private_key`` is not a ``PrivateKeyTestnet``.
    :param public_keys: A list or set of public keys encoded as hex or bytes
                        assigned to the multi-signature contract. If using a
                        list, then the order of the public keys will be used in
                        the contract. If using a set, then Bit will order the
                        public keys according to lexicographical order.
    :type public_keys: ``list`` or ``set`` of ``str`` or ``bytes``
    :raises TypeError: When the list ``public_keys`` does not include the public
                       key corresponding to the private key used in this class.
    :param m: The number of required signatures to spend from this multi-
              signature contract.
    :type m: ``int``
    """

    def __init__(self, private_key, public_keys, m):

        if private_key.instance != 'PrivateKeyTestnet':
            raise TypeError('MultiSigTesnet only accepts PrivateKeyTestnet '
                            'class to assign a private key.')

        if (bytes_to_hex(private_key.public_key) not in public_keys
                and private_key.public_key not in public_keys):
            raise ValueError('Private key does not match any provided public key.')

        if type(public_keys) not in (list, set):
            raise TypeError('The public keys must be provided in a list or set.')

        self.version = 'test'
        self.instance = 'MultiSigTestnet'

        self._pk = private_key
        self.public_key = private_key.public_key
        if type(public_keys) == set:
            public_keys = sorted(public_keys)
        self.public_keys = list(map(lambda k: k if type(k) == bytes else hex_to_bytes(k), public_keys))
        self.m = m
        self.redeemscript = multisig_to_redeemscript(self.public_keys, self.m)
        self.is_compressed = all(len(p) == 33 for p in self.public_keys)

        self._address = None
        self._segwit_address = None
        self._scriptcode = None
        self._segwit_scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = multisig_to_address(self.public_keys, self.m, version=self.version)
        return self._address

    @property
    def segwit_address(self):
        """The public segwit nested in P2SH address you share with others to
        receive funds."""
        # Only make segwit-address if all public keys are compressed
        if self._segwit_address is None and self.is_compressed is True:
            self._segwit_address = multisig_to_segwit_address(self.public_keys,
                self.m, version=self.version)
        return self._segwit_address

    @property
    def scriptcode(self):
        self._scriptcode = self.redeemscript
        return self._scriptcode

    @property
    def segwit_scriptcode(self):
        self._segwit_scriptcode = (OP_0 + OP_PUSH_32
                                   + sha256(self.redeemscript))
        return self._segwit_scriptcode

    def can_sign_unspent(self, unspent):
        script = bytes_to_hex(address_to_scriptpubkey(self.address))
        if self.segwit_address:
            segwit_script = bytes_to_hex(address_to_scriptpubkey(self.segwit_address))
            return unspent.script == script or unspent.script == segwit_script
        else:
            return unspent.script == script

    def sign(self, data):  # pragma: no cover
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
        add_p2sh_vsize = (self.m * 73 + len(int_to_varint(len(self.redeemscript)))
                          + len(self.public_keys) * 34)
        add_np2wsh_vsize = (add_p2sh_vsize + 6) // 4

        self.unspents[:] = list(map(
            lambda u: u.set_type('p2sh', add_p2sh_vsize+46),
            NetworkAPI.get_unspent_testnet(self.address)
        ))
        if self.segwit_address:
            self.unspents += list(map(
                lambda u: u.set_type('np2wsh', add_np2wsh_vsize+75),
                NetworkAPI.get_unspent_testnet(self.segwit_address)
            ))
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.

        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions[:] = NetworkAPI.get_transactions_testnet(self.address)
        if self.segwit_address:
            self.transactions += NetworkAPI.get_transactions_testnet(self.segwit_address)
        return self.transactions

    def create_transaction(self, outputs, fee=None, absolute_fee=False,
                           leftover=None, combine=True, message=None,
                           unspents=None):  # pragma: no cover
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
        try:
            unspents = unspents or self.get_unspents()
        except ConnectionError:
            raise ConnectionError('All APIs are unreachable. Please provide '
                                  'the unspents to spend from directly.')

        # If at least one input is from segwit the return address is for segwit
        return_address = self.segwit_address if any(
            [u.segwit for u in unspents]) else self.address

        unspents, outputs = sanitize_tx_data(
            unspents,
            outputs,
            fee or get_fee_cached(),
            leftover or return_address,
            combine=combine,
            message=message,
            absolute_fee=absolute_fee,
            version=self.version
        )

        return create_new_transaction(self, unspents, outputs)

    @classmethod
    def prepare_transaction(cls, address, outputs, compressed=True, fee=None,
                            absolute_fee=False, leftover=None, combine=True,
                            message=None, unspents=None):  # pragma: no cover
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
            unspents or NetworkAPI.get_unspent_testnet(address),
            outputs,
            fee or get_fee_cached(),
            leftover or address,
            combine=combine,
            message=message,
            absolute_fee=absolute_fee,
            version='test'
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data, unspents=None):  # pragma: no cover
        """Creates a signed P2SH transaction using previously prepared
        transaction data.

        :param tx_data: Hex-encoded transaction or output of :func:`~bit.Key.prepare_transaction`.
        :type tx_data: ``str``
        :param unspents: The UTXOs to use as the inputs. By default Bit will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        try:  # Json-tx-data from :func:`~bit.Key.prepare_transaction`
            data = json.loads(tx_data)
            assert(unspents is None)

            unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
            outputs = data['outputs']

            return create_new_transaction(self, unspents, outputs)
        except:  # May be hex-encoded partially-signed transaction or using batching:
            try:
                unspents = unspents or self.get_unspents()
            except ConnectionError:
                raise ConnectionError(
                    'All APIs are unreachable. Please provide the unspent '
                    'inputs as unspents directly to sign this transaction.')

            tx_data = deserialize(tx_data)
            return sign_tx(self, tx_data, unspents=unspents)

    def __repr__(self):
        return '<MultiSigTestnet: {}>'.format(self.address)
