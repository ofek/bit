from bit.utils import flip_hex_byte_order


class UTXO:
    __slots__ = ('amount', 'confirmations', 'script', 'txid', 'txindex')

    def __init__(self, amount, confirmations, script, txid, txindex):
        self.amount = amount
        self.confirmations = confirmations
        self.script = script
        self.txid = txid
        self.txindex = txindex

    def __eq__(self, other):
        return (self.amount == other.amount and
                self.confirmations == other.confirmations and
                self.script == other.script and
                self.txid == other.txid and
                self.txindex == other.txindex)

    def __repr__(self):
        return 'UTXO({}, {}, {}, {}, {})'.format(
            repr(self.amount),
            repr(self.confirmations),
            repr(self.script),
            repr(self.txid),
            repr(self.txindex)
        )
