Release History
===============

Unreleased (see `master <https://github.com/ofek/bit>`_)
--------------------------------------------------------

0.4.0 (2017-04-11)
------------------

- Changed elliptic curve backend from OpenSSL to libsecp256k1. This results
  in an order of magnitude faster key creation and signing/verifying.
- Improved performance of base58 encoding/decoding.
- **Breaking:** Dropped support for Python 3.3 & 3.4.
- **Breaking:** :func:`~bit.verify_sig` now returns ``False`` for invalid
  signatures instead of raising an exception. Also, ``strict`` is no longer
  a parameter as BIP-62 compliance is now required.

0.3.1 (2017-03-21)
------------------

- **Fixed** :ref:`cold storage <coldstorage>` workflow.
- Improved performance of private key instantiation.

0.3.0 (2017-03-20)
------------------

- Implemented a way to use private keys in :ref:`cold storage <coldstorage>`.
- Changed the default timeout of services from 5 to 10 seconds.
- Fixed network service redundancy by failing if response code is not 200.

0.2.0 (2017-03-17)
------------------

- Improved stability of network tests.
- Added :func:`~bit.verify_sig`.
- Refactored crypto to yield over an order of magnitude faster hashing.

0.1.0 (2017-03-15)
------------------

- Initial release.
