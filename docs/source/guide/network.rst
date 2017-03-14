.. _network:

Network
=======

Balance
-------

Every private key has a `balance` property which is initially set to `0`. This
internal balance will always be in `satoshi`_.

.. code-block:: python

    >>> from bit import PrivateKeyTestnet
    >>>
    >>> key = PrivateKeyTestnet('cU6s7jckL3bZUUkb3Q2CD9vNu8F1o58K5R5a3JFtidoccMbhEGKZ')
    >>> key.balance
    0

You can query the `blockchain`_ for the current balance by calling `get_balance`.
It takes an optional argument `currency` (see :ref:`supported currencies`) and
returns a formatted string rounded down to the proper number of decimal places.
By default it will return the balance in satoshi.

.. code-block:: python

    >>> key.get_balance('btc')
    '0.82721202'
    >>> key.balance
    82721202

After you communicate with the network, you can view the internal balance in
terms of other currencies using `balance_as`.

.. code-block:: python

    >>> key.balance_as('mbtc')
    '827.21202'
    >>> key.balance_as('usd')
    '944.06'
    >>> key.balance_as('gbp')
    '757.58'
    >>> key.balance_as('cny')
    '6485.39'

See also :ref:`unsupported currencies`.

Unspent
-------

You can see what `unspent transaction outputs`_ (commonly referred to as UTXO)
you have available to spend by calling `get_unspents`.

.. code-block:: python

    >>> key = PrivateKeyTestnet('cU6s7jckL3bZUUkb3Q2CD9vNu8F1o58K5R5a3JFtidoccMbhEGKZ')
    >>> key.unspents
    []
    >>> key.get_unspents()
    [Unspent(amount=82721202, confirmations=688, script='76a914990ef60d63b5b5964a1c2282061af45123e93fcb88ac', txid='2ae6f3cc21cf11cfc7ad5d79436ecf08521df6a106691dcd1672b076138ea6ff', txindex=1)]
    >>> key.unspents
    [Unspent(amount=82721202, confirmations=688, script='76a914990ef60d63b5b5964a1c2282061af45123e93fcb88ac', txid='2ae6f3cc21cf11cfc7ad5d79436ecf08521df6a106691dcd1672b076138ea6ff', txindex=1)]

As you can see, this address has 1 available UTXO to spend worth 82721202
satoshi. `get_balance` uses this method by totalling the amount of all UTXO.
You will never have to use this directly.

Transaction History
-------------------

Get a list of all transactions from newest to oldest by calling `get_transactions`.

.. code-block:: python

    >>> key = PrivateKeyTestnet('cU6s7jckL3bZUUkb3Q2CD9vNu8F1o58K5R5a3JFtidoccMbhEGKZ')
    >>> key.transactions
    []
    >>> key.get_transactions()
    ['2ae6f3cc21cf11cfc7ad5d79436ecf08521df6a106691dcd1672b076138ea6ff',
     '56e2df8402c86c3e9467a296d112127a27c11ba8d187e0e1cac1b35f4780d11d',
     'c055bd6c8090e839ac8caea116aa5519897aaa6ee12fb2566de996dd46c9ca97',
     'ab8e45386651c6bc1230841b6c728bff222754d6c9c0b4e40bb5bbc39796dc44',
     '9c3d31f8a72f3358a73d39abdf1088d119bac2baba31bb04f0721aeb4e19fd61',
     '94fe41e489626642541df5deccaed64354f0840934fb0177dc0374beecaaeaa7',
     '143c0fc2fae94a0ad5572e8f1735db5fe26835778127f29e097b1e736f8842b7',
     '21064f95e82f6061704652a0fe9b92a2c7a75a75be4aa8a83bdf9b45678818a2',
     '0ec29933320919b4b92c3df2ad646e01ffa62f139530e7d98934db884b264943',
     'bdf635087dc14111eda16a094b41acc6fe6563fe315cc10562f3736b364173c6',
     '4c82f8f10adeae19003586fe1a705395fc91683b8e7364823227f0003639b233',
     'a3533f0cf84f57f20c9697c5e8379f7b5c5f3461ba6f80acd906104788a92ddd',
     '1eceb6c9576d0a9ab23a9e25c07b8c7407d9363a8a30ad9309941783d831305f',
     'e02e968a68788bb53dba546a775b79ede8a704e5761d37644f02f76fc1d2b52a',
     '52a573c2aa3428f035b8b90b1663dec70c8a1fae4f99f183eb88be4393c395ea',
     '5c9ae53024e1606f74d7c7219a629cf582432e402f5d5de599377a4932423731',
     'b99dd023ddd511e185c25cbb829f0f96c5515d4fc35ec86e23db30e43c37baa2',
     '66aa55b471b39534935d011f445ea1bc83b5d785a533d7c1f29116d9360f1dd0',
     '0338b19483b32d9f3b1d11e7fc79ac14b1ed14fcfa66fce4b9a691082985665b',
     '51e09d0752fc6cc22cf2de73b9cab1bd0394f9b0fa9aa05638136f539f4e8091',
     '4e1e8302572dd910bb7478b8b0a7839ac34999bec847c2940be29100ae4af472',
     'dc885a7cfcb12d8553cc91f06c0cebf72228ba1abaed67c0b40c2d6a620b2df4',
     '1bf4248262aba1518e8fbe09fdc2feb8b8165205d9cae150077f1b0dc5df5d16']

Presently this just returns each transaction's hash for further lookup. In
a future release they will become proper objects.

Services
--------

Bit communicates with the blockchain using trusted third-party APIs.
Specifically, it can access:

- `<https://insight.bitpay.com>`_ via `bit.network.services.BitpayAPI`
- `<https://blockchain.info>`_ via `bit.network.services.BlockchainAPI`
- `<https://smartbit.com.au>`_ via `bit.network.services.SmartbitAPI`
- `<http://blockr.io>`_ via `bit.network.services.BlockrAPI`

NetworkAPI
^^^^^^^^^^

Private key network operations use `bit.network.NetworkAPI`. For each method,
it polls a service and if an error occurs it tries another.

.. _satoshi: https://en.bitcoin.it/wiki/Satoshi_(unit)
.. _blockchain: https://en.bitcoin.it/wiki/Block_chain
.. _unspent transaction outputs: https://en.bitcoin.it/wiki/Transaction#Input
