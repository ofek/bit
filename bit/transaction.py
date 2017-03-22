from collections import namedtuple
from itertools import islice

from bit.crypto import double_sha256, sha256
from bit.exceptions import InsufficientFunds
from bit.format import address_to_public_key_hash
from bit.network.rates import currency_to_satoshi_cached
from bit.utils import (
    bytes_to_hex, chunk_data, hex_to_bytes, int_to_unknown_bytes
)

VERSION_1 = 0x01.to_bytes(4, byteorder='little')
SEQUENCE = 0xffffffff.to_bytes(4, byteorder='little')
LOCK_TIME = 0x00.to_bytes(4, byteorder='little')
HASH_TYPE = 0x01.to_bytes(4, byteorder='little')

OP_0 = b'\x00'
OP_CHECKLOCKTIMEVERIFY = b'\xb1'
OP_CHECKSIG = b'\xac'
OP_DUP = b'v'
OP_EQUALVERIFY = b'\x88'
OP_HASH160 = b'\xa9'
OP_PUSH_20 = b'\x14'
OP_RETURN = b'\x6a'

MESSAGE_LIMIT = 40


class TxIn:
    __slots__ = ('script', 'script_len', 'txid', 'txindex')

    def __init__(self, script, script_len, txid, txindex):
        self.script = script
        self.script_len = script_len
        self.txid = txid
        self.txindex = txindex

    def __eq__(self, other):
        return (self.script == other.script and
                self.script_len == other.script_len and
                self.txid == other.txid and
                self.txindex == other.txindex)

    def __repr__(self):
        return 'TxIn({}, {}, {}, {})'.format(
            repr(self.script),
            repr(self.script_len),
            repr(self.txid),
            repr(self.txindex)
        )


Output = namedtuple('Output', ('address', 'amount', 'currency'))


def calc_txid(tx_hex):
    return bytes_to_hex(double_sha256(hex_to_bytes(tx_hex))[::-1])


def estimate_tx_fee(n_in, n_out, satoshis, compressed):

    if not satoshis:
        return 0

    estimated_size = (
        n_in * (148 if compressed else 180)
        + len(int_to_unknown_bytes(n_in, byteorder='little'))
        + n_out * 34
        + len(int_to_unknown_bytes(n_out, byteorder='little'))
        + 8
    )

    return estimated_size * satoshis


def sanitize_tx_data(unspents, outputs, fee, leftover, combine=True, message=None, compressed=True):

    outputs = outputs.copy()

    for i, output in enumerate(outputs):
        dest, amount, currency = output
        outputs[i] = (dest, currency_to_satoshi_cached(amount, currency))

    if not unspents:
        raise ValueError('Transactions must have at least one unspent.')

    # Temporary storage so all outputs precede messages.
    messages = []

    if message:
        message_chunks = chunk_data(message.encode('utf-8'), MESSAGE_LIMIT)

        for message in message_chunks:
            messages.append((message, 0))

    # Include return address in fee estimate.
    fee = estimate_tx_fee(len(unspents), len(outputs) + len(messages) + 1, fee, compressed)
    total_out = sum(out[1] for out in outputs) + fee

    total_in = 0

    if combine:
        unspents = unspents.copy()
        total_in += sum(unspent.amount for unspent in unspents)

    else:
        unspents = sorted(unspents, key=lambda x: x.amount)

        index = 0

        for index, unspent in enumerate(unspents):
            total_in += unspent.amount

            if total_in >= total_out:
                break

        unspents[:] = unspents[:index + 1]

    remaining = total_in - total_out

    if remaining > 0:
        outputs.append((leftover, remaining))
    elif remaining < 0:
        raise InsufficientFunds('Balance {} is less than {} (including '
                                'fee).'.format(total_in, total_out))

    outputs.extend(messages)

    return unspents, outputs


def construct_output_block(outputs):

    output_block = b''

    for data in outputs:
        dest, amount = data

        # Real recipient
        if amount:
            script = (OP_DUP + OP_HASH160 + OP_PUSH_20 +
                      address_to_public_key_hash(dest) +
                      OP_EQUALVERIFY + OP_CHECKSIG)

            output_block += amount.to_bytes(8, byteorder='little')

        # Blockchain storage
        else:
            script = (OP_RETURN +
                      len(dest).to_bytes(1, byteorder='little') +
                      dest)

            output_block += b'\x00\x00\x00\x00\x00\x00\x00\x00'

        output_block += int_to_unknown_bytes(len(script), byteorder='little')
        output_block += script

    return output_block


def construct_input_block(inputs):

    input_block = b''
    sequence = SEQUENCE

    for txin in inputs:
        input_block += (
            txin.txid +
            txin.txindex +
            txin.script_len +
            txin.script +
            sequence
        )

    return input_block


def create_p2pkh_transaction(private_key, unspents, outputs):

    public_key = private_key.public_key
    public_key_len = len(public_key).to_bytes(1, byteorder='little')

    version = VERSION_1
    lock_time = LOCK_TIME
    sequence = SEQUENCE
    hash_type = HASH_TYPE
    input_count = int_to_unknown_bytes(len(unspents), byteorder='little')
    output_count = int_to_unknown_bytes(len(outputs), byteorder='little')
    output_block = construct_output_block(outputs)

    # Optimize for speed, not memory, by pre-computing values.
    inputs = []
    for unspent in unspents:
        script = hex_to_bytes(unspent.script)
        script_len = int_to_unknown_bytes(len(script), byteorder='little')
        txid = hex_to_bytes(unspent.txid)[::-1]
        txindex = unspent.txindex.to_bytes(4, byteorder='little')

        inputs.append(TxIn(script, script_len, txid, txindex))

    for i, txin in enumerate(inputs):

        hashed = sha256(
            version +
            input_count +
            b''.join(ti.txid + ti.txindex + OP_0 + sequence
                     for ti in islice(inputs, i)) +
            txin.txid +
            txin.txindex +
            txin.script_len +
            txin.script +
            sequence +
            b''.join(ti.txid + ti.txindex + OP_0 + sequence
                     for ti in islice(inputs, i + 1, None)) +
            output_count +
            output_block +
            lock_time +
            hash_type
        )

        signature = private_key.sign(hashed) + b'\x01'

        script_sig = (
            len(signature).to_bytes(1, byteorder='little') +
            signature +
            public_key_len +
            public_key
        )

        txin.script = script_sig
        txin.script_len = int_to_unknown_bytes(len(script_sig), byteorder='little')

    return bytes_to_hex(
        version +
        input_count +
        construct_input_block(inputs) +
        output_count +
        output_block +
        lock_time
    )
