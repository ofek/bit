import requests


def get_decoded_tx(tx_hex, test=False):
    url = 'http://{}btc.blockr.io/api/v1/tx/decode'.format('t' if test else '')
    return requests.post(url, data={'hex': tx_hex}).json()
