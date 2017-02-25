Bit: Bitcoin made easy.
=======================

Version |version|.

.. image:: https://img.shields.io/pypi/v/bit.svg?style=flat-square
    :target: https://pypi.org/project/bit

.. image:: https://img.shields.io/travis/ofek/bit.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/ofek/bit

.. image:: https://img.shields.io/codecov/c/github/ofek/bit.svg?style=flat-square
    :target: https://codecov.io/gh/ofek/bit

.. image:: https://img.shields.io/pypi/pyversions/bit.svg?style=flat-square
    :target: https://pypi.org/project/bit

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

-----

Bit is a fast and compliant Bitcoin library with an extremely easy-to-use API.

**So easy in fact, you can do this:**

.. code-block:: python

    >>> from bit import Key
    >>>
    >>> my_key = Key(...)
    >>> my_key.get_balance('usd')
    '11.97'
    >>>
    >>> # Let's donate!
    >>> outputs = [
    >>>     # Wikileaks
    >>>     ('1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v', .004, 'btc'),
    >>>     # Internet Archive
    >>>     ('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy'),
    >>>     # The Pirate Bay
    >>>     ('129TQVAroeehD9fZpzK51NdZGQT4TqifbG', 3, 'eur'),
    >>>     # xkcd
    >>>     ('14Tr4HaKkKuC1Lmpr2YMAuYVZRWqAdRTcr', 2.5, 'cad')
    >>> ]
    >>>
    >>> my_key.send(outputs)
    TODO

Features
--------

- Multiple representations of private keys; WIF, PEM, DER, etc.
- Compressed public keys by default
- Fully supports 25 different currencies
- Standard P2PKH transactions
- First class support for storing data in the blockchain
- Access to the blockchain through multiple APIs for redundancy
- Exchange rate API, with optional caching
- Optimal transaction fee API, with optional caching

Guide
-----

This section will tell you a little about the project, show how to install it,
and will then walk you through how to use Bit with many examples and explanations
of best practices.

.. toctree::
   :maxdepth: 2

   guide/intro
   guide/install
   guide/keys
