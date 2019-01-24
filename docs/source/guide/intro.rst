.. _intro:

Introduction
============

Bit is a fast and compliant Bitcoin library with an extremely easy-to-use API.

Why Bit?
--------

- Robust API with sane defaults, making development a breeze
- Python's fastest available implementation (100x faster than closest library)
- Compliant to many presently implemented Bitcoin Improvement Protocols
- All commits require 100% test coverage
- Available on all major platforms
- Extensive documentation

Python's Bitcoin story was pretty bleak. All libraries in use prior to Bit were
marred by unfriendly APIs, lack of testing, lack of documentation, lack of
cross-platform support, and/or slow implementations.

When I originally went to experiment with sending Bitcoin there were really no
good choices. Two choices were out almost immediately: `pybitcointools`_ was
`scary`_, unpleasant to use, and not very maintained, while `python-bitcoinlib`_,
was far too low level. That left `pycoin`_, which was a bit better but still no
docs, and 2 libraries from VC funded companies: `two1`_ from `21`_, which had
decent documentation but had an incorrect implementation of the standardized
compressed public keys (meaning such keys could literally not spend money), and
`pybitcoin`_ from `Blockstack`_ which did not support Python 3 and had limited
docs.

All of these libraries are also slow. Let's take a look at some common operations.

Instantiate a compressed private key and get its computed public key:

.. code-block:: bash

    $ python -m timeit -s "from bit import Key" "Key('L3jsepcttyuJK3HKezD4qqRKGtwc8d2d1Nw6vsoPDX9cMcUxqqMv').public_key"
    1000 loops, best of 3: 89 usec per loop
    $ python -m timeit -s "from two1.bitcoin.crypto import PrivateKey" "PrivateKey.from_b58check('L3jsepcttyuJK3HKezD4qqRKGtwc8d2d1Nw6vsoPDX9cMcUxqqMv').public_key.compressed_bytes"
    100 loops, best of 3: 11 msec per loop
    $ python -m timeit -s "from pycoin.key import Key" "Key.from_text('L3jsepcttyuJK3HKezD4qqRKGtwc8d2d1Nw6vsoPDX9cMcUxqqMv').sec()"
    10 loops, best of 3: 48.2 msec per loop
    (py2) >python -m timeit -s "from pybitcoin import BitcoinPrivateKey" "BitcoinPrivateKey('c28a9f80738f770d527803a566cf6fc3edf6cea586c4fc4a5223a5ad797e1ac3').public_key().to_hex()"
    10 loops, best of 3: 190 msec per loop

We'll use two1 only as that was the closest to Bit. Getting the address:

.. code-block:: bash

    $ python -m timeit -s "from bit import Key;k=Key()" "k.address"
    1000000 loops, best of 3: 0.249 usec per loop
    $ python -m timeit -s "from two1.bitcoin.crypto import PrivateKey;k=PrivateKey.from_random()" "k.public_key.address()"
    10000 loops, best of 3: 31.1 usec per loop

Signing, which is the most used operation:

.. code-block:: bash

    $ python -m timeit -s "from bit import Key;k=Key()" "k.sign(b'data')"
    1000 loops, best of 3: 91 usec per loop
    $ python -m timeit -s "from two1.bitcoin.crypto import PrivateKey;k=PrivateKey.from_random()" "k.raw_sign(b'data')"
    100 loops, best of 3: 10.7 msec per loop

.. note::

    The author of pycoin `has informed me <https://github.com/ofek/bit/issues/4>`_
    that a flag can be set on Linux to make some operations faster.

License
-------

Bit is licensed under terms of the `MIT License`_.

Credits
-------

- Logo courtesy of `<https://textcraft.net>`_
- `Gregory Maxwell`_ (Bitcoin core dev) for teaching me a bit of `ECC`_ math
- `arubi`_ in #bitcoin for helping me understand transaction gotchas
- `fuzeman`_ for bestowing me the name `bit` on the `Python Package Index`_

.. _pybitcointools: https://github.com/vbuterin/pybitcointools
.. _scary: https://github.com/JoinMarket-Org/joinmarket/issues/61
.. _python-bitcoinlib: https://github.com/petertodd/python-bitcoinlib
.. _pycoin: https://github.com/richardkiss/pycoin
.. _two1: https://github.com/21dotco/two1-python
.. _21: https://angel.co/21
.. _pybitcoin: https://github.com/blockstack/pybitcoin
.. _Blockstack: https://angel.co/blockstack
.. _MIT License: https://en.wikipedia.org/wiki/MIT_License
.. _Gregory Maxwell: https://github.com/gmaxwell
.. _ECC: https://en.wikipedia.org/wiki/Elliptic_curve_cryptography
.. _arubi: https://github.com/fivepiece
.. _fuzeman: https://github.com/fuzeman
.. _Python Package Index: https://pypi.org
