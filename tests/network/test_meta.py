from bit.network.meta import Unspent


class TestUnspent:
    def test_init(self):
        unspent = Unspent(10000, 7, 'script', 'txid', 0)
        assert unspent.amount == 10000
        assert unspent.confirmations == 7
        assert unspent.script == 'script'
        assert unspent.txid == 'txid'
        assert unspent.txindex == 0

    def test_dict_conversion(self):
        unspent = Unspent(10000, 7, 'script', 'txid', 0)

        assert unspent == Unspent.from_dict(unspent.to_dict())

    def test_equality(self):
        unspent1 = Unspent(10000, 7, 'script', 'txid', 0)
        unspent2 = Unspent(10000, 7, 'script', 'txid', 0)
        unspent3 = Unspent(50000, 7, 'script', 'txid', 0)
        assert unspent1 == unspent2
        assert unspent1 != unspent3

    def test_repr(self):
        unspent = Unspent(10000, 7, 'script', 'txid', 0)

        assert repr(unspent) == ("Unspent(amount=10000, confirmations=7, "
                                 "script='script', txid='txid', txindex=0, "
                                 "segwit=False)")

    def test_set_type(self):
        unspent = Unspent(10000, 7, 'script', 'txid', 0)

        unspent.set_type('p2pkh-uncompressed')
        assert unspent.segwit is False
        assert unspent.vsize == 180

        unspent.set_type('p2pkh')
        assert unspent.segwit is False
        assert unspent.vsize == 148

        unspent.set_type('p2sh')
        assert unspent.segwit is False
        assert unspent.vsize == 292

        unspent.set_type('np2wkh')
        assert unspent.segwit is True
        assert unspent.vsize == 90

        unspent.set_type('np2wsh')
        assert unspent.segwit is True
        assert unspent.vsize == 139

        unspent.set_type('p2wkh')
        assert unspent.segwit is True
        assert unspent.vsize == 67

        unspent.set_type('p2wsh')
        assert unspent.segwit is True
        assert unspent.vsize == 104
