.. _exchange rates:

Exchange Rates
==============

Bit gets exchange rate data from trusted third-party APIs. Specifically,
it can access:

- `<https://bitpay.com/bitcoin-exchange-rates>`_ via :class:`~bit.network.rates.BitpayRates`
- `<https://blockchain.info/api/exchange_rates_api>`_ via :class:`~bit.network.rates.BlockchainRates`

RatesAPI
--------

Core operations use :class:`~bit.network.rates.RatesAPI`. For each method,
it polls a service and if an error occurs it tries another.

You will likely never use this directly.

Currency to Satoshi
-------------------

Bit exposes 2 ways to convert a given amount of currency to the equivalent
number of satoshi: :func:`~bit.network.currency_to_satoshi` and
:func:`~bit.network.currency_to_satoshi_cached`. The latter function will
cache results for 1 minute :ref:`by default <cache times>`.

Bit uses :func:`~bit.network.currency_to_satoshi_cached` in transactions to convert the
amount in each output to spendable satoshi.

To illustrate, here is how your outputs in `(destination, amount, currency)`
format are converted to `(destination, satoshi)` format for spending during
transactions:

.. code-block:: python

    >>> from bit.network import currency_to_satoshi_cached
    >>>
    >>> ...
    >>> for i, output in enumerate(outputs):
    ...     dest, amount, currency = output
    ...     outputs[i] = (dest, currency_to_satoshi_cached(amount, currency))

Satoshi to Currency
-------------------

Converting satoshi to another currency as a formatted string can be done using
:func:`~bit.network.satoshi_to_currency` or :func:`~bit.network.satoshi_to_currency_cached`.
The result will be rounded down to the proper number of decimal places for each currency.

.. code-block:: python

    >>> from bit.network import satoshi_to_currency_cached
    >>>
    >>> satoshi_to_currency_cached(56789, 'usd')
    '0.59'
    >>> satoshi_to_currency_cached('56789', 'jpy')
    '82'

.. _supported currencies:

Supported Currencies
--------------------

These are all the currencies currently supported by Bit. Note that converting
satoshi to itself, ubtc, mbtc, or btc never requires exchange rate data and
therefore no network calls are needed.

.. code-block:: python

    >>> from bit import SUPPORTED_CURRENCIES
    >>> print(SUPPORTED_CURRENCIES)

+---------+----------------------+
| Code    | Currency             |
+=========+======================+
| satoshi | Satoshi              |
+---------+----------------------+
| ubtc    | Microbitcoin         |
+---------+----------------------+
| mbtc    | Millibitcoin         |
+---------+----------------------+
| btc     | Bitcoin              |
+---------+----------------------+
| usd     | United States Dollar |
+---------+----------------------+
| eur     | Eurozone Euro        |
+---------+----------------------+
| gbp     | Pound Sterling       |
+---------+----------------------+
| jpy     | Japanese Yen         |
+---------+----------------------+
| cny     | Chinese Yuan         |
+---------+----------------------+
| cad     | Canadian Dollar      |
+---------+----------------------+
| aud     | Australian Dollar    |
+---------+----------------------+
| nzd     | New Zealand Dollar   |
+---------+----------------------+
| rub     | Russian Ruble        |
+---------+----------------------+
| brl     | Brazilian Real       |
+---------+----------------------+
| chf     | Swiss Franc          |
+---------+----------------------+
| sek     | Swedish Krona        |
+---------+----------------------+
| dkk     | Danish Krone         |
+---------+----------------------+
| isk     | Icelandic Krona      |
+---------+----------------------+
| pln     | Polish Zloty         |
+---------+----------------------+
| hkd     | Hong Kong Dollar     |
+---------+----------------------+
| krw     | South Korean Won     |
+---------+----------------------+
| sgd     | Singapore Dollar     |
+---------+----------------------+
| thb     | Thai Baht            |
+---------+----------------------+
| twd     | New Taiwan Dollar    |
+---------+----------------------+
| clp     | Chilean Peso         |
+---------+----------------------+

.. _unsupported currencies:

Unsupported Currencies
----------------------

If you need to use currencies in your :ref:`transactions` that Bit does not
support, convert it yourself to satoshi, ubtc, mbtc, or btc as these are
supported natively.
