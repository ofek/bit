TX_TRUST_LOW = 1
TX_TRUST_MEDIUM = 6
TX_TRUST_HIGH = 30

UNSPENT_TYPES = {
    # Dictionary containing as keys known unspent types and as value a
    # dictionary containing information if spending uses a witness
    # program (Segwit) and its estimated scriptSig size.
    'unknown': {'segwit': None, 'vsize': 180},     # Unknown type
    'p2pkh-uncompressed':                          # Legacy P2PKH using
               {'segwit': False, 'vsize': 180},    # uncompressed keys
    'p2pkh':   {'segwit': False, 'vsize': 148},    # Legacy P2PKH
    'p2sh':    {'segwit': False, 'vsize': 292},    # Legacy P2SH (vsize corresponds to a 2-of-3 multisig input)
    'np2wkh':  {'segwit': True,  'vsize': 90},     # (Nested) P2SH-P2WKH
    'np2wsh':  {'segwit': True,  'vsize': 139},    # (Nested) P2SH-P2WSH (vsize corresponds to a 2-of-3 multisig input)
    'p2wkh':   {'segwit': True,  'vsize': 67},     # Bech32 P2WKH -- Not yet supported to sign
    'p2wsh':   {'segwit': True,  'vsize': 104}     # Bech32 P2WSH -- Not yet supported to sign (vsize corresponds to a 2-of-3 multisig input)
}


class Unspent:
    """Represents an unspent transaction output (UTXO)."""
    __slots__ = ('amount', 'confirmations', 'script', 'txid', 'txindex',
                 'type', 'vsize', 'segwit')

    def __init__(self, amount, confirmations, script, txid, txindex,
                 type='p2pkh', vsize=None, segwit=None):
        self.amount = amount
        self.confirmations = confirmations
        self.script = script
        self.txid = txid
        self.txindex = txindex
        self.type = type if type in UNSPENT_TYPES else 'unknown'
        self.vsize = vsize if vsize else UNSPENT_TYPES[self.type]['vsize']
        self.segwit = UNSPENT_TYPES[self.type]['segwit']

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in Unspent.__slots__}

    @classmethod
    def from_dict(cls, d):
        return Unspent(**{attr: d[attr] for attr in Unspent.__slots__})

    def __eq__(self, other):
        return (self.amount == other.amount and
                self.script == other.script and
                self.txid == other.txid and
                self.txindex == other.txindex and
                self.segwit == other.segwit)

    def __repr__(self):
        return 'Unspent(amount={}, confirmations={}, script={}, txid={}, txindex={}, segwit={})'.format(
            repr(self.amount),
            repr(self.confirmations),
            repr(self.script),
            repr(self.txid),
            repr(self.txindex),
            repr(self.segwit)
        )

    def set_type(self, type, vsize=0):
        self.type = type if type in UNSPENT_TYPES else 'unknown'
        self.vsize = vsize if vsize else UNSPENT_TYPES[self.type]['vsize']
        self.segwit = UNSPENT_TYPES[self.type]['segwit']
        return self
