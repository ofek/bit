.. _transactions:

Transactions
============

Keys in Bit allow 2 ways of handling transactions: a
:func:`~bit.PrivateKey.create_transaction` method that creates a signed
transaction and returns the aforementioned transaction in hex, and a
:func:`~bit.PrivateKey.send` method that does the same thing but will
attempt to broadcast the transaction, returning instead the transaction id
for future lookup. Both methods take the exact same arguments.

For multisignature keys it is very similar, but due to the nature of requiring
more signatures a single multisignature key can typically not create a fully
valid transaction with the :func:`~bit.MultiSig.create_transaction` method.
A raw partially signed transaction can be passed as hex to
:func:`~bit.MultiSig.sign_transaction`, adding the signature of the private
key that multisignature key encapsulates.
Bit allows for cross-operation between the way Bitcoin Core handles raw
partially signed transactions.

Note: :class:`~bit.MultiSig` and :class:`~bit.MultiSigTestnet` do not have a
function `send()`.

To send a fully signed and serialized transaction in hex please use
:func:`~bit.network.NetworkAPI.broadcast_tx` for mainnet or
:func:`~bit.network.NetworkAPI.broadcast_tx_testnet` for testnet directly.

.. _outputsparam:

Creating and Signing
--------------------

The only required argument to create a transaction is a list of outputs:

.. code-block:: python

    >>> key.create_transaction([('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy')])

In the same way we can also create transactions from a multisignature key, which
will be signed by the private key it encapsulates and returned as hex:

.. code-block:: python

    >>> tx_1 = multisig1.create_transaction([('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy')])

However, unless the multisignature contract only requires a single signature the
resulting transaction will only be "partially signed" and not pass validation of
the Bitcoin network.

To add a signature from another private key to a partially signed transaction,
the transaction can be passed to :func:`~bit.MultiSig.sign_transaction` of
another instance of a multisignature key, which encapsulates that private key.
The return value will be a serialization of the transaction in hex containing
now two signatures:

.. code-block:: python

    >>> tx_2 = multisig2.sign_transaction(tx_1)

The order in which the different multisignature keys sign the raw transaction
does not matter. Bit is able to append the signatures in accordance to the
multisignature contract definition.

When all required signatures have been added the returned raw transaction in hex
will pass validation of the Bitcoin network.

Batching
--------

Batching transactions allows adding multiple unspents from diferent keys to a
single transaction. This can be done with Bit in the following way:

It is possible to manually provide :class:`~bit.network.meta.Unspent` objects when
calling :func:`create_transaction` on any key object. If provided with unspents
that do not belong to the key that calls :func:`create_transaction`, then those
unspents will still be added to the transaction without being signed.

Likewise, a transaction with some unsigned inputs left can be passed to
:func:`sign_transaction` of an instance of a key object that can sign an
input and the signature will be added, similar to how multisignature inputs are
signed.

Output Format
-------------

Each output should be a tuple of arity 3 in the form `(destination, amount, currency)`.
The amount can be either an int, float, or string as long as it is a valid input to
:py:class:`decimal.Decimal`. The currency must be :ref:`supported <supported currencies>`.

Change Address
--------------

Whenever you spend an `unspent transaction output`_, it must be used in its
entirety.

Say for example you had this UTXO::

    Unspent(amount=55000, ...)

If you wanted to use 35000 satoshi to buy ice cream, you need to use all 55000
satoshi in the transaction. How this works is whatever is left over you send
back to yourself as change.

By default, if spending any unspent from a Segwit address then Bit will send any
change to its Segwit address you sent from, otherwise choose the legacy address.
But you can also manually specify where leftover funds go:

.. code-block:: python

    >>> key.create_transaction(..., leftover='some_address')

Whatever funds remain at this point (`remaining = unspent - (sending + leftover)`)
will be collected by miners as a fee.

.. _feeparam:

Fee
---

    "Miner fees are a small amount of digital currency that is included in
    transactions as a reward/incentive to the people who operate the network.
    They help the network continue to grow and provide an incentive for your
    transactions to be verified quickly."

    -- Coinbase

By default, Bit will poll `<https://mempool.space/api/v1/fees/recommended>`_ and use a fee that
will allow your transaction to be confirmed as soon as possible.

You can change the satoshi per byte fee like so:

.. code-block:: python

    >>> key.create_transaction(..., fee=70)

It is also possible to specify an absolute fee value instead. This is done by
activating the absolute fee flag and re-purposing the fee parameter with the
absolute fee value of e.g. 150 satoshis for the transaction:

    >>> key.create_transaction(..., fee=150, absolute_fee=True)

You can create a replaceable transaction whose fee can be later increased by a minimum of 1 sat/B (`BIP 125`_):

    >>> key.send(..., replace_by_fee=True)
    >>> key.create_transaction(..., replace_by_fee=True)

For more information about transaction fees `read this`_.

Unspent Consolidation
---------------------

By default Bit will use all of your available UTXOs to make future transactions
smaller and therefore reduce fees.

If you don't desire this behavior and only wish to use what is needed, do this:

.. code-block:: python

    >>> key.create_transaction(..., combine=False)

If the consolidation is disabled, Bit will use the `Branch-and-Bound`_ algorithm
to try to find a perfect match of unspents with as fall-back using Single Random
Draw of unspents.

As an example, assume you had the following UTXOs available::

    Unspent(amount=100, ...)
    Unspent(amount=200, ...)
    Unspent(amount=300, ...)

Ignoring fees for the moment and say you want to spend 150 satoshi. If
you combine all funds, you'd be left with::

    Unspent(amount=450, ...)

If you don't, you could be left with e.g.::

    Unspent(amount=150, ...)
    Unspent(amount=300, ...)

The exact unspents you would be left with when consolidation is turned off will
depend both on the amount you want to send and the available unspents. If no
exact match can be found then due to the Single Random Draw the unspents you
will be left with will not be deterministic.

Transfer Funds
--------------

If you want to send all available funds to another address or wish to simply
move your coins, you can specify a leftover address and zero outputs:

.. code-block:: python

    >>> key.create_transaction([], leftover='some_address')

.. _unspentparam:

Unspent
-------

If you already have a means of communicating with the blockchain, you can
supply your own list of unspent transaction outputs by doing either:

.. code-block:: python

    >>> key.unspents = [Unspent(...), Unspent(...), ...]
    >>> key.create_transaction(...)

or

.. code-block:: python

    >>> unspents = [Unspent(...), Unspent(...), ...]
    >>> key.create_transaction(..., unspents=unspents)

Each item must be an instance of :class:`~bit.network.meta.Unspent`.

.. _decimal.Decimal: https://docs.python.org/3/library/decimal.html#decimal.Decimal
.. _read this: https://blog.blockchain.com/2016/12/15/bitcoin-transaction-fees-what-are-they-why-should-you-care
.. _Branch-and-Bound: http://murch.one/wp-content/uploads/2016/11/erhardt2016coinselection.pdf
.. _unspent transaction output: https://en.bitcoin.it/wiki/Transaction#Input
.. _BIP 125: https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki
