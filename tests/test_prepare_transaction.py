import json

import pytest

from bit.network.meta import Unspent
from bit.transaction import address_to_scriptpubkey, deserialize
from bit.wallet import MultiSig, MultiSigTestnet, PrivateKey, PrivateKeyTestnet


@pytest.mark.parametrize('wallet_class', [PrivateKey, PrivateKeyTestnet, MultiSig, MultiSigTestnet])
@pytest.mark.parametrize('message', [None, 'Happy new year', 'こんにちは' * 12, b'\x00\xff' * 30])
def test_prepare_and_sign_message_offline(wallet_class, message):
    key_class = PrivateKeyTestnet if wallet_class in (PrivateKeyTestnet, MultiSigTestnet) else PrivateKey
    key = key_class.from_int(1)
    if wallet_class in (MultiSig, MultiSigTestnet):
        other_key = key_class.from_int(2)
        wallet = wallet_class(key, [key.public_key, other_key.public_key], 2)
        unspent_type = 'p2sh'
    else:
        wallet = key
        unspent_type = 'p2pkh'
    unspent = Unspent(100000, 1, address_to_scriptpubkey(wallet.address).hex(), '11' * 32, 0, unspent_type)
    prepared = wallet_class.prepare_transaction(
        wallet.address,
        [(wallet.address, 1000, 'satoshi')],
        fee=1,
        unspents=[unspent],
        message=message,
        message_is_hex=isinstance(message, bytes),
    )
    data = json.loads(prepared)
    assert data['outputs'][0] == [wallet.address, 1000]

    signed = wallet.sign_transaction(prepared)
    transaction = deserialize(signed)
    assert transaction.TxOut[0].script_pubkey == address_to_scriptpubkey(wallet.address)
    messages = [output.script_pubkey for output in transaction.TxOut if output.amount == b'\x00' * 8]
    if message is None:
        assert messages == []
    else:
        raw = message if isinstance(message, bytes) else message.encode('utf-8')
        assert b''.join(script[2:] for script in messages) == raw
        assert all(script[0] == 0x6A and script[1] == len(script) - 2 for script in messages)
        assert all(0 < len(script) - 2 <= 80 for script in messages)
