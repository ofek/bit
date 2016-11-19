from decimal import Decimal

import requests

from bit.format import BTC


class InsightAPI:
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_TX_PUSH_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get('{}/{}/balance'.format(cls.MAIN_ADDRESS_API, address))

        return Decimal(str(r.json())) / BTC

    @classmethod
    def get_balances(cls, addresses):
        endpoint = cls.MAIN_ADDRESS_API

        balances = []
        url = '{}/{}/balance'

        for address in addresses:
            r = requests.get(url.format(endpoint, address))

            balances.append(Decimal(str(r.json())) / BTC)

        return balances

    @classmethod
    def get_tx_list(cls, address):
        r = requests.get('{}/{}'.format(cls.MAIN_ADDRESS_API, address))

        return r.json()['transactions']

    @classmethod
    def get_tx_lists(cls, addresses):
        endpoint = cls.MAIN_ADDRESS_API

        transaction_lists = []

        for address in addresses:
            r = requests.get('{}/{}'.format(endpoint, address))

            transaction_lists.append(r.json()['transactions'])

        return transaction_lists


class BitpayAPI(InsightAPI):
    MAIN_ENDPOINT = 'https://insight.bitpay.com/api'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + '/addr'
    MAIN_ENDPOINT_TX_PUSH = MAIN_ENDPOINT + '/tx/send'
    TEST_ENDPOINT = 'https://test-insight.bitpay.com/api'
    TEST_ADDRESS_API = TEST_ENDPOINT + '/addr'
    TEST_ENDPOINT_TX_PUSH = TEST_ENDPOINT + '/tx/send'
    TX_PUSH_PARAM = 'rawtx'

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get('{}/{}/balance'.format(cls.TEST_ADDRESS_API, address))

        return Decimal(str(r.json())) / BTC

    @classmethod
    def get_test_balances(cls, addresses):
        endpoint = cls.TEST_ADDRESS_API

        balances = []
        url = '{}/{}/balance'

        for address in addresses:
            r = requests.get(url.format(endpoint, address))

            balances.append(Decimal(str(r.json())) / BTC)

        return balances

    @classmethod
    def get_test_tx_list(cls, address):
        r = requests.get('{}/{}'.format(cls.TEST_ADDRESS_API, address))

        return r.json()['transactions']

    @classmethod
    def get_test_tx_lists(cls, addresses):
        endpoint = cls.TEST_ADDRESS_API

        transaction_lists = []

        for address in addresses:
            r = requests.get('{}/{}'.format(endpoint, address))

            transaction_lists.append(r.json()['transactions'])

        return transaction_lists


class BlockexplorerAPI(InsightAPI):
    MAIN_ENDPOINT = 'https://blockexplorer.com/api'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + '/addr'
    MAIN_ENDPOINT_TX_PUSH = MAIN_ENDPOINT + '/tx/send'
    TX_PUSH_PARAM = 'rawtx'


class LocalbitcoinsAPI(InsightAPI):
    MAIN_ENDPOINT = 'https://localbitcoinschain.com/api'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + '/addr'
    MAIN_ENDPOINT_TX_PUSH = MAIN_ENDPOINT + '/tx/send'
    TX_PUSH_PARAM = 'rawtx'


class BlockrAPI:
    MAIN_ENDPOINT = 'http://btc.blockr.io/api/v1/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + 'balance/'
    MAIN_TRANSACTION_API = MAIN_ADDRESS_API + 'txs/'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx/push'
    TEST_ENDPOINT = 'http://tbtc.blockr.io/api/v1/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/'
    TEST_BALANCE_API = TEST_ADDRESS_API + 'balance/'
    TEST_TRANSACTION_API = TEST_ADDRESS_API + 'txs/'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'tx/push'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API + address)

        return Decimal(str(r.json()['data']['balance']))

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_BALANCE_API + address)

        return Decimal(str(r.json()['data']['balance']))

    @classmethod
    def get_balances(cls, addresses):
        r = requests.get(cls.MAIN_BALANCE_API + ','.join(addresses))

        balances = []

        for data in r.json()['data']:
            balances.append(Decimal(str(data['balance'])))

        return balances

    @classmethod
    def get_test_balances(cls, addresses):
        r = requests.get(cls.TEST_BALANCE_API + ','.join(addresses))

        balances = []

        for data in r.json()['data']:
            balances.append(Decimal(str(data['balance'])))

        return balances

    @classmethod
    def get_tx_list(cls, address):
        r = requests.get(cls.MAIN_TRANSACTION_API + address)
        tx_data = r.json()['data']['txs']

        return [d['tx'] for d in tx_data]

    @classmethod
    def get_test_tx_list(cls, address):
        r = requests.get(cls.TEST_TRANSACTION_API + address)
        tx_data = r.json()['data']['txs']

        return [d['tx'] for d in tx_data]

    @classmethod
    def get_tx_lists(cls, addresses):

        # Blockr's API doesn't return a list for one address.
        if len(addresses) == 1:
            return [cls.get_tx_list(addresses[0])]

        r = requests.get(cls.MAIN_TRANSACTION_API + ','.join(addresses))
        transaction_lists = []

        for data in r.json()['data']:
            transaction_lists.append([d['tx'] for d in data['txs']])

        return transaction_lists

    @classmethod
    def get_test_tx_lists(cls, addresses):

        # Blockr's API doesn't return a list for one address.
        if len(addresses) == 1:
            return [cls.get_test_tx_list(addresses[0])]

        r = requests.get(cls.TEST_TRANSACTION_API + ','.join(addresses))
        transaction_lists = []

        for data in r.json()['data']:
            transaction_lists.append([d['tx'] for d in data['txs']])

        return transaction_lists


class BlockchainAPI:
    ENDPOINT = 'https://blockchain.info/'
    ADDRESS_API = ENDPOINT + 'address/{}?format=json'
    MULTI_ADDRESS_API = ENDPOINT + 'multiaddr?active='
    TX_PUSH_API = ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'tx'
    TEST_ENDPOINT = None

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.ADDRESS_API.format(address) + '&limit=0')

        return Decimal(str(r.json()['final_balance'])) / BTC

    @classmethod
    def get_balances(cls, addresses):
        r = requests.get(cls.MULTI_ADDRESS_API + '|'.join(addresses) + '&limit=0')

        balances = []

        for address in r.json()['addresses']:
            balances.append(Decimal(str(address['final_balance'])))

        return balances

    @classmethod
    def get_tx_list(cls, address):
        endpoint = cls.ADDRESS_API

        transaction_list = []
        offset = 0
        payload = {'offset': str(offset)}
        txs_per_page = 50

        response = requests.get(endpoint.format(address)).json()
        total_txs = response['n_tx']

        while total_txs > 0:
            transaction_list.extend(tx['hash'] for tx in response['txs'])

            total_txs -= txs_per_page
            offset += txs_per_page
            payload['offset'] = str(offset)
            response = requests.get(endpoint.format(address), params=payload).json()

        return transaction_list

    @classmethod
    def get_tx_lists(cls, addresses):
        endpoint = cls.ADDRESS_API

        transaction_lists = []
        txs_per_page = 50

        for address in addresses:
            transactions = []
            offset = 0
            payload = {'offset': str(offset)}

            response = requests.get(endpoint.format(address)).json()
            total_txs = response['n_tx']

            while total_txs > 0:
                transactions.extend(tx['hash'] for tx in response['txs'])

                total_txs -= txs_per_page
                offset += txs_per_page
                payload['offset'] = str(offset)
                response = requests.get(endpoint.format(address), params=payload).json()

            transaction_lists.append(transactions)

        return transaction_lists


class SmartbitAPI:
    MAIN_ENDPOINT = 'https://api.smartbit.com.au/v1/blockchain/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'pushtx'
    TEST_ENDPOINT = 'https://testnet-api.smartbit.com.au/v1/blockchain/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1')

        return Decimal(r.json()['address']['total']['balance'])

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1')

        return Decimal(r.json()['address']['total']['balance'])

    @classmethod
    def get_balances(cls, addresses):

        if len(addresses) == 1:
            return [cls.get_balance(addresses[0])]

        endpoint = cls.MAIN_ADDRESS_API

        balances = []

        for address in addresses:
            r = requests.get(endpoint + address + '?limit=1')

            balances.append(Decimal(r.json()['address']['total']['balance']))

        return balances

    @classmethod
    def get_test_balances(cls, addresses):

        if len(addresses) == 1:
            return [cls.get_test_balance(addresses[0])]

        endpoint = cls.TEST_ADDRESS_API

        balances = []

        for address in addresses:
            r = requests.get(endpoint + address + '?limit=1')

            balances.append(Decimal(r.json()['address']['total']['balance']))

        return balances

    @classmethod
    def get_tx_list(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1000')
        data = r.json()['address']

        transactions = []

        if 'transactions' in data:
            transactions.extend(t['hash'] for t in data['transactions'])

        return transactions

    @classmethod
    def get_test_tx_list(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1000')
        data = r.json()['address']

        transactions = []

        if 'transactions' in data:
            transactions.extend(t['hash'] for t in data['transactions'])

        return transactions

    @classmethod
    def get_tx_lists(cls, addresses):
        endpoint = cls.MAIN_ADDRESS_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint + address + '?limit=1000')
            data = r.json()['address']

            transactions = []

            if 'transactions' in data:
                transactions.extend(t['hash'] for t in data['transactions'])

            transaction_lists.append(transactions)

        return transaction_lists

    @classmethod
    def get_test_tx_lists(cls, addresses):
        endpoint = cls.TEST_ADDRESS_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint + address + '?limit=1000')
            data = r.json()['address']

            transactions = []

            if 'transactions' in data:
                transactions.extend(t['hash'] for t in data['transactions'])

            transaction_lists.append(transactions)

        return transaction_lists
