from decimal import Decimal

import requests

from bit.format import BTC


class InsightAPI:
    MAIN_ENDPOINT = 'https://insight.bitpay.com/api'
    MAIN_ENDPOINT_ADDRESS = MAIN_ENDPOINT + '/addr'
    TEST_ENDPOINT = 'https://test-insight.bitpay.com/api'
    TEST_ENDPOINT_ADDRESS = TEST_ENDPOINT + '/addr'

    @classmethod
    def get_balance(cls, address, version='main'):
        if version == 'main':
            endpoint = InsightAPI.MAIN_ENDPOINT_ADDRESS
        else:
            endpoint = InsightAPI.TEST_ENDPOINT_ADDRESS

        r = requests.get('{}/{}/balance'.format(endpoint, address))

        if r.status_code == 200:
            return Decimal(str(r.json())) / BTC
        else:
            return None

    @classmethod
    def get_balances(cls, addresses, version='main'):
        if version == 'main':
            endpoint = InsightAPI.MAIN_ENDPOINT_ADDRESS
        else:
            endpoint = InsightAPI.TEST_ENDPOINT_ADDRESS

        balances = []
        url = '{}/{}/balance'

        for address in addresses:
            r = requests.get(url.format(endpoint, address))

            if r.status_code == 200:
                balances.append(Decimal(str(r.json())) / BTC)
            else:
                balances.append(None)

        return balances













