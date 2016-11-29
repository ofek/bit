from collections import namedtuple
from decimal import Decimal
from itertools import islice

from bit.base58 import b58decode_check
from bit.crypto import double_sha256
from bit.format import BTC
from bit.utils import bytes_to_hex, hex_to_bytes, int_to_unknown_bytes

VERSION_1 = 0x01.to_bytes(4, byteorder='little')
SEQUENCE = 0xffffffff.to_bytes(4, byteorder='little')
LOCK_TIME = 0x00.to_bytes(4, byteorder='little')
HASH_TYPE = 0x01.to_bytes(4, byteorder='little')
ZERO = b'\x00'


Output = namedtuple('Output', ('address', 'amount'))


class UTXO:
    __slots__ = ('amount', 'confirmations', 'script', 'script_len', 'txid', 'txindex')

    def __init__(self, amount, confirmations, script, txid, txindex):
        self.amount = amount
        self.confirmations = confirmations
        self.script = script
        self.txid = txid
        self.txindex = txindex

    def __eq__(self, other):
        return (self.amount == other.amount and
                self.confirmations == other.confirmations and
                self.script == other.script and
                self.txid == other.txid and
                self.txindex == other.txindex)

    def __repr__(self):
        return 'UTXO({}, {}, {}, {}, {})'.format(
            repr(self.amount),
            repr(self.confirmations),
            repr(self.script),
            repr(self.txid),
            repr(self.txindex)
        )


def estimate_tx_fee(n_in, n_out, satoshis):
    estimated_size = Decimal(str(n_in))*148 + Decimal(str(n_out))*34 + 10
    return estimated_size * satoshis / BTC


def construct_output_block(outputs):
    output_block = b''

    for data in outputs:
        address, amount = data
        script = b'v\xa9\x14' + b58decode_check(address)[1:] + b'\x88\xac'
        amount = int(amount * BTC)

        output_block += amount.to_bytes(8, byteorder='little')
        output_block += int_to_unknown_bytes(len(script), byteorder='little')
        output_block += script

    return output_block


def construct_input_block(utxos):
    input_block = b''
    sequence = SEQUENCE

    for utxo in utxos:
        input_block += (
            utxo.txid +
            utxo.txindex +
            utxo.script_len +
            utxo.script +
            sequence
        )

    return input_block


def create_signed_transaction(private_key, utxos, outputs):
    utxos = utxos.copy()

    public_key = private_key.public_key()
    public_key_len = len(public_key).to_bytes(1, byteorder='little')

    version = VERSION_1
    lock_time = LOCK_TIME
    sequence = SEQUENCE
    hash_type = HASH_TYPE
    input_count = int_to_unknown_bytes(len(utxos), byteorder='little')
    output_count = int_to_unknown_bytes(len(outputs), byteorder='little')
    output_block = construct_output_block(outputs)

    for utxo in utxos:
        utxo.txid = hex_to_bytes(utxo.txid)[::-1]
        utxo.txindex = utxo.txindex.to_bytes(4, byteorder='little')
        utxo.script = hex_to_bytes(utxo.script)
        utxo.script_len = int_to_unknown_bytes(len(utxo.script), byteorder='little')

    inputs_signed = 0

    for utxo in utxos:

        hashed = double_sha256(
            version +
            input_count +
            b''.join(utxo.txid + utxo.txindex + ZERO + sequence
                     for utxo in islice(utxos, inputs_signed)) +
            utxo.txid +
            utxo.txindex +
            utxo.script_len +
            utxo.script +
            sequence +
            b''.join(utxo.txid + utxo.txindex + ZERO + sequence
                     for utxo in islice(utxos, inputs_signed, None)) +
            output_count +
            output_block +
            lock_time +
            hash_type
        )

        signature = private_key.sign(hashed) + hash_type

        script_sig = (
            len(signature).to_bytes(1, byteorder='little') +
            signature +
            public_key_len +
            public_key
        )

        utxo.script = script_sig
        utxo.script_len = int_to_unknown_bytes(len(script_sig), byteorder='little')

        inputs_signed += 1

    return bytes_to_hex(
        version +
        input_count +
        construct_input_block(utxos) +
        output_count +
        output_block +
        lock_time
    )



















