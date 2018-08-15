import logging
from collections import namedtuple
from itertools import islice
import re

from bit.crypto import double_sha256, sha256
from bit.exceptions import InsufficientFunds
from bit.format import address_to_public_key_hash, TEST_SCRIPT_HASH, MAIN_SCRIPT_HASH
from bit.network.rates import currency_to_satoshi_cached
from bit.utils import (
    bytes_to_hex, chunk_data, hex_to_bytes, int_to_unknown_bytes, int_to_varint, script_push, get_signatures_from_script
)

from bit.format import verify_sig
from bit.base58 import b58decode_check

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
OP_EQUAL = b'\x87'

MESSAGE_LIMIT = 40


class TxIn:
    __slots__ = ('script', 'script_len', 'txid', 'txindex', 'sequence')

    def __init__(self, script, txid, txindex, sequence=SEQUENCE):
        self.script = script
        self.script_len = int_to_varint(len(script))
        self.txid = txid
        self.txindex = txindex
        self.sequence = sequence

    def __eq__(self, other):
        return (self.script == other.script and
                self.script_len == other.script_len and
                self.txid == other.txid and
                self.txindex == other.txindex and
                self.sequence == other.sequence)

    def __repr__(self):
        return 'TxIn({}, {}, {}, {}, {})'.format(
            repr(self.script),
            repr(self.script_len),
            repr(self.txid),
            repr(self.txindex),
            repr(self.sequence)
        )


Output = namedtuple('Output', ('address', 'amount', 'currency'))


class TxOut:
    __slots__ = ('value', 'script_len', 'script')

    def __init__(self, value, script):
        self.value = value
        self.script = script
        self.script_len = int_to_varint(len(script))

    def __eq__(self, other):
        return (self.value == other.value and
                self.script == other.script and
                self.script_len == other.script_len)

    def __repr__(self):
        return 'TxOut({}, {}, {})'.format(
            repr(self.value),
            repr(self.script),
            repr(self.script_len)
        )


class TxObj:
    __slots__ = ('version', 'TxIn', 'input_count', 'TxOut', 'output_count', 'locktime')

    def __init__(self, version, TxIn, TxOut, locktime):
        self.version = version
        self.TxIn = TxIn
        self.input_count = len(TxIn)
        self.TxOut = TxOut
        self.output_count = len(TxOut)
        self.locktime = locktime

    def __eq__(self, other):
        return (self.version == other.version and
                self.TxIn == other.TxIn and
                self.input_count == other.input_count and
                self.TxOut == other.TxOut and
                self.output_count == other.output_count and
                self.locktime == other.locktime)

    def __repr__(self):
        return 'TxObj({}, {}, {}, {})'.format(
            repr(self.version),
            repr(self.TxIn),
            repr(self.TxOut),
            repr(self.locktime)
        )


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

    estimated_fee = estimated_size * satoshis

    logging.debug('Estimated fee: {} satoshis for {} bytes'.format(estimated_fee, estimated_size))

    return estimated_fee


def deserialize(txhex):
    if isinstance(txhex, str) and re.match('^[0-9a-fA-F]*$', txhex):
        #return deserialize(binascii.unhexlify(txhex))
        return deserialize(hex_to_bytes(txhex))

    pos = [0]

    def read_as_int(bytez):
        pos[0] += bytez
        return int(bytes_to_hex(txhex[pos[0]-bytez:pos[0]][::-1]), base=16)

    def read_var_int():
        pos[0] += 1

        val = int(bytes_to_hex(txhex[pos[0]-1:pos[0]]), base=16)
        if val < 253:
            return val
        return read_as_int(pow(2, val - 252))

    def read_bytes(bytez):
        pos[0] += bytez
        return txhex[pos[0]-bytez:pos[0]]

    def read_var_string():
        size = read_var_int()
        return read_bytes(size)

    version = read_as_int(4).to_bytes(4, byteorder='little')

    ins = read_var_int()
    inputs = []
    for _ in range(ins):
        txid = read_bytes(32)
        txindex = read_as_int(4).to_bytes(4, byteorder='little')
        script = read_var_string()
        sequence = read_as_int(4).to_bytes(4, byteorder='little')
        inputs.append(TxIn(script, txid, txindex, sequence))

    outs = read_var_int()
    outputs = []
    for _ in range(outs):
        value = read_as_int(8).to_bytes(8, byteorder='little')
        script = read_var_string()
        outputs.append(TxOut(value, script))

    locktime = read_as_int(4).to_bytes(4, byteorder='little')

    txobj = TxObj(version, inputs, outputs, locktime)

    return txobj


def sanitize_tx_data(unspents, outputs, fee, leftover, combine=True, message=None, compressed=True):
    """
    sanitize_tx_data()

    fee is in satoshis per byte.
    """

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

    # Include return address in output count.
    num_outputs = len(outputs) + len(messages) + 1
    sum_outputs = sum(out[1] for out in outputs)

    total_in = 0

    if combine:
        # calculated_fee is in total satoshis.
        calculated_fee = estimate_tx_fee(len(unspents), num_outputs, fee, compressed)
        total_out = sum_outputs + calculated_fee
        unspents = unspents.copy()
        total_in += sum(unspent.amount for unspent in unspents)

    else:
        unspents = sorted(unspents, key=lambda x: x.amount)

        index = 0

        for index, unspent in enumerate(unspents):
            total_in += unspent.amount
            calculated_fee = estimate_tx_fee(len(unspents[:index + 1]), num_outputs, fee, compressed)
            total_out = sum_outputs + calculated_fee

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


def construct_outputs(outputs):
    outputs_obj = []

    for data in outputs:
        dest, amount = data

        # P2SH
        if amount and (b58decode_check(dest)[0:1] == MAIN_SCRIPT_HASH or 
                       b58decode_check(dest)[0:1] == TEST_SCRIPT_HASH):
            script = (OP_HASH160 + OP_PUSH_20 +
                      address_to_public_key_hash(dest) +
                      OP_EQUAL)

            amount = amount.to_bytes(8, byteorder='little')

        # P2PKH
        elif amount:
            script = (OP_DUP + OP_HASH160 + OP_PUSH_20 +
                      address_to_public_key_hash(dest) +
                      OP_EQUALVERIFY + OP_CHECKSIG)

            amount = amount.to_bytes(8, byteorder='little')

        # Blockchain storage
        else:
            script = (OP_RETURN +
                      len(dest).to_bytes(1, byteorder='little') +
                      dest)

            amount = b'\x00\x00\x00\x00\x00\x00\x00\x00'

        outputs_obj.append(TxOut(amount, script))

    return outputs_obj


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

def sign_legacy_tx(private_key, tx, j=-1):
# j is the input to be signed and can be a single index, a list of indices, or denote all inputs (-1)

    if not isinstance(tx, TxObj):
        tx = deserialize(tx)

    version = tx.version
    lock_time = tx.locktime
    hash_type = HASH_TYPE

    input_count = int_to_varint(tx.input_count)
    output_count = int_to_varint(tx.output_count)

    output_block = b''
    for i in range(tx.output_count):
        output_block += tx.TxOut[i].value
        output_block += tx.TxOut[i].script_len
        output_block += tx.TxOut[i].script

    inputs = tx.TxIn

    if j<0:
        j = range(len(inputs))
    elif not isinstance(j, list):
        j = [j]

    for i in j:

        public_key = private_key.public_key
        public_key_len = script_push(len(public_key))

        scriptCode = private_key.scriptcode
        scriptCode_len = int_to_varint(len(scriptCode))

        hashed = sha256(
            version +
            input_count +
            b''.join(ti.txid + ti.txindex + OP_0 + ti.sequence
                     for ti in islice(inputs, i)) +
            inputs[i].txid +
            inputs[i].txindex +
            scriptCode_len +
            scriptCode +
            inputs[i].sequence +
            b''.join(ti.txid + ti.txindex + OP_0 + ti.sequence
                     for ti in islice(inputs, i + 1, None)) +
            output_count +
            output_block +
            lock_time +
            hash_type
        )

        signature = private_key.sign(hashed) + b'\x01'

        # ------------------------------------------------------------------
        if private_key.instance == 'MultiSig' or private_key.instance == 'MultiSigTestnet':

            script_blob = b''
            sigs = {}
            if tx.TxIn[i].script:  # If tx is already partially signed: Make a dictionary of the provided signatures with public-keys as key-values
                sig_list = get_signatures_from_script(tx.TxIn[i].script)
                if len(sig_list) > private_key.m:
                    raise TypeError('Transaction is already signed with {} of {} needed signatures.').format(len(sig_list), private_key.m)
                for sig in sig_list:
                    for pub in private_key.public_keys:
                        if verify_sig(sig[:-1], hashed, hex_to_bytes(pub)):
                            sigs[pub] = sig
                script_blob += b'\x00' * (private_key.m - len(sig_list)-1)  # Bitcoin Core convention: Every missing signature is denoted by 0x00. Only used for already partially-signed scriptSigs.

            sigs[bytes_to_hex(public_key)] = signature

            script_sig = b''  # P2SH -  Multisig
            for pub in private_key.public_keys:  # Sort the signatures according to the public-key list:
                if pub in sigs:
                    sig = sigs[pub]
                    length = script_push(len(sig))
                    script_sig += length + sig

            script_sig = b'\x00' + script_sig + script_blob
            script_sig += script_push(len(private_key.redeemscript)) + private_key.redeemscript

        # ------------------------------------------------------------------
        else:
            script_sig = (  # P2PKH
                      len(signature).to_bytes(1, byteorder='little') +
                      signature +
                      public_key_len +
                      public_key
                     )

        inputs[i].script = script_sig
        inputs[i].script_len = int_to_varint(len(script_sig))

    return bytes_to_hex(
        version +
        input_count +
        construct_input_block(inputs) +
        output_count +
        output_block +
        lock_time
    )


def create_new_transaction(private_key, unspents, outputs):

    version = VERSION_1
    lock_time = LOCK_TIME
    outputs = construct_outputs(outputs)

    # Optimize for speed, not memory, by pre-computing values.
    inputs = []
    for unspent in unspents:
        script = b''  # empty scriptSig for new unsigned transaction.
        txid = hex_to_bytes(unspent.txid)[::-1]
        txindex = unspent.txindex.to_bytes(4, byteorder='little')

        inputs.append(TxIn(script, txid, txindex))

    tx_unsigned = TxObj(version, inputs, outputs, lock_time)

    tx = sign_legacy_tx(private_key, tx_unsigned)
    return tx
