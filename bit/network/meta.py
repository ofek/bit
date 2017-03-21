TX_TRUST_LOW = 1
TX_TRUST_MEDIUM = 6
TX_TRUST_HIGH = 30


class Unspent:
    """Represents an unspent transaction output (UTXO)."""
    __slots__ = ('amount', 'confirmations', 'script', 'txid', 'txindex')

    def __init__(self, amount, confirmations, script, txid, txindex):
        self.amount = amount
        self.confirmations = confirmations
        self.script = script
        self.txid = txid
        self.txindex = txindex

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in Unspent.__slots__}

    @classmethod
    def from_dict(cls, d):
        return Unspent(**{attr: d[attr] for attr in Unspent.__slots__})

    def __eq__(self, other):
        return (self.amount == other.amount and
                self.script == other.script and
                self.txid == other.txid and
                self.txindex == other.txindex)

    def __repr__(self):
        return 'Unspent(amount={}, confirmations={}, script={}, txid={}, txindex={})'.format(
            repr(self.amount),
            repr(self.confirmations),
            repr(self.script),
            repr(self.txid),
            repr(self.txindex)
        )
