import sys
from decimal import Decimal

import requests
from requests.exceptions import ConnectionError, Timeout

from bit.format import BTC
from bit.transaction import UTXO

if sys.version_info < (3, 5):
    JSONDecodeError = ValueError
else:
    from json.decoder import JSONDecodeError


class InsightAPI:
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_BALANCE_API = ''
    MAIN_UNSPENT_API = ''
    MAIN_TX_PUSH_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address))

        return Decimal(str(r.json())).normalize() / BTC

    @classmethod
    def get_balances(cls, addresses):
        endpoint = cls.MAIN_BALANCE_API

        balances = []

        for address in addresses:
            r = requests.get(endpoint.format(address))

            balances.append(Decimal(str(r.json())).normalize() / BTC)

        return balances

    @classmethod
    def get_tx_list(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address)

        return r.json()['transactions']

    @classmethod
    def get_tx_lists(cls, addresses):
        endpoint = cls.MAIN_ADDRESS_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint + address)

            transaction_lists.append(r.json()['transactions'])

        return transaction_lists

    @classmethod
    def get_utxo_list(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address))

        return [
            UTXO(Decimal(str(tx['amount'])).normalize(),
                 tx['confirmations'],
                 tx['scriptPubKey'],
                 tx['txid'],
                 tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def get_utxo_lists(cls, addresses):
        endpoint = cls.MAIN_UNSPENT_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint.format(address))

            transaction_lists.append([
                UTXO(Decimal(str(tx['amount'])).normalize(),
                     tx['confirmations'],
                     tx['scriptPubKey'],
                     tx['txid'],
                     tx['vout'])
                for tx in r.json()
            ])

        return transaction_lists


class BitpayAPI(InsightAPI):
    MAIN_ENDPOINT = 'https://insight.bitpay.com/api/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'addr/'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + '{}/balance'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '{}/utxo'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx/send'
    TEST_ENDPOINT = 'https://test-insight.bitpay.com/api/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'addr/'
    TEST_BALANCE_API = TEST_ADDRESS_API + '{}/balance'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '{}/utxo'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'tx/send'
    TX_PUSH_PARAM = 'rawtx'

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_BALANCE_API.format(address))

        return Decimal(str(r.json())).normalize() / BTC

    @classmethod
    def get_test_balances(cls, addresses):
        endpoint = cls.TEST_BALANCE_API

        balances = []

        for address in addresses:
            r = requests.get(endpoint.format(address))

            balances.append(Decimal(str(r.json())).normalize() / BTC)

        return balances

    @classmethod
    def get_test_tx_list(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address)

        return r.json()['transactions']

    @classmethod
    def get_test_tx_lists(cls, addresses):
        endpoint = cls.TEST_ADDRESS_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint + address)

            transaction_lists.append(r.json()['transactions'])

        return transaction_lists

    @classmethod
    def get_test_utxo_list(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API.format(address))

        return [
            UTXO(Decimal(str(tx['amount'])).normalize(),
                 tx['confirmations'],
                 tx['scriptPubKey'],
                 tx['txid'],
                 tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def get_test_utxo_lists(cls, addresses):
        endpoint = cls.TEST_UNSPENT_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint.format(address))

            transaction_lists.append([
                UTXO(Decimal(str(tx['amount'])).normalize(),
                     tx['confirmations'],
                     tx['scriptPubKey'],
                     tx['txid'],
                     tx['vout'])
                for tx in r.json()
            ])

        return transaction_lists


class BlockexplorerAPI(InsightAPI):
    MAIN_ENDPOINT = 'https://blockexplorer.com/api/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'addr/'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + '{}/balance'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '{}/utxo'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx/send'
    TX_PUSH_PARAM = 'rawtx'


class BlockrAPI:
    MAIN_ENDPOINT = 'http://btc.blockr.io/api/v1/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + 'balance/'
    MAIN_TRANSACTION_API = MAIN_ADDRESS_API + 'txs/'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + 'unspent/'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx/push'
    TEST_ENDPOINT = 'http://tbtc.blockr.io/api/v1/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/'
    TEST_BALANCE_API = TEST_ADDRESS_API + 'balance/'
    TEST_TRANSACTION_API = TEST_ADDRESS_API + 'txs/'
    TEST_UNSPENT_API = TEST_ADDRESS_API + 'unspent/'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'tx/push'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API + address)

        return Decimal(str(r.json()['data']['balance'])).normalize()

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_BALANCE_API + address)

        return Decimal(str(r.json()['data']['balance'])).normalize()

    @classmethod
    def get_balances(cls, addresses):

        if len(addresses) == 1:
            return [cls.get_balance(addresses[0])]

        r = requests.get(cls.MAIN_BALANCE_API + ','.join(addresses))

        balances = []

        for data in r.json()['data']:
            balances.append(Decimal(str(data['balance'])).normalize())

        return balances

    @classmethod
    def get_test_balances(cls, addresses):

        if len(addresses) == 1:
            return [cls.get_test_balance(addresses[0])]

        r = requests.get(cls.TEST_BALANCE_API + ','.join(addresses))

        balances = []

        for data in r.json()['data']:
            balances.append(Decimal(str(data['balance'])).normalize())

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

    @classmethod
    def get_utxo_list(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API + address)

        return [
            UTXO(Decimal(str(tx['amount'])).normalize(),
                 tx['confirmations'],
                 tx['script'],
                 tx['tx'],
                 tx['n'])
            for tx in r.json()['data']['unspent']
        ]

    @classmethod
    def get_utxo_lists(cls, addresses):

        # Blockr's API doesn't return a list for one address.
        if len(addresses) == 1:
            return [cls.get_utxo_list(addresses[0])]

        r = requests.get(cls.MAIN_UNSPENT_API + ','.join(addresses))
        transaction_lists = []

        for data in r.json()['data']:
            transaction_lists.append([
                UTXO(Decimal(str(tx['amount'])).normalize(),
                     tx['confirmations'],
                     tx['script'],
                     tx['tx'],
                     tx['n'])
                for tx in data['unspent']
            ])

        return transaction_lists

    @classmethod
    def get_test_utxo_list(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API + address)

        return [
            UTXO(Decimal(str(tx['amount'])).normalize(),
                 tx['confirmations'],
                 tx['script'],
                 tx['tx'],
                 tx['n'])
            for tx in r.json()['data']['unspent']
        ]

    @classmethod
    def get_test_utxo_lists(cls, addresses):

        # Blockr's API doesn't return a list for one address.
        if len(addresses) == 1:
            return [cls.get_utxo_list(addresses[0])]

        r = requests.get(cls.TEST_UNSPENT_API + ','.join(addresses))
        transaction_lists = []

        for data in r.json()['data']:
            transaction_lists.append([
                UTXO(Decimal(str(tx['amount'])).normalize(),
                     tx['confirmations'],
                     tx['script'],
                     tx['tx'],
                     tx['n'])
                for tx in data['unspent']
            ])

        return transaction_lists


class BlockchainAPI:
    ENDPOINT = 'https://blockchain.info/'
    ADDRESS_API = ENDPOINT + 'address/{}?format=json'
    MULTI_ADDRESS_API = ENDPOINT + 'multiaddr?active='
    UNSPENT_API = ENDPOINT + 'unspent?active='
    TX_PUSH_API = ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'tx'
    TEST_ENDPOINT = None

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.ADDRESS_API.format(address) + '&limit=0')

        return Decimal(str(r.json()['final_balance'])).normalize() / BTC

    @classmethod
    def get_balances(cls, addresses):
        r = requests.get(cls.MULTI_ADDRESS_API + '|'.join(addresses) + '&limit=0')

        balances = []

        for address in r.json()['addresses']:
            balances.append(Decimal(str(address['final_balance'])).normalize() / BTC)

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
            response = requests.get(endpoint.format(address),
                                    params=payload).json()

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
                response = requests.get(endpoint.format(address),
                                        params=payload).json()

            transaction_lists.append(transactions)

        return transaction_lists

    @classmethod
    def get_utxo_list(cls, address):
        r = requests.get(cls.UNSPENT_API + address)

        if r.status_code == 500:
            return []

        return [
            UTXO(Decimal(str(tx['value'])).normalize() / BTC,
                 tx['confirmations'],
                 tx['script'],
                 tx['tx_hash_big_endian'],
                 tx['tx_output_n'])
            for tx in r.json()['unspent_outputs']
        ][::-1]

    @classmethod
    def get_utxo_lists(cls, addresses):

        transaction_lists = []

        for address in addresses:
            r = requests.get(cls.UNSPENT_API + address)

            if r.status_code == 500:
                transaction_lists.append([])

            else:
                transaction_lists.append([
                    UTXO(Decimal(str(tx['value'])).normalize() / BTC,
                         tx['confirmations'],
                         tx['script'],
                         tx['tx_hash_big_endian'],
                         tx['tx_output_n'])
                    for tx in r.json()['unspent_outputs']
                ][::-1])

        return transaction_lists


class SmartbitAPI:
    MAIN_ENDPOINT = 'https://api.smartbit.com.au/v1/blockchain/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '{}/unspent'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'pushtx'
    TEST_ENDPOINT = 'https://testnet-api.smartbit.com.au/v1/blockchain/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '{}/unspent'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1')

        return Decimal(str(r.json()['address']['total']['balance_int'])).normalize() / BTC

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1')

        return Decimal(str(r.json()['address']['total']['balance_int'])).normalize() / BTC

    @classmethod
    def get_balances(cls, addresses):

        if len(addresses) == 1:
            return [cls.get_balance(addresses[0])]

        endpoint = cls.MAIN_ADDRESS_API

        balances = []

        for address in addresses:
            r = requests.get(endpoint + address + '?limit=1')

            balances.append(Decimal(str(r.json()['address']['total']['balance_int'])).normalize() / BTC)

        return balances

    @classmethod
    def get_test_balances(cls, addresses):

        if len(addresses) == 1:
            return [cls.get_test_balance(addresses[0])]

        endpoint = cls.TEST_ADDRESS_API

        balances = []

        for address in addresses:
            r = requests.get(endpoint + address + '?limit=1')

            balances.append(Decimal(str(r.json()['address']['total']['balance_int'])).normalize() / BTC)

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

    @classmethod
    def get_utxo_list(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address) + '?limit=1000')

        return [
            UTXO(Decimal(str(tx['value'])).normalize(),
                 tx['confirmations'],
                 tx['script_pub_key']['hex'],
                 tx['txid'],
                 tx['n'])
            for tx in r.json()['unspent']
        ]

    @classmethod
    def get_utxo_lists(cls, addresses):
        endpoint = cls.MAIN_UNSPENT_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint.format(address) + '?limit=1000')

            transaction_lists.append([
                UTXO(Decimal(str(tx['value'])).normalize(),
                     tx['confirmations'],
                     tx['script_pub_key']['hex'],
                     tx['txid'],
                     tx['n'])
                for tx in r.json()['unspent']
            ])

        return transaction_lists

    @classmethod
    def get_test_utxo_list(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API.format(address) + '?limit=1000')

        return [
            UTXO(Decimal(str(tx['value'])).normalize(),
                 tx['confirmations'],
                 tx['script_pub_key']['hex'],
                 tx['txid'],
                 tx['n'])
            for tx in r.json()['unspent']
        ]

    @classmethod
    def get_test_utxo_lists(cls, addresses):
        endpoint = cls.TEST_UNSPENT_API

        transaction_lists = []

        for address in addresses:
            r = requests.get(endpoint.format(address) + '?limit=1000')

            transaction_lists.append([
                UTXO(Decimal(str(tx['value'])).normalize(),
                     tx['confirmations'],
                     tx['script_pub_key']['hex'],
                     tx['txid'],
                     tx['n'])
                for tx in r.json()['unspent']
            ])

        return transaction_lists


class MultiBackend:
    IGNORED_ERRORS = (ConnectionError, JSONDecodeError, Timeout)

    GET_BALANCE_MAIN = [BitpayAPI.get_balance,
                        BlockchainAPI.get_balance,
                        BlockrAPI.get_balance,
                        BlockexplorerAPI.get_balance,
                        SmartbitAPI.get_balance]
    GET_BALANCES_MAIN = [BlockchainAPI.get_balances,
                         BlockrAPI.get_balances,
                         BitpayAPI.get_balances,
                         BlockexplorerAPI.get_balances,
                         SmartbitAPI.get_balances]
    GET_TX_LIST_MAIN = [BlockchainAPI.get_tx_list,  # No limit, requires multiple requests
                        BitpayAPI.get_tx_list,  # Limit 1000
                        SmartbitAPI.get_tx_list,  # Limit 1000
                        BlockexplorerAPI.get_tx_list,  # Limit 1000
                        BlockrAPI.get_tx_list]  # Limit 200
    GET_TX_LISTS_MAIN = [BlockchainAPI.get_tx_lists,
                         BitpayAPI.get_tx_lists,
                         SmartbitAPI.get_tx_lists,
                         BlockexplorerAPI.get_tx_lists,
                         BlockrAPI.get_tx_lists]
    GET_UTXO_LIST_MAIN = [BlockexplorerAPI.get_utxo_list,  # No limit
                          BitpayAPI.get_utxo_list,  # No limit
                          BlockrAPI.get_utxo_list,  # No limit
                          SmartbitAPI.get_utxo_list,  # Limit 1000
                          BlockchainAPI.get_utxo_list]  # Limit 250
    GET_UTXO_LISTS_MAIN = [BlockrAPI.get_utxo_lists,
                           BlockexplorerAPI.get_utxo_lists,
                           BitpayAPI.get_utxo_lists,
                           SmartbitAPI.get_utxo_lists,
                           BlockchainAPI.get_utxo_lists]

    GET_BALANCE_TEST = [BitpayAPI.get_test_balance,
                        BlockrAPI.get_test_balance,
                        SmartbitAPI.get_test_balance]
    GET_BALANCES_TEST = [BlockrAPI.get_test_balances,
                         BitpayAPI.get_test_balances,
                         SmartbitAPI.get_test_balances]
    GET_TX_LIST_TEST = [BitpayAPI.get_test_tx_list,  # Limit 1000
                        SmartbitAPI.get_test_tx_list,  # Limit 1000
                        BlockrAPI.get_test_tx_list]  # Limit 200
    GET_TX_LISTS_TEST = [BitpayAPI.get_test_tx_lists,
                         SmartbitAPI.get_test_tx_lists,
                         BlockrAPI.get_test_tx_lists]
    GET_UTXO_LIST_TEST = [BitpayAPI.get_test_utxo_list,  # No limit
                          BlockrAPI.get_test_utxo_list,  # No limit
                          SmartbitAPI.get_test_utxo_list]  # Limit 1000
    GET_UTXO_LISTS_TEST = [BlockrAPI.get_test_utxo_lists,
                           BitpayAPI.get_test_utxo_lists,
                           SmartbitAPI.get_test_utxo_lists]

    @classmethod
    def get_balance(cls, address):

        for api_call in cls.GET_BALANCE_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_test_balance(cls, address):

        for api_call in cls.GET_BALANCE_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_balances(cls, addresses):

        for api_call in cls.GET_BALANCES_MAIN:
            try:
                return api_call(addresses)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_test_balances(cls, addresses):

        for api_call in cls.GET_BALANCES_TEST:
            try:
                return api_call(addresses)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_tx_list(cls, address):

        for api_call in cls.GET_TX_LIST_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_test_tx_list(cls, address):

        for api_call in cls.GET_TX_LIST_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_tx_lists(cls, addresses):

        for api_call in cls.GET_TX_LISTS_MAIN:
            try:
                return api_call(addresses)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_test_tx_lists(cls, addresses):

        for api_call in cls.GET_TX_LISTS_TEST:
            try:
                return api_call(addresses)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_utxo_list(cls, address):

        for api_call in cls.GET_UTXO_LIST_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_test_utxo_list(cls, address):

        for api_call in cls.GET_UTXO_LIST_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_utxo_lists(cls, addresses):

        for api_call in cls.GET_UTXO_LISTS_MAIN:
            try:
                return api_call(addresses)
            except cls.IGNORED_ERRORS:
                pass

        return None

    @classmethod
    def get_test_utxo_lists(cls, addresses):

        for api_call in cls.GET_UTXO_LISTS_TEST:
            try:
                return api_call(addresses)
            except cls.IGNORED_ERRORS:
                pass

        return None
