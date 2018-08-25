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
