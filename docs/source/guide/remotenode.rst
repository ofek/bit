.. _remotenode:

Using a Remote Bitcoin Core Node
================================

Instead of using web APIs to interact with the Bitcoin blockchain it is
possible to connect to a remote Bitcoin Core node. Bitcoin Core however is not
meant as a full-fledged blockchain explorer and does only keep track of
addresses associated with its wallet.

Transaction Database Index and `txindex`
----------------------------------------

By default Bitcoin Core does not maintain any transaction-level data except for
those transactions
- in the mempool or relay set
- pertinent to addresses in your wallet
- pertinent to your "watch-only" addresses

If querying arbitrary transactions is important then the option `txindex` must
be set to true (1) inside the Bitcoin Core configuration file, see
`Running Bitcoin`_. Setting this option does not allow querying arbitrary data
on addresses, which are still required to be present in the wallet for Bitcoin
Core to be fetched.

Configuring Bitcoin Core
------------------------

To use Bitcoin Core as a remote node it must accept remote procedure call (RPC)
methods from the host running Bit. A username and password for the RPC must be
defined inside the Bitcoin Core configuration file.

Adding a RPC user and password can be done with the `rpcauth` option that uses a
hashed password. The field comes in the format: `<USERNAME>:<SALT>$<HASH>`. A
canonical python script is included inside Bitcoin Core's `share/rpcuser`_
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
running Bit. The option `rpcallowip=<ip>` allows RPC connections from specified
host IP. The default port used to listen to RPC methods can be set with the
option `rpcport=<port>`; the default values being 8332 for mainnet, 18332 for
testnet and 18443 for regtest.

A default configuration file can be found inside the Bitcoin Core directory
under `share/examples/bitcoin.conf`_.

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

We can directly access the Bitcoin Core node's RPC and then use `importaddress`
to import a specific address as follows:

.. code-block:: python

    >>> import bit
    >>> from bit.network import NetworkAPI
    >>> # Get the `node` object for direct access:
    >>> node = NetworkAPI.connect_to_node(user='username', password='password', host='localhost', port=18443, use_https=False, testnet=True)
    >>> key = bit.PrivateKeyTestnet()
    >>> # Import an address to the node's wallet:
    >>> node.importaddress(key.segwit_address, "optional-label", False)

You can read more about the RPC `importaddress` [here](https://bitcoincore.org/en/doc/0.18.0/rpc/wallet/importaddress/).

As we had just created the new address we set the last argument in
`importaddress` to `False`, which defines that the node will not rescan the
blockchain for the address as it will not have any transactions yet. If you are
importing a _used_ address you must set the rescan parameter to `True`, as you
will otherwise receive incorrect information from your node!

Performing a rescan can take several minutes.
