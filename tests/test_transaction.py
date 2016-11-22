from decimal import Decimal

from bit.transaction import UTXO


class TestUTXO:
    def test_utxo_init(self):
        utxo = UTXO(Decimal('0.01'), 7, 'script', 'txid', 0)
        assert utxo.amount == Decimal('0.01')
        assert utxo.confirmations == 7
        assert utxo.script == 'script'
        assert utxo.txid == 'txid'
        assert utxo.txindex == 0

    def test_utxo_equality(self):
        utxo1 = UTXO(Decimal('0.01'), 7, 'script', 'txid', 0)
        utxo2 = UTXO(Decimal('0.01'), 7, 'script', 'txid', 0)
        utxo3 = UTXO(Decimal('0.10'), 7, 'script', 'txid', 0)
        assert utxo1 == utxo2
        assert utxo1 != utxo3

    def test_utxo_repr(self):
        utxo = UTXO(Decimal('0.01'), 7, 'script', 'txid', 0)

        assert repr(utxo) == "UTXO(Decimal('0.01'), 7, 'script', 'txid', 0)"
