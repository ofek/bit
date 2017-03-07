.. _advanced:

Advanced
========

Server Integration
------------------

Blockchain Storage
------------------

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
