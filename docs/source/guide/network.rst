.. _network:

Network
=======

Balance
-------

Every private key has a ``balance`` property which is initially set to 0. This
internal balance will always be in `satoshi`_.

.. code-block:: python

    >>> from bit import PrivateKeyTestnet
    >>>
    >>> key = PrivateKeyTestnet('cU6s7jckL3bZUUkb3Q2CD9vNu8F1o58K5R5a3JFtidoccMbhEGKZ')
    >>> key.balance
    0

You can query the `blockchain`_ for the current balance by calling
:func:`~bit.PrivateKey.get_balance`. It takes an optional argument ``currency``
(see :ref:`supported currencies`) and returns a formatted string rounded down
to the proper number of decimal places. By default it will return the balance
in satoshi.

.. code-block:: python

    >>> key.get_balance('btc')
    '0.82721202'
    >>> key.balance
    82721202

After you communicate with the network, you can view the internal balance in
terms of other currencies using :func:`~bit.PrivateKey.balance_as`.

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
you have available to spend by calling :func:`~bit.PrivateKey.get_unspents`.

.. code-block:: python

    >>> key = PrivateKeyTestnet('cU6s7jckL3bZUUkb3Q2CD9vNu8F1o58K5R5a3JFtidoccMbhEGKZ')
    >>> key.unspents
    []
    >>> key.get_unspents()
    [Unspent(amount=82721202, confirmations=688, script='76a914990ef60d63b5b5964a1c2282061af45123e93fcb88ac', txid='2ae6f3cc21cf11cfc7ad5d79436ecf08521df6a106691dcd1672b076138ea6ff', txindex=1)]
    >>> key.unspents
    [Unspent(amount=82721202, confirmations=688, script='76a914990ef60d63b5b5964a1c2282061af45123e93fcb88ac', txid='2ae6f3cc21cf11cfc7ad5d79436ecf08521df6a106691dcd1672b076138ea6ff', txindex=1)]

As you can see, this address has 1 available UTXO to spend worth 82721202
satoshi. :func:`~bit.PrivateKey.get_balance` uses this method by totalling the
amount of all UTXO. You will never have to use this directly.

Transaction History
-------------------

Get a list of all transactions from newest to oldest by calling
:func:`~bit.PrivateKey.get_transactions`.

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

- `<https://blockchair.com>`_ via :class:`~bit.network.services.BlockchairAPI`
- `<https://blockstream.info>`_ via :class:`~bit.network.services.BlockstreamAPI`
- `<https://bitcore.io>`_ via :class:`~bit.network.services.BitcoreAPI`
- `<https://smartbit.com.au>`_ via :class:`~bit.network.services.SmartbitAPI`
- `<https://blockchain.info>`_ via :class:`~bit.network.services.BlockchainAPI`

NetworkAPI
^^^^^^^^^^

Private key network operations use :class:`~bit.network.NetworkAPI`. For each method,
it polls a service and if an error occurs it tries another.

**Note:**

:class:`~bit.network.services.BlockchainAPI` does only track up to 1000 unspent 
transaction outputs (UTXOs) and will raise :class:`~bit.exceptions.ExcessiveAddress` 
if polling unspents on an address with 1000 or more UTXOs.

:class:`~bit.network.services.BlockstreamAPI` does only track up to 50 _unconfirmed_
transactions and will raise :class:`~bit.exceptions.ExcessiveAddress` if polling 
unspents on an address with 50 or more unconfirmed. It may occasionally also 
raise :class:`~bit.exceptions.ExcessiveAddress` on an address with a history of 
many (1000+) transactions.

In those cases where the API may raise errors due to :class:`~bit.exceptions.ExcessiveAddress` 
it is advised to use your own remote Bitcoin node to poll, see below.

Using a Remote Bitcoin Core Node
================================

Bit can alternatively use a remote Bitcoin node to interact with the blockchain.

Instead of using web APIs to interact with the Bitcoin blockchain it is
possible to connect to a remote Bitcoin Core node. Bitcoin Core however is not
meant as a full-fledged blockchain explorer and does only keep track of
addresses associated with its wallet.

Transaction Database Index and ``txindex``
------------------------------------------

By default Bitcoin Core does not maintain any transaction-level data except for
those transactions
- in the mempool or relay set
- pertinent to addresses in your wallet
- pertinent to your "watch-only" addresses

If querying arbitrary transactions is important then the option ``txindex`` must
be set to true (1) inside the Bitcoin Core configuration file. Setting this 
option does not allow querying for arbitrary data on addresses, but only for 
those that are added to the wallet in for Bitcoin Core to be fetched.

Configuring Bitcoin Core
------------------------

To use Bitcoin Core as a remote node it must accept remote procedure call (RPC)
methods from the host running Bit. A username and password for the RPC must be
defined inside the Bitcoin Core configuration file.

Adding a RPC user and password can be done with the ``rpcauth`` option that uses a
hashed password. The field comes in the format: ``<USERNAME>:<SALT>$<HASH>``. A
canonical python script is included inside Bitcoin Core's `share/rpcuser <https://github.com/bitcoin/bitcoin/tree/master/share/rpcauth>`_
directory. This python script creates such a user/password combination
(note that you are given the password, you do not get to specify it yourself).

Run the script, e.g.:

.. code-block:: python

    >>> python ./rpcuser.py username
    String to be appended to bitcoin.conf:
    rpcauth=username:a14191e6892facf70686a397b126423$ddd6f7480817bd6f8083a2e07e24b93c4d74e667f3a001df26c5dd0ef5eafd0d
    Your password:
    VX3z87LBVc_X7NBLABLABLABLA


Note that this option can be specified multiple times.

Finally, make sure that Bitcoin Core will accept RPC methods from the host
running Bit. The option ``rpcallowip=<ip>`` allows RPC connections from specified
host IP. The default port used to listen to RPC methods can be set with the
option ``rpcport=<port>``; the default values being ``8332`` for mainnet, ``18332`` for
testnet and ``18443`` for regtest.

A default configuration file can be found inside the Bitcoin Core directory
under `share/examples/bitcoin.conf <https://github.com/bitcoin/bitcoin/blob/master/share/examples/bitcoin.conf>`_.

Connecting To The Node
----------------------

Connecting to a remote Bitcoin Core node from Bit is straight forward. It can be
done by calling :func:`~bit.network.services.NetworkAPI.connect_to_node`, e.g.

.. code-block:: python

    >>> from bit.network import NetworkAPI
    >>> NetworkAPI.connect_to_node(user='username', password='password', host='localhost', port=18443, use_https=False, testnet=True)

It is possible to connect to both a testnet and mainnet node by calling
:func:`~bit.network.services.NetworkAPI.connect_to_node` twice with the
arguments accordingly.

Using The Remote Bitcoin Core Node
----------------------------------

After connecting to the remote node all API calls done by
:class:`~bit.network.services.NetworkAPI` are seamlessly redirected to it.

Adding An Address To The Internal Wallet Of A Node
--------------------------------------------------

Bit will poll the node for data on an address using Bitcoin Core's internal
wallet. An address to poll must therefore first be imported to Bitcoin Core's
wallet.

We can directly access the Bitcoin Core node's RPC and then use ``importaddress``
to import a specific address as follows:

.. code-block:: python

    >>> import bit
    >>> from bit.network import NetworkAPI
    >>> # Get the `node` object for direct access:
    >>> node = NetworkAPI.connect_to_node(user='username', password='password', host='localhost', port=18443, use_https=False, testnet=True)
    >>> key = bit.PrivateKeyTestnet()
    >>> # Import an address to the node's wallet:
    >>> node.importaddress(key.segwit_address, "optional-label", False)

You can read more about the RPC ``importaddress`` `here <https://bitcoincore.org/en/doc/0.18.0/rpc/wallet/importaddress/>`_.

As we had just created the new address we set the last argument in
``importaddress`` to ``False``, which defines that the node will not rescan the
blockchain for the address as it will not have any transactions yet. If you are
importing a *used* address you must set the rescan parameter to ``True``, as you
will otherwise receive incorrect information from your node!

Performing a rescan can take several minutes.


.. _satoshi: https://en.bitcoin.it/wiki/Satoshi_(unit)
.. _blockchain: https://en.bitcoin.it/wiki/Block_chain
.. _unspent transaction outputs: https://en.bitcoin.it/wiki/Transaction#Input
