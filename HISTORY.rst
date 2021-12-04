Release History
===============

Unreleased (see `master <https://github.com/ofek/bit>`_)
--------------------------------------------------------

0.8.0 (2021-12-04)
------------------

- Add custom URL route functionality for connecting to nodes
- Change fee provider

0.7.2 (2020-09-22)
------------------

- Downgrade priority of BitCoreAPI endpoints

0.7.1 (2020-08-11)
------------------

- Fix testnet Unspent.confirmations from Blockchair API
- Support change in Blockchair's push txn endpoint

0.7.0 (2020-08-06)
------------------

- Fix Unspent.confirmations from Blockchair API
- Add support for replace-by-fee (BIP 125)

0.6.2 (2020-07-10)
------------------

- Fix of critical bug that could lead to paying high fees (see PR #116)
- Better fee calculation by estimating transaction sizes for multisig correctly
- Lots of Network API improvements: Removed deprecated Bitpay API and added Blockstream, Blockchair and Bitcore.

0.6.1 (2020-02-16)
------------------

- Fixed Smartbit polling transaction hashes instead of ids
- Add support for passing raw hexadecimal messages to ``send``

0.6.0 (2019-09-04)
------------------

- Added support for ``NetworkAPI`` to use a remote Bitcoin node
- Fixed usage of BitPay rates API (it was changed abruptly)

0.5.2 (2019-05-16)
------------------

- Fixed a subtle bug when signing a multisig transaction over multiple inputs

0.5.1 (2019-04-19)
------------------

- New: Add `get_transaction_by_id()` calls
- Update default fees
- Multisig improvements

0.5.0 (2019-03-10)
------------------

- New :class:`~bit.MultiSig` adds support for P2SH nested m-of-n multisignature contracts
- Support for sending to P2SH and Bech32 output addresses
- P2SH nested segwit addresses for :class:`~bit.PrivateKey` and :class:`~bit.MultiSig`
- Support for batching transaction inputs from different keys
- Update transaction message length limit to 80

0.4.3 (2018-03-11)
------------------

- Fixed fee calculation when ``combine=False``
- **Breaking:** Exceptions will now be raised when using pay2sh addresses (until implemented)

0.4.2 (2017-12-09)
------------------

- Optimized network API priorities
- Fixed Smartbit pushtx usage
- Updated `21.co <https://www.21.co>`_ to `earn.com <https://www.earn.com>`_

0.4.1 (2017-11-01)
------------------

- Removed ``blockr.io`` network backend as `Coinbase <https://www.coinbase.com>`_ has shut it down.

0.4.0 (2017-04-19)
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
