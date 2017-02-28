Transactions
============

Create Transaction
------------------

Keys in Bit allow 2 ways of handling transactions: a `create_transaction`
method that creates a signed transaction and returns the aforementioned
transaction in hex, and a `send` method that does the same thing but will
attempt to broadcast the transaction, returning instead the transaction id
for future lookup. Both methods take the exact arguments.

Outputs
-------

The only required argument is a list of outputs.

.. code-block:: python

    >>> key.create_transaction([('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy')])

Output Format
-------------

Each output should be a tuple of arity 3 in the form `(destination, amount, currency)`.
Amount can be an int, float, or string as long as it is a valid input to `decimal.Decimal`_.
The currency must be `supported`_.

.. _decimal.Decimal: https://docs.python.org/3/library/decimal.html#decimal.Decimal
