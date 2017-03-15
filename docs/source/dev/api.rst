.. _api:

Developer Interface
===================

.. module:: bit

.. _keysapi:

Keys
----

.. autoclass:: bit.PrivateKey
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.PrivateKeyTestnet
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

.. autoclass:: bit.network.services.BitpayAPI
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bit.network.services.BlockchainAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.services.SmartbitAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.services.BlockrAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.meta.Unspent
    :members:
    :undoc-members:

Exchange Rates
--------------

.. autofunction:: bit.network.rates.currency_to_satoshi
.. autofunction:: bit.network.rates.currency_to_satoshi_cached
.. autofunction:: bit.network.rates.satoshi_to_currency
.. autofunction:: bit.network.rates.satoshi_to_currency_cached

.. autoclass:: bit.network.rates.RatesAPI
    :members:
    :undoc-members:

.. autoclass:: bit.network.rates.BitpayRates
    :members:
    :undoc-members:

.. autoclass:: bit.network.rates.BlockchainRates
    :members:
    :undoc-members:
