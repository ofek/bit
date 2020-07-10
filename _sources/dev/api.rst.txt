.. _api:

Developer Interface
===================

.. module:: bit

.. _keysapi:

Keys
----

.. autoclass:: bit.Key

.. autoclass:: bit.PrivateKey
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.PrivateKeyTestnet
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.MultiSig
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.MultiSigTestnet
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.wallet.BaseKey
    :members:
    :undoc-members:

Network
-------

.. autoclass:: bit.network.NetworkAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.services.BitcoreAPI
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.network.services.BlockchairAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.services.BlockstreamAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.services.BlockchainAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.services.SmartbitAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.meta.Unspent
    :members:
    :undoc-members:

Exchange Rates
--------------

.. autofunction:: bit.network.currency_to_satoshi
.. autofunction:: bit.network.currency_to_satoshi_cached
.. autofunction:: bit.network.satoshi_to_currency
.. autofunction:: bit.network.satoshi_to_currency_cached

.. autoclass:: bit.network.rates.RatesAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.rates.BitpayRates
    :members:
    :undoc-members:

.. autoclass:: bit.network.rates.BlockchainRates
    :members:
    :undoc-members:

Fees
----

.. autofunction:: bit.network.get_fee
.. autofunction:: bit.network.get_fee_cached

Utilities
---------

.. autofunction:: bit.verify_sig

Exceptions
----------

.. autoexception:: bit.exceptions.InsufficientFunds
.. autoexception:: bit.exceptions.BitcoinNodeException
.. autoexception:: bit.exceptions.ExcessiveAddress
