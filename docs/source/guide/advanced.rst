.. _advanced:

Advanced
========

Server Integration
------------------

If you only want to use Bit for its raw speed to lessen the load on your
servers, you don't have to use any of our network capabilities.

- Use :func:`~bit.PrivateKey.create_transaction` instead of
  :func:`~bit.PrivateKey.send`
- Supply :ref:`your own UTXOs <unspentparam>`
- Set :ref:`your own fee <feeparam>`
- Make sure all :ref:`outputsparam` only use these currencies: satoshi, ubtc,
  mbtc, or btc.

.. _coldstorage:

Offline Transactions
--------------------

Bit supports the signing of transactions for keys in cold storage. First you
need to prepare a transaction while connected to the internet using the
:func:`~bit.PrivateKey.prepare_transaction` class method of a private key.
You must know your address.

.. code-block:: python

    >>> from bit import PrivateKeyTestnet
    >>> from bit.network import NetworkAPI, satoshi_to_currency
    >>>
    >>> satoshi_to_currency(NetworkAPI.get_balance_testnet(address), 'usd')
    '833.03'
    >>> tx_data = PrivateKeyTestnet.prepare_transaction(address, [('n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi', 1, 'jpy')])
    >>> tx_data
    '{"unspents":[{"amount":80775726,"confirmations":1,"script":"76a914990ef60d63b5b5964a1c2282061af45123e93fcb88ac","txid":"c47061643341aca8665ca7e447aff8c57bc0fd61a3ef731f44642b1d9fa46d5a","txindex":1}],"outputs":[["n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi",861],["muUFbvTKDEokGTVUjScMhw1QF2rtv5hxCz",80720625]]}'

This performs validation and returns a JSON string containing all the required
information to create a transaction. You should then take this to your offline
machine and use the :func:`~bit.PrivateKey.sign_transaction` method of your
private key.

.. code-block:: python

    >>> tx_hex = key.sign_transaction(tx_data)
    >>> tx_hex
    '01000000015a6da49f1d2b64441f73efa361fdc07bc5f8af47e4a75c66a8ac4133646170c4010000006a4730440220266c56a2592fbd6948f3e5d17720ad2dad57ce23a5cc0d2d4fd2315cbe5a798802203372b9b0d10e920462f9553392333e84cd8fa1d92953d0b4598888370dc187140121033d5c2875c9bd116875a71a5db64cffcb13396b163d039b1d9327824891804334ffffffff025d030000000000001976a914e7c1345fc8f87c68170b3aa798a956c2fe6a9eff88acf1b2cf04000000001976a914990ef60d63b5b5964a1c2282061af45123e93fcb88ac00000000'

Finally, bring this transaction back to your connected device and broadcast it.

.. code-block:: python

    >>> from bit.network import NetworkAPI
    >>> NetworkAPI.broadcast_tx_testnet(tx_hex)

Blockchain Storage
------------------

Bit allows you to easily `store messages or data`_ in the blockchain itself
using the ``message`` parameter of :func:`~bit.PrivateKey.create_transaction`
or :func:`~bit.PrivateKey.send`:

.. code-block:: python

    >>> key.send(..., message='Simplicity level is over 9000!!!')

Messages will be encoded as UTF-8 when stored. Also, do note that the length
of each datum must not exceed 40 bytes. Therefore, your resulting byte string
will be stored in chunks to adhere to this property if it is too long.

Services Timeout
----------------

If you want to change the default timeout of 5 seconds for service API calls:

.. code-block:: python

    >>> from bit import set_service_timeout
    >>> set_service_timeout(3)

.. _cache times:

Cache Times
-----------

If you want to change the default cache time of exchange rates (60 seconds)
or recommended fees (10 minutes):

.. code-block:: python

    >>> from bit import set_fee_cache_time, set_rate_cache_time
    >>> set_rate_cache_time(30)
    >>> set_fee_cache_time(60 * 5)

.. _bytestowif:

Bytes to WIF
------------

If you store your keys as bytes (or hex) instead of WIF you lose the ability to
retain metadata. To convert your bytes keys to WIF to use certain properties,
do this:

.. code-block:: python

    >>> from bit import Key
    >>> from bit.format import bytes_to_wif
    >>>
    >>> # Compressed by default
    >>> key1 = Key()
    >>>
    >>> wif = bytes_to_wif(key1.to_bytes(), compressed=False)
    >>> key2 = Key(wif)
    >>>
    >>> # Same point on curve
    >>> key1 == key2
    True
    >>> # Different public keys for derivation of address
    >>> key1.address
    '15BYk3fNHwPB5GMjsxTX26QoWZZtwJnzCf'
    >>> key2.address
    '1BQCscSMaJhezQvX6hzCdcRVdsxJuMAdwt'

.. _store messages or data: https://en.bitcoin.it/wiki/OP_RETURN
