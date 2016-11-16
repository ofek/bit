from decimal import Decimal

from bit.network import InsightAPI

MAIN_ADDRESS_USED1 = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'


class TestInsightAPI:
    def test_get_balance_return_type(self):
        assert isinstance(InsightAPI.get_balance(MAIN_ADDRESS_USED1), Decimal)

    def test_get_balance_main_used(self):
        assert InsightAPI.get_balance(MAIN_ADDRESS_USED1) > 16

    def test_get_balance_main_unused(self):
        assert InsightAPI.get_balance(MAIN_ADDRESS_UNUSED) == 0

    def test_get_balance_test_used(self):
        assert InsightAPI.get_balance(TEST_ADDRESS_USED1, version='test') > 0

    def test_get_balance_test_unused(self):
        assert InsightAPI.get_balance(TEST_ADDRESS_UNUSED, version='test') == 0

    def test_get_balance_unknown(self):
        assert InsightAPI.get_balance(MAIN_ADDRESS_UNUSED[:-1]) is None

    def test_get_balances_return_type(self):
        assert all(isinstance(a, Decimal) for a in InsightAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_USED2
        ]))

    def test_get_balances_main(self):
        balance1, balance2 = InsightAPI.get_balances([
            MAIN_ADDRESS_USED1, MAIN_ADDRESS_UNUSED
        ])
        assert balance1 > 16
        assert balance2 == 0

    def test_get_balances_test(self):
        balance1, balance2 = InsightAPI.get_balances([
            TEST_ADDRESS_USED1, TEST_ADDRESS_UNUSED
        ], version='test')
        assert balance1 > 0
        assert balance2 == 0

    def test_get_balances_unknown(self):
        assert InsightAPI.get_balances([MAIN_ADDRESS_UNUSED[:-1]]) == [None]












