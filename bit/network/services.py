import requests

from bit.network import currency_to_satoshi
from bit.network.meta import Unspent

DEFAULT_TIMEOUT = 5


def set_service_timeout(seconds):
    global DEFAULT_CACHE_TIME
    DEFAULT_CACHE_TIME = seconds


class InsightAPI:
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_BALANCE_API = ''
    MAIN_UNSPENT_API = ''
    MAIN_TX_PUSH_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address, timeout=DEFAULT_TIMEOUT)
        return r.json()['transactions']

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


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
        r = requests.get(cls.TEST_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        return r.json()

    @classmethod
    def get_test_transactions(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address, timeout=DEFAULT_TIMEOUT)
        return r.json()['transactions']

    @classmethod
    def get_test_unspent(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def broadcast_test_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


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
        r = requests.get(cls.MAIN_BALANCE_API + address, timeout=DEFAULT_TIMEOUT)
        return currency_to_satoshi(r.json()['data']['balance'], 'btc')

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_BALANCE_API + address, timeout=DEFAULT_TIMEOUT)
        return currency_to_satoshi(r.json()['data']['balance'], 'btc')

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_TRANSACTION_API + address, timeout=DEFAULT_TIMEOUT)
        tx_data = r.json()['data']['txs']
        return [d['tx'] for d in tx_data]

    @classmethod
    def get_test_transactions(cls, address):
        r = requests.get(cls.TEST_TRANSACTION_API + address, timeout=DEFAULT_TIMEOUT)
        tx_data = r.json()['data']['txs']
        return [d['tx'] for d in tx_data]

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API + address, timeout=DEFAULT_TIMEOUT)
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['script'],
                    tx['tx'],
                    tx['n'])
            for tx in r.json()['data']['unspent']
        ]

    @classmethod
    def get_test_unspent(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API + address, timeout=DEFAULT_TIMEOUT)
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['script'],
                    tx['tx'],
                    tx['n'])
            for tx in r.json()['data']['unspent']
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_test_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class BlockchainAPI:
    ENDPOINT = 'https://blockchain.info/'
    ADDRESS_API = ENDPOINT + 'address/{}?format=json'
    UNSPENT_API = ENDPOINT + 'unspent?active='
    TX_PUSH_API = ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'tx'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.ADDRESS_API.format(address) + '&limit=0', timeout=DEFAULT_TIMEOUT)
        return r.json()['final_balance']

    @classmethod
    def get_transactions(cls, address):
        endpoint = cls.ADDRESS_API

        transactions = []
        offset = 0
        payload = {'offset': str(offset)}
        txs_per_page = 50

        response = requests.get(endpoint.format(address), timeout=DEFAULT_TIMEOUT).json()
        total_txs = response['n_tx']

        while total_txs > 0:
            transactions.extend(tx['hash'] for tx in response['txs'])

            total_txs -= txs_per_page
            offset += txs_per_page
            payload['offset'] = str(offset)
            response = requests.get(endpoint.format(address),
                                    params=payload,
                                    timeout=DEFAULT_TIMEOUT).json()

        return transactions

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.UNSPENT_API + address, timeout=DEFAULT_TIMEOUT)

        if r.status_code == 500:
            return []

        return [
            Unspent(tx['value'],
                    tx['confirmations'],
                    tx['script'],
                    tx['tx_hash_big_endian'],
                    tx['tx_output_n'])
            for tx in r.json()['unspent_outputs']
        ][::-1]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


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
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1', timeout=DEFAULT_TIMEOUT)
        return r.json()['address']['total']['balance_int']

    @classmethod
    def get_test_balance(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1', timeout=DEFAULT_TIMEOUT)
        return r.json()['address']['total']['balance_int']

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        data = r.json()['address']

        transactions = []

        if 'transactions' in data:
            transactions.extend(t['hash'] for t in data['transactions'])

        return transactions

    @classmethod
    def get_test_transactions(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        data = r.json()['address']

        transactions = []

        if 'transactions' in data:
            transactions.extend(t['hash'] for t in data['transactions'])

        return transactions

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address) + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        return [
            Unspent(currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'])
            for tx in r.json()['unspent']
        ]

    @classmethod
    def get_test_unspent(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API.format(address) + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        return [
            Unspent(currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'])
            for tx in r.json()['unspent']
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_test_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class NetworkApi:
    IGNORED_ERRORS = (requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout)

    GET_BALANCE_MAIN = [BitpayAPI.get_balance,
                        BlockchainAPI.get_balance,
                        BlockrAPI.get_balance,
                        SmartbitAPI.get_balance]
    GET_TRANSACTIONS_MAIN = [BlockchainAPI.get_transactions,  # No limit, requires multiple requests
                             BitpayAPI.get_transactions,  # Limit 1000
                             SmartbitAPI.get_transactions,  # Limit 1000
                             BlockrAPI.get_transactions]  # Limit 200
    GET_UNSPENT_MAIN = [BitpayAPI.get_unspent,  # No limit
                        BlockrAPI.get_unspent,  # No limit
                        SmartbitAPI.get_unspent,  # Limit 1000
                        BlockchainAPI.get_unspent]  # Limit 250
    BROADCAST_TX_MAIN = [BlockchainAPI.broadcast_tx,
                         BitpayAPI.broadcast_tx,
                         SmartbitAPI.broadcast_tx,
                         BlockrAPI.broadcast_tx]  # Limit 5/minute

    GET_BALANCE_TEST = [BitpayAPI.get_test_balance,
                        BlockrAPI.get_test_balance,
                        SmartbitAPI.get_test_balance]
    GET_TRANSACTIONS_TEST = [BitpayAPI.get_test_transactions,  # Limit 1000
                             SmartbitAPI.get_test_transactions,  # Limit 1000
                             BlockrAPI.get_test_transactions]  # Limit 200
    GET_UNSPENT_TEST = [BitpayAPI.get_test_unspent,  # No limit
                        BlockrAPI.get_test_unspent,  # No limit
                        SmartbitAPI.get_test_unspent]  # Limit 1000
    BROADCAST_TX_TEST = [BitpayAPI.broadcast_test_tx,
                         SmartbitAPI.broadcast_test_tx,
                         BlockrAPI.broadcast_test_tx]  # Limit 5/minute

    @classmethod
    def get_balance(cls, address):

        for api_call in cls.GET_BALANCE_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_test_balance(cls, address):

        for api_call in cls.GET_BALANCE_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transactions(cls, address):

        for api_call in cls.GET_TRANSACTIONS_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_test_transactions(cls, address):

        for api_call in cls.GET_TRANSACTIONS_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_unspent(cls, address):

        for api_call in cls.GET_UNSPENT_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_test_unspent(cls, address):

        for api_call in cls.GET_UNSPENT_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        success = None

        for api_call in cls.BROADCAST_TX_MAIN:
            try:
                success = api_call(tx_hex)
                if not success:
                    continue
                return
            except cls.IGNORED_ERRORS:
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_test_tx(cls, tx_hex):  # pragma: no cover
        success = None

        for api_call in cls.BROADCAST_TX_TEST:
            try:
                success = api_call(tx_hex)
                if not success:
                    continue
                return
            except cls.IGNORED_ERRORS:
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
