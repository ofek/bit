from decimal import Decimal

from bit.network import BitpayAPI, BlockchainAPI, BlockexplorerAPI, BlockrAPI, LocalbitcoinsAPI

MAIN_ADDRESS_USED1 = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'


class TestBitpayAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BitpayAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_main_used(self):
        assert BitpayAPI.get_balance(MAIN_ADDRESS_USED1) > 16

    def test_get_balance_main_unused(self):
        assert BitpayAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BitpayAPI.get_test_balance(TEST_ADDRESS_USED1) > 0

    def test_get_balance_test_unused(self):
        assert BitpayAPI.get_test_balance(TEST_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BitpayAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances_main(self):
        balance1, balance2 = BitpayAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 16
        assert balance2 == 0

    def test_get_balances_test(self):
        balance1, balance2 = BitpayAPI.get_test_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BitpayAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_main_used(self):
        assert len(BitpayAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 1000

    def test_get_tx_list_main_unused(self):
        assert len(BitpayAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_list_test_used(self):
        assert len(BitpayAPI.get_test_tx_list(TEST_ADDRESS_USED1)) >= 444

    def test_get_tx_list_test_unused(self):
        assert len(BitpayAPI.get_test_tx_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BitpayAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists_main(self):
        txl1, txl2 = BitpayAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1000
        assert len(txl2) == 0

    def test_get_tx_lists_test_used(self):
        txl1, txl2 = BitpayAPI.get_test_tx_lists([TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 444
        assert len(txl2) == 0


class TestBlockexplorerAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockexplorerAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_used(self):
        assert BlockexplorerAPI.get_balance(MAIN_ADDRESS_USED1) > 16

    def test_get_balance_unused(self):
        assert BlockexplorerAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BlockexplorerAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances(self):
        balance1, balance2 = BlockexplorerAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 16
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BlockexplorerAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_used(self):
        assert len(BlockexplorerAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 1000

    def test_get_tx_list_unused(self):
        assert len(BlockexplorerAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BlockexplorerAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists(self):
        txl1, txl2 = BlockexplorerAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1000
        assert len(txl2) == 0


class TestLocalbitcoinsAPI:
    def test_get_balance_return_type(self):
        assert isinstance(LocalbitcoinsAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_used(self):
        assert LocalbitcoinsAPI.get_balance(MAIN_ADDRESS_USED1) > 16

    def test_get_balance_unused(self):
        assert LocalbitcoinsAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in LocalbitcoinsAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances(self):
        balance1, balance2 = LocalbitcoinsAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 16
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(LocalbitcoinsAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_used(self):
        assert len(LocalbitcoinsAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 1000

    def test_get_tx_list_unused(self):
        assert len(LocalbitcoinsAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(LocalbitcoinsAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists(self):
        txl1, txl2 = LocalbitcoinsAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1000
        assert len(txl2) == 0


class TestBlockrAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockrAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)
        assert isinstance(BlockrAPI.get_test_balance(TEST_ADDRESS_USED1), Decimal)

    def test_get_balance_main_used(self):
        assert BlockrAPI.get_balance(MAIN_ADDRESS_USED1) > 16

    def test_get_balance_main_unused(self):
        assert BlockrAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert BlockrAPI.get_test_balance(TEST_ADDRESS_USED1) > 0

    def test_get_balance_test_unused(self):
        assert BlockrAPI.get_test_balance(TEST_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BlockrAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))
        assert all(isinstance(a, Decimal) for a in BlockrAPI.get_test_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_USED2
        ]))

    def test_get_balances_main(self):
        balance1, balance2 = BlockrAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 16
        assert balance2 == 0

    def test_get_balances_test(self):
        balance1, balance2 = BlockrAPI.get_test_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED
        ])
        assert balance1 > 0
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BlockrAPI.get_tx_list(MAIN_ADDRESS_USED1))
        assert iter(BlockrAPI.get_test_tx_list(TEST_ADDRESS_USED1))

    def test_get_tx_list_main_used(self):
        assert len(BlockrAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 200

    def test_get_tx_list_main_unused(self):
        assert len(BlockrAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_list_test_used(self):
        assert len(BlockrAPI.get_test_tx_list(TEST_ADDRESS_USED1)) >= 200

    def test_get_tx_list_test_unused(self):
        assert len(BlockrAPI.get_test_tx_list(TEST_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BlockrAPI.get_tx_lists([MAIN_ADDRESS_USED1]))
        assert iter(BlockrAPI.get_test_tx_lists([TEST_ADDRESS_USED1]))

    def test_get_tx_lists_main(self):
        txl1, txl2 = BlockrAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 200
        assert len(txl2) == 0

    def test_get_tx_lists_test_used(self):
        txl1, txl2 = BlockrAPI.get_test_tx_lists([TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED])
        assert len(txl1) >= 200
        assert len(txl2) == 0


class TestBlockchainAPI:
    def test_get_balance_return_type(self):
        assert isinstance(BlockchainAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_used(self):
        assert BlockchainAPI.get_balance(MAIN_ADDRESS_USED1) > 16

    def test_get_balance_unused(self):
        assert BlockchainAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in BlockchainAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances(self):
        balance1, balance2 = BlockchainAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 16
        assert balance2 == 0

    def test_get_tx_list_return_type(self):
        assert iter(BlockchainAPI.get_tx_list(MAIN_ADDRESS_USED1))

    def test_get_tx_list_used(self):
        assert len(BlockchainAPI.get_tx_list(MAIN_ADDRESS_USED1)) >= 1066

    def test_get_tx_list_unused(self):
        assert len(BlockchainAPI.get_tx_list(MAIN_ADDRESS_UNUSED)) == 0

    def test_get_tx_lists_return_type(self):
        assert iter(BlockchainAPI.get_tx_lists([MAIN_ADDRESS_USED1]))

    def test_get_tx_lists(self):
        txl1, txl2 = BlockchainAPI.get_tx_lists([MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED])
        assert len(txl1) >= 1066
        assert len(txl2) == 0
