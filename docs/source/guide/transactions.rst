.. _transactions:

Transactions
============

Keys in Bit allow 2 ways of handling transactions: a
:func:`~bit.PrivateKey.create_transaction` method that creates a signed
transaction and returns the aforementioned transaction in hex, and a
:func:`~bit.PrivateKey.send` method that does the same thing but will
attempt to broadcast the transaction, returning instead the transaction id
for future lookup. Both methods take the exact same arguments.

.. _outputsparam:

Outputs
-------

The only required argument is a list of outputs.

.. code-block:: python

    >>> key.create_transaction([('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy')])

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

By default Bit will send any change to the same address you sent from. You
can specify where leftover funds go like this:

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

By default, Bit will poll `<https://bitcoinfees.21.co>`_ and use a fee that
will allow your transaction to be confirmed as soon as possible.

You can change the satoshi per byte fee like so:

.. code-block:: python

    >>> key.create_transaction(..., fee=70)

For more information about transaction fees `read this`_.

Unspent Consolidation
---------------------

By default Bit will use all of your available UTXOs to make future transactions
smaller and therefore reduce fees.

If you don't desire this behavior and only wish to use what is needed, do this:

.. code-block:: python

    >>> key.create_transaction(..., combine=False)

For example, if your had the following UTXOs available::

    Unspent(amount=100, ...)
    Unspent(amount=200, ...)
    Unspent(amount=300, ...)

Forgetting about fees for the moment, assume you want to spend 150 satoshi. If
you combine all funds, you'd be left with::

    Unspent(amount=450, ...)

If you don't, you'd be left with::

    Unspent(amount=150, ...)
    Unspent(amount=300, ...)

Transfer Funds
--------------

If you want to send all available funds to another address or wish to simply
move your coins, you can specify a leftover address and zero outputs like so:

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

Each item must be an instance of `Unspent`_.

.. _decimal.Decimal: https://docs.python.org/3/library/decimal.html#decimal.Decimal
.. _read this: https://blog.blockchain.com/2016/12/15/bitcoin-transaction-fees-what-are-they-why-should-you-care
.. _unspent transaction output: https://en.bitcoin.it/wiki/Transaction#Input
