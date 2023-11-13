.. _fees:

Fees
====

Bit provides a convenient way to get recommended satoshi/byte fees in the
form of :func:`~bit.network.get_fee` and :func:`~bit.network.get_fee_cached`,
the latter of which will cache results for 10 minutes
:ref:`by default <cache times>`. Currently, the only service in
use is `<https://mempool.space/api/v1/fees/recommended>`_.

Each function takes an optional argument ``fast`` that is ``True`` by default.
If ``True``, the fee returned will be "The lowest fee (in satoshis per byte)
that will currently result in the fastest transaction confirmations (usually
0 to 1 block delay)". Otherwise, the number returned will be "The lowest fee
(in satoshis per byte) that will confirm transactions within an hour (with 90%
probability)".

.. code-block:: python

    >>> from bit.network import get_fee, get_fee_cached
    >>>
    >>> get_fee(fast=False)
    180
    >>> get_fee_cached()
    240

If recommended fee services are unreachable, hard-coded defaults will be used.

.. code-block:: python

    >>> from bit.network import fees
    >>>
    >>> fees.DEFAULT_FEE_FAST
    220
    >>> fees.DEFAULT_FEE_HOUR
    160
