Release History
===============

Unreleased (see `master <https://github.com/ofek/bit>`_)
--------------------------------------------------------

- Faster creation new unique private keys.

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
