Bit: Bitcoin made easy.
=======================

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

So easy in fact, you can do this:

.. code-block:: python

    >>> from bit import Key
    >>>
    >>> my_key = Key('L3jsepcttyuJK3HKezD4qqRKGtwc8d2d1Nw6vsoPDX9cMcUxqqMv')
    >>> my_key.get_balance('usd')
    11.97
    >>>
    >>> wikileaks = ('1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v', .004, 'btc')
    >>> internet_archive = ('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy')
    >>> the_pirate_bay = ('129TQVAroeehD9fZpzK51NdZGQT4TqifbG', 3, 'eur')
    >>> xkcd = ('14Tr4HaKkKuC1Lmpr2YMAuYVZRWqAdRTcr', 2.5, 'cad')
    >>>
    >>> outputs = [
    >>>     wikileaks,
            internet_archive,
            the_pirate_bay,
            xkcd
    >>> ]
    >>>
    >>> my_key.send(outputs)
    TODO

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
