from decimal import Decimal

import requests

from bit.format import BTC


class InsightAPI:
    MAIN_ENDPOINT = 'https://insight.bitpay.com/api'
    MAIN_ENDPOINT_ADDRESS = MAIN_ENDPOINT + '/addr'
    MAIN_ENDPOINT_TX_PUSH = MAIN_ENDPOINT + '/tx/send'
    TEST_ENDPOINT = 'https://test-insight.bitpay.com/api'
    TEST_ENDPOINT_ADDRESS = TEST_ENDPOINT + '/addr'
    TEST_ENDPOINT_TX_PUSH = TEST_ENDPOINT + '/tx/send'
    TX_PUSH_PARAM = 'rawtx'

    @classmethod
    def get_balance(cls, address, version='main'):
        if version == 'main':
            endpoint = InsightAPI.MAIN_ENDPOINT_ADDRESS
        else:
            endpoint = InsightAPI.TEST_ENDPOINT_ADDRESS

        r = requests.get('{}/{}/balance'.format(endpoint, address))

        return Decimal(str(r.json())) / BTC

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

            balances.append(Decimal(str(r.json())) / BTC)

        return balances

    @classmethod
    def get_tx_list(cls, address, version='main'):
        if version == 'main':
            endpoint = InsightAPI.MAIN_ENDPOINT_ADDRESS
        else:
            endpoint = InsightAPI.TEST_ENDPOINT_ADDRESS

        r = requests.get('{}/{}'.format(endpoint, address))

        return r.json()['transactions']

    @classmethod
    def get_tx_lists(cls, addresses, version='main'):
        if version == 'main':
            endpoint = InsightAPI.MAIN_ENDPOINT_ADDRESS
        else:
            endpoint = InsightAPI.TEST_ENDPOINT_ADDRESS

        transaction_lists = []

        for address in addresses:
            r = requests.get('{}/{}'.format(endpoint, address))

            transaction_lists.append(r.json()['transactions'])

        return transaction_lists


class BlockrAPI:
    MAIN_ENDPOINT = 'http://btc.blockr.io/api/v1/'
    MAIN_ENDPOINT_ADDRESS = MAIN_ENDPOINT + 'address/'
    MAIN_ENDPOINT_BALANCE = MAIN_ENDPOINT_ADDRESS + 'balance/'
    MAIN_ENDPOINT_TRANSACTION = MAIN_ENDPOINT_ADDRESS + 'txs/'
    MAIN_ENDPOINT_TX_PUSH = MAIN_ENDPOINT + 'tx/push'
    TEST_ENDPOINT = 'http://tbtc.blockr.io/api/v1/'
    TEST_ENDPOINT_ADDRESS = TEST_ENDPOINT + 'address/'
    TEST_ENDPOINT_BALANCE = TEST_ENDPOINT_ADDRESS + 'balance/'
    TEST_ENDPOINT_TRANSACTION = TEST_ENDPOINT_ADDRESS + 'txs/'
    TEST_ENDPOINT_TX_PUSH = TEST_ENDPOINT + 'tx/push'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address, version='main'):
        if version == 'main':
            endpoint = BlockrAPI.MAIN_ENDPOINT_BALANCE
        else:
            endpoint = BlockrAPI.TEST_ENDPOINT_BALANCE

        r = requests.get(endpoint + address)

        return Decimal(str(r.json()['data']['balance']))

    @classmethod
    def get_balances(cls, addresses, version='main'):
        if version == 'main':
            endpoint = BlockrAPI.MAIN_ENDPOINT_BALANCE
        else:
            endpoint = BlockrAPI.TEST_ENDPOINT_BALANCE

        r = requests.get(endpoint + ','.join(addresses))

        balances = []

        for data in r.json()['data']:
            balances.append(Decimal(str(data['balance'])))

        return balances

    @classmethod
    def get_tx_list(cls, address, version='main'):
        if version == 'main':
            endpoint = BlockrAPI.MAIN_ENDPOINT_TRANSACTION
        else:
            endpoint = BlockrAPI.TEST_ENDPOINT_TRANSACTION

        r = requests.get(endpoint + address)
        tx_data = r.json()['data']['txs']

        return [d['tx'] for d in tx_data]

    @classmethod
    def get_tx_lists(cls, addresses, version='main'):

        # Blockr's API doesn't return a list for one address.
        if len(addresses) == 1:
            return BlockrAPI.get_tx_list(addresses[0], version)

        if version == 'main':
            endpoint = BlockrAPI.MAIN_ENDPOINT_TRANSACTION
        else:
            endpoint = BlockrAPI.TEST_ENDPOINT_TRANSACTION

        r = requests.get(endpoint + ','.join(addresses))
        transaction_lists = []

        for data in r.json()['data']:
            transaction_lists.append([d['tx'] for d in data['txs']])

        return transaction_lists
