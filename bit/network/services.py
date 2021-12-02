import requests
import json
import logging
from decimal import Decimal, getcontext

from bit.constants import BTC
from bit.network import currency_to_satoshi
from bit.network.meta import Unspent
from bit.exceptions import BitcoinNodeException, ExcessiveAddress
from bit.transaction import address_to_scriptpubkey
from bit.utils import bytes_to_hex

DEFAULT_TIMEOUT = 10


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class RPCHost:
    def __init__(self, user, password, host, port, use_https, path):
        self._session = requests.Session()
        self._url = "http{s}://{user}:{password}@{host}:{port}/{path}".format(
            s="s" if use_https else "", user=user, password=password, host=host, port=port, path=path
        )
        self._headers = {"content-type": "application/json"}
        self._session.verify = use_https

    def __getattr__(self, rpc_method):
        return RPCMethod(rpc_method, self)

    def get_balance(self, address):
        getcontext().prec = len(str(BTC))
        b = Decimal(self.getreceivedbyaddress(address, 0))
        return int(b * BTC)

    def get_balance_testnet(self, address):
        return self.get_balance(address)

    def get_transactions(self, address):
        r = self.listreceivedbyaddress(0, True, True, address)
        if len(r) > 0:
            r = r[0]["txids"]
        return r

    def get_transactions_testnet(self, address):
        return self.get_transactions(address)

    def get_transaction_by_id(self, txid):
        return self.getrawtransaction(txid, False)

    def get_transaction_by_id_testnet(self, txid):
        return self.get_transaction_by_id(txid)

    def get_unspent(self, address):
        r = self.listunspent(0, 9999999, [address])
        return [
            Unspent(
                currency_to_satoshi(tx["amount"], "btc"),
                tx["confirmations"],
                tx["scriptPubKey"],
                tx["txid"],
                tx["vout"],
            )
            for tx in r
        ]

    def get_unspent_testnet(self, address):
        return self.get_unspent(address)

    def broadcast_tx(self, tx_hex):
        try:
            _ = self.sendrawtransaction(tx_hex)
        except BitcoinNodeException as e:
            logging.warning(e)
            return False
        return True

    def broadcast_tx_testnet(self, tx_hex):
        return self.broadcast_tx(tx_hex)


class RPCMethod:
    def __init__(self, rpc_method, host):
        self._rpc_method = rpc_method
        self._host = host

    def __getattr__(self, rpc_method):
        new_method = '{}.{}'.format(self._rpc_method, rpc_method)
        return RPCMethod(new_method, self._host)

    def __call__(self, *args):
        payload = json.dumps({"method": self._rpc_method, "params": list(args), "jsonrpc": "2.0"})
        try:
            response = self._host._session.post(self._host._url, headers=self._host._headers, data=payload)
        except requests.exceptions.ConnectionError:
            raise ConnectionError
        if response.status_code not in (200, 500):
            raise BitcoinNodeException("RPC connection failure: " + str(response.status_code) + " " + response.reason)
        responseJSON = response.json()
        if "error" in responseJSON and responseJSON["error"] is not None:
            raise BitcoinNodeException("Error in RPC call: " + str(responseJSON["error"]))
        return responseJSON["result"]


class BlockchairAPI:
    MAIN_ENDPOINT = 'https://api.blockchair.com/bitcoin/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'dashboards/address/{}'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'push/transaction'
    MAIN_TX_API = MAIN_ENDPOINT + 'raw/transaction/{}'
    TEST_ENDPOINT = 'https://api.blockchair.com/bitcoin/testnet/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'dashboards/address/{}'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'push/transaction'
    TEST_TX_API = TEST_ENDPOINT + 'raw/transaction/{}'
    TX_PUSH_PARAM = 'data'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['data'][address]['address']['balance']

    @classmethod
    def get_balance_testnet(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['data'][address]['address']['balance']

    @classmethod
    def get_transactions(cls, address):
        endpoint = cls.MAIN_ADDRESS_API

        transactions = []
        offset = 0
        txs_per_page = 1000
        payload = {'offset': str(offset), 'limit': str(txs_per_page)}

        r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return []
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()
        response = response['data'][address]
        total_txs = response['address']['transaction_count']

        while total_txs > 0:
            transactions.extend(tx for tx in response['transactions'])

            total_txs -= txs_per_page
            offset += txs_per_page
            payload['offset'] = str(offset)
            r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()['data'][address]

        return transactions

    @classmethod
    def get_transactions_testnet(cls, address):
        endpoint = cls.TEST_ADDRESS_API

        transactions = []
        offset = 0
        txs_per_page = 1000
        payload = {'offset': str(offset), 'limit': str(txs_per_page)}

        r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return []
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()
        response = response['data'][address]
        total_txs = response['address']['transaction_count']

        while total_txs > 0:
            transactions.extend(tx for tx in response['transactions'])

            total_txs -= txs_per_page
            offset += txs_per_page
            payload['offset'] = str(offset)
            r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()['data'][address]

        return transactions

    @classmethod
    def get_transaction_by_id(cls, txid):
        r = requests.get(cls.MAIN_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()['data']
        if not response:  # pragma: no cover
            return None
        return response[txid]['raw_transaction']

    @classmethod
    def get_transaction_by_id_testnet(cls, txid):
        r = requests.get(cls.TEST_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()['data']
        if not response:  # pragma: no cover
            return None
        return response[txid]['raw_transaction']

    @classmethod
    def get_unspent(cls, address):
        endpoint = cls.MAIN_ADDRESS_API

        unspents = []
        offset = 0
        unspents_per_page = 1000
        payload = {'offset': str(offset), 'limit': str(unspents_per_page)}

        r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()

        block_height = response['context']['state']
        response = response['data'][address]
        script_pubkey = response['address']['script_hex']
        total_unspents = response['address']['unspent_output_count']

        while total_unspents > 0:
            unspents.extend(
                Unspent(
                    utxo['value'],
                    block_height - utxo['block_id'] + 1 if utxo['block_id'] != -1 else 0,
                    script_pubkey,
                    utxo['transaction_hash'],
                    utxo['index'],
                )
                for utxo in response['utxo']
            )

            total_unspents -= unspents_per_page
            offset += unspents_per_page
            payload['offset'] = str(offset)
            r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()['data'][address]

        return unspents

    @classmethod
    def get_unspent_testnet(cls, address):
        endpoint = cls.TEST_ADDRESS_API

        unspents = []
        offset = 0
        unspents_per_page = 1000
        payload = {'offset': str(offset), 'limit': unspents_per_page}

        r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()

        block_height = response['context']['state']
        response = response['data'][address]
        script_pubkey = response['address']['script_hex']
        total_unspents = response['address']['unspent_output_count']

        while total_unspents > 0:
            unspents.extend(
                Unspent(
                    utxo['value'],
                    block_height - utxo['block_id'] + 1 if utxo['block_id'] != -1 else 0,
                    script_pubkey,
                    utxo['transaction_hash'],
                    utxo['index'],
                )
                for utxo in response['utxo']
            )

            total_unspents -= unspents_per_page
            offset += unspents_per_page
            payload['offset'] = str(offset)
            r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()['data'][address]

        return unspents

    @classmethod
    def broadcast_tx(
        cls, tx_hex,
    ):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class BlockstreamAPI:
    MAIN_ENDPOINT = 'https://blockstream.info/api/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/{}'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '/utxo'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx'
    MAIN_TX_API = MAIN_ENDPOINT + 'tx/{}/hex'
    TEST_ENDPOINT = 'https://blockstream.info/testnet/api/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/{}'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '/utxo'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'tx'
    TEST_TX_API = TEST_ENDPOINT + 'tx/{}/hex'
    TX_PUSH_PARAM = 'data'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()
        funded = response['chain_stats']['funded_txo_sum'] + response['mempool_stats']['funded_txo_sum']
        spent = response['chain_stats']['spent_txo_sum'] + response['mempool_stats']['spent_txo_sum']
        return funded - spent

    @classmethod
    def get_balance_testnet(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()
        funded = response['chain_stats']['funded_txo_sum'] + response['mempool_stats']['funded_txo_sum']
        spent = response['chain_stats']['spent_txo_sum'] + response['mempool_stats']['spent_txo_sum']
        return funded - spent

    @classmethod
    def get_transactions(
        cls, address,
    ):
        #! Blockstream returns at most 50 mempool (unconfirmed) transactions and ignores the rest
        mempool_endpoint = cls.MAIN_ADDRESS_API + '/txs/mempool'
        
        endpoint = cls.MAIN_ADDRESS_API + '/txs/chain/{}'

        transactions = []

        # Add mempool (unconfirmed) transactions
        r = requests.get(mempool_endpoint.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 400:  # pragma: no cover
            return []
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()
        unconfirmed = [tx['txid'] for tx in response]

        # It is safer to raise exception if API returns exactly 50 unconfirmed
        # transactions, as there could be more that the API is unaware of.
        if len(unconfirmed) == 50:  # pragme: no cover
            raise ExcessiveAddress

        r = requests.get(endpoint.format(address, ''), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 400:  # pragma: no cover
            return []
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()

        # The first 25 confirmed transactions are shown with no
        # indication of the number of total transactions.
        total_txs = len(response)

        while total_txs > 0:
            transactions.extend(tx['txid'] for tx in response)

            response = requests.get(endpoint.format(address, transactions[-1]), timeout=DEFAULT_TIMEOUT).json()
            total_txs = len(response)

        transactions.extend(unconfirmed)

        return transactions

    @classmethod
    def get_transactions_testnet(cls, address):
        endpoint = cls.TEST_ADDRESS_API + '/txs/chain/{}'

        transactions = []

        r = requests.get(endpoint.format(address, ''), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 400:  # pragma: no cover
            return []
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()

        # The first 50 mempool and 25 confirmed transactions are shown with no
        # indication of the number of total transactions.
        total_txs = len(response)

        while total_txs > 0:
            transactions.extend(tx['txid'] for tx in response)

            response = requests.get(endpoint.format(address, transactions[-1]), timeout=DEFAULT_TIMEOUT).json()
            total_txs = len(response)

        return transactions

    @classmethod
    def get_transaction_by_id(cls, txid):
        r = requests.get(cls.MAIN_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.text

    @classmethod
    def get_transaction_by_id_testnet(cls, txid):
        r = requests.get(cls.TEST_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.text

    @classmethod
    def get_unspent(cls, address):
        # Get current block height:
        r_block = requests.get(cls.MAIN_ENDPOINT + 'blocks/tip/height', timeout=DEFAULT_TIMEOUT)
        if r_block.status_code != 200:  # pragma: no cover
            raise ConnectionError
        block_height = int(r_block.text)

        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)

        #! BlockstreamAPI blocks addresses with "too many" UTXOs.
        if r.status_code == 400 and r.text == "Too many history entries":
            raise ExcessiveAddress
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        script_pubkey = bytes_to_hex(address_to_scriptpubkey(address))

        return sorted(
            [
                Unspent(
                    tx["value"],
                    block_height - tx["status"]["block_height"] + 1 if tx["status"]["confirmed"] else 0,
                    script_pubkey,
                    tx["txid"],
                    tx["vout"],
                )
                for tx in r.json()
            ],
            key=lambda u: u.confirmations,
        )

    @classmethod
    def get_unspent_testnet(cls, address):
        # Get current block height:
        r_block = requests.get(cls.TEST_ENDPOINT + 'blocks/tip/height', timeout=DEFAULT_TIMEOUT)
        if r_block.status_code != 200:  # pragma: no cover
            raise ConnectionError
        block_height = int(r_block.text)

        r = requests.get(cls.TEST_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)

        if r.status_code == 400:  # pragma: no cover
            return []
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        script_pubkey = bytes_to_hex(address_to_scriptpubkey(address))

        return [
            Unspent(
                tx["value"],
                block_height - tx["status"]["block_height"] + 1 if tx["status"]["confirmed"] else 0,
                script_pubkey,
                tx["txid"],
                tx["vout"],
            )
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class InsightAPI:  # pragma: no cover
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_BALANCE_API = ''
    MAIN_UNSPENT_API = ''
    MAIN_TX_PUSH_API = ''
    MAIN_TX_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['transactions']

    @classmethod
    def get_transaction_by_id(cls, txid):
        r = requests.get(cls.MAIN_TX_API + txid, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()["rawtx"]

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(
                currency_to_satoshi(tx['amount'], 'btc'),
                tx['confirmations'],
                tx['scriptPubKey'],
                tx['txid'],
                tx['vout'],
            )
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class BitcoreAPI(InsightAPI):
    """ Insight API v8 """

    MAIN_ENDPOINT = 'https://api.bitcore.io/api/BTC/mainnet/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/{}'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + '/balance'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '/?unspent=true'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx/send'
    MAIN_TX_API = MAIN_ENDPOINT + 'tx/{}'
    MAIN_TX_AMOUNT_API = MAIN_TX_API
    TEST_ENDPOINT = 'https://api.bitcore.io/api/BTC/testnet/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/{}'
    TEST_BALANCE_API = TEST_ADDRESS_API + '/balance'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '/?unspent=true'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'tx/send'
    TEST_TX_API = TEST_ENDPOINT + 'tx/{}'
    TEST_TX_AMOUNT_API = TEST_TX_API
    TX_PUSH_PARAM = 'rawTx'

    @classmethod
    def get_unspent(cls, address):
        endpoint = cls.MAIN_UNSPENT_API + "&limit=100"

        unspents = []

        r = requests.get(endpoint.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()

        while len(response) > 0:
            unspents.extend(
                Unspent(
                    currency_to_satoshi(tx['value'], 'satoshi'),
                    tx['confirmations'],
                    tx['script'],
                    tx['mintTxid'],
                    tx['mintIndex'],
                )
                for tx in response
            )
            response = requests.get(
                endpoint.format(address) + "&since={}".format(response[-1]['_id']), timeout=DEFAULT_TIMEOUT
            ).json()

        return unspents

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()['balance']

    @classmethod
    def get_balance_testnet(cls, address):
        r = requests.get(cls.TEST_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()['balance']

    @classmethod
    def get_unspent_testnet(cls, address):
        endpoint = cls.TEST_UNSPENT_API + "&limit=100"

        unspents = []

        r = requests.get(endpoint.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()

        while len(response) > 0:
            unspents.extend(
                Unspent(
                    currency_to_satoshi(tx['value'], 'satoshi'),
                    tx['confirmations'],
                    tx['script'],
                    tx['mintTxid'],
                    tx['mintIndex'],
                )
                for tx in response
            )
            response = requests.get(
                endpoint.format(address) + "&since={}".format(response[-1]['_id']), timeout=DEFAULT_TIMEOUT
            ).json()

        return unspents

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        r = requests.post(
            cls.TEST_TX_PUSH_API,
            json={cls.TX_PUSH_PARAM: tx_hex, 'network': 'testnet', 'coin': 'BCH'},
            timeout=DEFAULT_TIMEOUT,
        )
        return True if r.status_code == 200 else False


class BlockchainAPI:
    ENDPOINT = 'https://blockchain.info/'
    ADDRESS_API = ENDPOINT + 'address/{}?format=json'
    UNSPENT_API = ENDPOINT + 'unspent'
    TX_PUSH_API = ENDPOINT + 'pushtx'
    TX_API = ENDPOINT + 'rawtx/'
    TX_PUSH_PARAM = 'tx'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.ADDRESS_API.format(address) + '&limit=0', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['final_balance']

    @classmethod
    def get_transactions(cls, address):
        endpoint = cls.ADDRESS_API

        transactions = []
        offset = 0
        txs_per_page = 50
        payload = {'offset': str(offset)}

        r = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json()
        total_txs = response['n_tx']

        while total_txs > 0:
            transactions.extend(tx['hash'] for tx in response['txs'])

            total_txs -= txs_per_page
            offset += txs_per_page
            payload['offset'] = str(offset)
            response = requests.get(endpoint.format(address), params=payload, timeout=DEFAULT_TIMEOUT).json()

        return transactions

    @classmethod
    def get_transaction_by_id(cls, txid):
        r = requests.get(cls.TX_API + txid + '?limit=0&format=hex', timeout=DEFAULT_TIMEOUT)
        if r.status_code == 500 and r.text == 'Transaction not found':  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.text

    @classmethod
    def get_unspent(cls, address):
        endpoint = cls.UNSPENT_API

        offset = 0
        utxos_per_page = 1000
        payload = {'active': address, 'offset': str(offset), 'limit': str(utxos_per_page)}

        r = requests.get(endpoint, params=payload, timeout=DEFAULT_TIMEOUT)

        if r.status_code == 500:  # pragma: no cover
            return []
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        unspents = [
            Unspent(tx['value'], tx['confirmations'], tx['script'], tx['tx_hash_big_endian'], tx['tx_output_n'])
            for tx in r.json()['unspent_outputs']
        ]

        #! BlockchainAPI only supports up to 1000 UTXOs.
        #! Raises an exception for addresses that may contain more UTXOs.
        if len(unspents) == 1000:
            raise ExcessiveAddress

        return unspents[::-1]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class SmartbitAPI:
    MAIN_ENDPOINT = 'https://api.smartbit.com.au/v1/blockchain/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/{}'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '/unspent'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'pushtx'
    MAIN_TX_API = MAIN_ENDPOINT + 'tx/{}/hex'
    TEST_ENDPOINT = 'https://testnet-api.smartbit.com.au/v1/blockchain/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/{}'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '/unspent'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'pushtx'
    TEST_TX_API = TEST_ENDPOINT + 'tx/{}/hex'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), params={'limit': '1'}, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['address']['total']['balance_int']

    @classmethod
    def get_balance_testnet(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API.format(address), params={'limit': '1'}, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['address']['total']['balance_int']

    @classmethod
    def get_transactions(cls, address):
        txs_per_page = 1000
        payload = {'limit': str(txs_per_page)}
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()['address']

        transactions = []
        next_link = None

        if 'transactions' in response:
            transactions.extend(t['txid'] for t in response['transactions'])
            next_link = response['transaction_paging']['next_link']

        while next_link:
            r = requests.get(next_link, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()['address']
            transactions.extend(t['txid'] for t in response['transactions'])
            next_link = response['transaction_paging']['next_link']

        return transactions

    @classmethod
    def get_transaction_by_id(cls, txid):
        r = requests.get(cls.MAIN_TX_API.format(txid) + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        if r.status_code == 400:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['hex'][0]['hex']

    @classmethod
    def get_transactions_testnet(cls, address):
        txs_per_page = 1000
        payload = {'limit': str(txs_per_page)}
        r = requests.get(cls.TEST_ADDRESS_API.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()['address']

        transactions = []
        next_link = None

        if 'transactions' in response:
            transactions.extend(t['txid'] for t in response['transactions'])
            next_link = response['transaction_paging']['next_link']

        while next_link:
            r = requests.get(next_link, params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()['address']
            transactions.extend(t['txid'] for t in response['transactions'])
            next_link = response['transaction_paging']['next_link']

        return transactions

    @classmethod
    def get_transaction_by_id_testnet(cls, txid):
        r = requests.get(cls.TEST_TX_API.format(txid) + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        if r.status_code == 400:  # pragma: no cover
            return None
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['hex'][0]['hex']

    @classmethod
    def get_unspent(cls, address):
        txs_per_page = 1000
        payload = {'limit': str(txs_per_page)}
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()

        unspents = []
        next_link = None

        if 'unspent' in response:
            unspents.extend(
                Unspent(
                    currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'],
                )
                for tx in response['unspent']
            )
            next_link = response['paging']['next_link']

        while next_link:
            r = requests.get(next_link, params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()
            unspents.extend(
                Unspent(
                    currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'],
                )
                for tx in response['unspent']
            )
            next_link = response['paging']['next_link']

        return unspents

    @classmethod
    def get_unspent_testnet(cls, address):
        txs_per_page = 1000
        payload = {'limit': str(txs_per_page)}
        r = requests.get(cls.TEST_UNSPENT_API.format(address), params=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        response = r.json()

        unspents = []
        next_link = None

        if 'unspent' in response:
            unspents.extend(
                Unspent(
                    currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'],
                )
                for tx in response['unspent']
            )
            next_link = response['paging']['next_link']

        while next_link:
            r = requests.get(next_link, params=payload, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:  # pragma: no cover
                raise ConnectionError
            response = r.json()
            unspents.extend(
                Unspent(
                    currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'],
                )
                for tx in response['unspent']
            )
            next_link = response['paging']['next_link']

        return unspents

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, json={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, json={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class NetworkAPI:
    IGNORED_ERRORS = (
        ConnectionError,
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ReadTimeout,
        ExcessiveAddress,
    )

    GET_BALANCE_MAIN = [
        BlockchairAPI.get_balance,
        BlockstreamAPI.get_balance,
        BitcoreAPI.get_balance,
        SmartbitAPI.get_balance,
        BlockchainAPI.get_balance,
    ]
    GET_TRANSACTIONS_MAIN = [
        BlockchairAPI.get_transactions,  # Limit 1000
        BlockstreamAPI.get_transactions,  # Limit 1000
        SmartbitAPI.get_transactions,  # Limit 1000
        BlockchainAPI.get_transactions,  # No limit, requires multiple requests
    ]
    GET_TRANSACTION_BY_ID_MAIN = [
        BlockchairAPI.get_transaction_by_id,
        BlockstreamAPI.get_transaction_by_id,
        SmartbitAPI.get_transaction_by_id,
        BlockchainAPI.get_transaction_by_id,
    ]
    GET_UNSPENT_MAIN = [
        BlockstreamAPI.get_unspent,
        BlockchairAPI.get_unspent,
        SmartbitAPI.get_unspent,  # Limit 1000
        BlockchainAPI.get_unspent,
        BitcoreAPI.get_unspent,  # No limit
    ]
    BROADCAST_TX_MAIN = [
        BlockchairAPI.broadcast_tx,
        BlockstreamAPI.broadcast_tx,
        BitcoreAPI.broadcast_tx,
        SmartbitAPI.broadcast_tx,  # Limit 5/minute
        BlockchainAPI.broadcast_tx,
    ]

    GET_BALANCE_TEST = [
        BlockchairAPI.get_balance_testnet,
        BlockstreamAPI.get_balance_testnet,
        BitcoreAPI.get_balance_testnet,
        SmartbitAPI.get_balance_testnet,
    ]
    GET_TRANSACTIONS_TEST = [
        BlockchairAPI.get_transactions_testnet,  # Limit 1000
        BlockstreamAPI.get_transactions_testnet,
        SmartbitAPI.get_transactions_testnet,  # Limit 1000
    ]
    GET_TRANSACTION_BY_ID_TEST = [
        BlockchairAPI.get_transaction_by_id_testnet,
        BlockstreamAPI.get_transaction_by_id_testnet,
        SmartbitAPI.get_transaction_by_id_testnet,
    ]
    GET_UNSPENT_TEST = [
        BlockstreamAPI.get_unspent_testnet,
        BlockchairAPI.get_unspent_testnet,
        SmartbitAPI.get_unspent_testnet,  # Limit 1000
        BitcoreAPI.get_unspent_testnet,  # No limit
    ]
    BROADCAST_TX_TEST = [
        BlockchairAPI.broadcast_tx_testnet,
        BlockstreamAPI.broadcast_tx_testnet,
        BitcoreAPI.broadcast_tx_testnet,
        SmartbitAPI.broadcast_tx_testnet,  # Limit 5/minute
    ]

    @classmethod
    def connect_to_node(cls, user, password, host='localhost', port=8332, use_https=False, testnet=False, path=""):
        """Connect to a remote Bitcoin node instead of using web APIs.
        Allows to connect to a testnet and mainnet Bitcoin node simultaneously.

        :param user: The RPC user to a Bitcoin node
        :type user: ``str``
        :param password: The RPC password to a Bitcoin node
        :type password: ``str``
        :param host: The host to a Bitcoin node
        :type host: ``str``
        :param port: The port to a Bitcoin node
        :type port: ``int``
        :param use_https: Connect to the Bitcoin node via HTTPS. Either a
            boolean, in which case it controls whether we connect to the node
            via HTTP or HTTPS, or a string, in which case we connect via HTTPS
            and it must be a path to the CA bundle to use. Defaults to False.
        :type use_https: ``bool`` or ``string``
        :param testnet: Defines if the node should be used for testnet
        :type testnet: ``bool``
        :returns: The node exposing its RPCs for direct interaction.
        :rtype: ``RPCHost``
        """
        node = RPCHost(user=user, password=password, host=host, port=port, use_https=use_https, path=path)

        # Inject remote node into NetworkAPI
        if testnet is False:
            cls.GET_BALANCE_MAIN = [node.get_balance]
            cls.GET_TRANSACTIONS_MAIN = [node.get_transactions]
            cls.GET_TRANSACTION_BY_ID_MAIN = [node.get_transaction_by_id]
            cls.GET_UNSPENT_MAIN = [node.get_unspent]
            cls.BROADCAST_TX_MAIN = [node.broadcast_tx]
        else:
            cls.GET_BALANCE_TEST = [node.get_balance_testnet]
            cls.GET_TRANSACTIONS_TEST = [node.get_transactions_testnet]
            cls.GET_TRANSACTION_BY_ID_TEST = [node.get_transaction_by_id_testnet]
            cls.GET_UNSPENT_TEST = [node.get_unspent_testnet]
            cls.BROADCAST_TX_TEST = [node.broadcast_tx_testnet]

        return node

    @classmethod
    def get_balance(cls, address):
        """Gets the balance of an address in satoshi.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in cls.GET_BALANCE_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_balance_testnet(cls, address):
        """Gets the balance of an address on the test network in satoshi.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in cls.GET_BALANCE_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transactions(cls, address):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in cls.GET_TRANSACTIONS_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transactions_testnet(cls, address):
        """Gets the ID of all transactions related to an address on the test
        network.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in cls.GET_TRANSACTIONS_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transaction_by_id(cls, txid):
        """Gets a raw transaction hex by its transaction id (txid).

        :param txid: The id of the transaction
        :type txid: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``string``
        """

        for api_call in cls.GET_TRANSACTION_BY_ID_MAIN:
            try:
                return api_call(txid)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transaction_by_id_testnet(cls, txid):
        """Gets a raw transaction hex by its transaction id (txid) on the test.

        :param txid: The id of the transaction
        :type txid: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``string``
        """

        for api_call in cls.GET_TRANSACTION_BY_ID_TEST:
            try:
                return api_call(txid)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_unspent(cls, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """

        for api_call in cls.GET_UNSPENT_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_unspent_testnet(cls, address):
        """Gets all unspent transaction outputs belonging to an address on the
        test network.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """

        for api_call in cls.GET_UNSPENT_TEST:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
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
            raise ConnectionError('Transaction broadcast failed, or Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the test network's blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
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
            raise ConnectionError('Transaction broadcast failed, or Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
