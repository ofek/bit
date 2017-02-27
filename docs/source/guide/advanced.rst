Advanced
========

Services Timeout
----------------

If you want to change the default timeout of 5 seconds for service API calls:

.. code-block:: python

    >>> import bit
    >>> bit.network.services.DEFAULT_TIMEOUT = 3

Hex to WIF
----------

If you store your keys as hex instead of WIF you lose the ability to
retain metadata. To convert your keys to WIF to use certain properties,
use `bit.format.private_key_hex_to_wif`.

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
