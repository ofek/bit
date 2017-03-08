.. _advanced:

Advanced
========

Server Integration
------------------

If you only want to use Bit for its raw speed to lessen the load on your
servers, you don't have to use any of our network capabilities.

- Use `create_transaction` instead of `send`
- Supply :ref:`your own UTXOs <unspentparam>`
- Set :ref:`your own fee <feeparam>`
- Make sure all :ref:`outputsparam` only use these currencies: satoshi, ubtc,
  mbtc, or btc.

Blockchain Storage
------------------

Bit allows you to easily `store messages or data`_ in the blockchain itself
using the `message` parameter of `create_transaction` or `send`:

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

.. _hextowif:

Hex to WIF
----------

If you store your keys as hex instead of WIF you lose the ability to retain
metadata. To convert your hex keys to WIF to use certain properties, use
`bit.format.private_key_hex_to_wif`.

.. code-block:: python

    >>> from bit import Key
    >>> from bit.format import private_key_hex_to_wif
    >>>
    >>> # Compressed by default
    >>> key1 = Key()
    >>>
    >>> wif = private_key_hex_to_wif(key1.to_hex(), compressed=False)
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
