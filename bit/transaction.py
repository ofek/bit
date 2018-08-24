import logging
from collections import namedtuple
from itertools import islice
import re

from bit.crypto import double_sha256, sha256
from bit.exceptions import InsufficientFunds
from bit.format import (address_to_public_key_hash, segwit_scriptpubkey,
                        TEST_SCRIPT_HASH, MAIN_SCRIPT_HASH, TEST_PUBKEY_HASH,
                        MAIN_PUBKEY_HASH)
from bit.network.rates import currency_to_satoshi_cached
from bit.utils import (
    bytes_to_hex, chunk_data, hex_to_bytes, int_to_unknown_bytes, int_to_varint,
    script_push, get_signatures_from_script, read_bytes, read_var_int, read_var_string,
    read_segwit_string
)

from bit.format import verify_sig, get_version
from bit.base58 import b58decode_check
from bit.base32 import decode as segwit_decode

VERSION_1 = 0x01.to_bytes(4, byteorder='little')
MARKER = b'\x00'
FLAG = b'\x01'
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
    __slots__ = ('script_sig', 'script_sig_len', 'txid', 'txindex', 'witness',
                 'sequence')

    def __init__(self, script_sig, txid, txindex, witness=b'',
                 sequence=SEQUENCE):

        self.script_sig = script_sig
        self.script_sig_len = int_to_varint(len(script_sig))
        self.txid = txid
        self.txindex = txindex
        self.witness = witness
        self.sequence = sequence

    def __eq__(self, other):
        return (self.script_sig == other.script_sig and
                self.script_sig_len == other.script_sig_len and
                self.txid == other.txid and
                self.txindex == other.txindex and
                self.witness == other.witness and
                self.sequence == other.sequence)

    def __repr__(self):
        if self.is_segwit():
            return 'TxIn({}, {}, {}, {}, {}, {})'.format(
                repr(self.script_sig),
                repr(self.script_sig_len),
                repr(self.txid),
                repr(self.txindex),
                repr(self.witness),
                repr(self.sequence)
            )
        return 'TxIn({}, {}, {}, {}, {})'.format(
            repr(self.script_sig),
            repr(self.script_sig_len),
            repr(self.txid),
            repr(self.txindex),
            repr(self.sequence)
        )

    def __bytes__(self):
        return b''.join([
            self.txid,
            self.txindex,
            self.script_sig_len,
            self.script_sig,
            self.sequence
        ])

    def is_segwit(self):
        return self.witness


Output = namedtuple('Output', ('address', 'amount', 'currency'))


class TxOut:
    __slots__ = ('amount', 'script_pubkey_len', 'script_pubkey')

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey
        self.script_pubkey_len = int_to_varint(len(script_pubkey))

    def __eq__(self, other):
        return (self.amount == other.amount and
                self.script_pubkey == other.script_pubkey and
                self.script_pubkey_len == other.script_pubkey_len)

    def __repr__(self):
        return 'TxOut({}, {}, {})'.format(
            repr(self.amount),
            repr(self.script_pubkey),
            repr(self.script_pubkey_len)
        )

    def __bytes__(self):
        return b''.join([
            self.amount,
            self.script_pubkey_len,
            self.script_pubkey
        ])


class TxObj:
    __slots__ = ('version', 'marker', 'flag', 'TxIn', 'TxOut', 'locktime')

    def __init__(self, version, TxIn, TxOut, locktime):
        segwit_tx = any([i.witness for i in TxIn])
        self.version = version
        self.marker = MARKER if segwit_tx else b''
        self.flag = FLAG if segwit_tx else b''
        self.TxIn = TxIn
        if segwit_tx:
            for i in self.TxIn:
                i.witness = i.witness if i.witness else b'\x00'
        self.TxOut = TxOut
        self.locktime = locktime

    def __eq__(self, other):
        return (self.version == other.version and
                self.marker == other.marker and
                self.flag == other.flag and
                self.TxIn == other.TxIn and
                self.TxOut == other.TxOut and
                self.locktime == other.locktime)

    def __repr__(self):
        return 'TxObj({}, {}, {}, {})'.format(
            repr(self.version),
            repr(self.TxIn),
            repr(self.TxOut),
            repr(self.locktime)
        )

    def __bytes__(self):
        inp = int_to_varint(len(self.TxIn)) + b''.join(map(bytes, self.TxIn))
        out = int_to_varint(len(self.TxOut)) + b''.join(map(bytes, self.TxOut))
        wit = b''.join([w.witness for w in self.TxIn])
        return b''.join([
            self.version,
            self.marker,
            self.flag,
            inp,
            out,
            wit,
            self.locktime
        ])

    def to_hex(self):
        return bytes_to_hex(bytes(self))

    @classmethod
    def is_segwit(cls, tx):
        if isinstance(tx, cls):
            return tx.marker + tx.flag == MARKER + FLAG
        elif not isinstance(tx, bytes):
            tx = hex_to_bytes(tx)
        return tx[4:6] == MARKER + FLAG


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


def deserialize(tx):
    if isinstance(tx, str) and re.match('^[0-9a-fA-F]*$', tx):
        return deserialize(hex_to_bytes(tx))

    segwit_tx = TxObj.is_segwit(tx)

    version, tx = read_bytes(tx, 4)

    if segwit_tx:
        _, tx = read_bytes(tx, 1)  # ``marker`` is nulled
        _, tx = read_bytes(tx, 1)  # ``flag`` is nulled

    ins, tx = read_var_int(tx)
    inputs = []
    for i in range(ins):
        txid, tx = read_bytes(tx, 32)
        txindex, tx = read_bytes(tx, 4)
        script_sig, tx = read_var_string(tx)
        sequence, tx = read_bytes(tx, 4)
        inputs.append(TxIn(script_sig, txid, txindex, sequence=sequence))

    outs, tx = read_var_int(tx)
    outputs = []
    for _ in range(outs):
        amount, tx = read_bytes(tx, 8)
        script_pubkey, tx = read_var_string(tx)
        outputs.append(TxOut(amount, script_pubkey))

    if segwit_tx:
        for i in range(ins):
            wnum, tx = read_var_int(tx)
            witness = int_to_varint(wnum)
            for _ in range(wnum):
                w, tx = read_segwit_string(tx)
                witness += w
            inputs[i].witness = witness

    locktime, _ = read_bytes(tx, 4)

    txobj = TxObj(version, inputs, outputs, locktime)

    return txobj


def sanitize_tx_data(unspents, outputs, fee, leftover, combine=True, message=None, compressed=True, version='main'):
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

    # Sanity check: If spending from main-/testnet, then all output addresses must also be for main-/testnet.
    for output in outputs:
        dest, amount = output
        if amount:  # ``dest`` could be a text to be stored in the blockchain; but only if ``amount`` is exactly zero.
            vs = get_version(dest)
            if vs and vs != version:
                raise ValueError('Cannot send to ' + vs + 'net address when spending from a ' + version + 'net address.')

    outputs.extend(messages)

    return unspents, outputs


def address_to_scriptpubkey(address):
    # Raise ValueError if we cannot identify the address.
    get_version(address)
    try:
        version = b58decode_check(address)[:1]
    except ValueError:
        witver, data = segwit_decode(address)
        return segwit_scriptpubkey(witver, data)

    if version == MAIN_PUBKEY_HASH or version == TEST_PUBKEY_HASH:
        return (OP_DUP + OP_HASH160 + OP_PUSH_20 +
                address_to_public_key_hash(address) +
                OP_EQUALVERIFY + OP_CHECKSIG)
    elif version == MAIN_SCRIPT_HASH or version == TEST_SCRIPT_HASH:
        return (OP_HASH160 + OP_PUSH_20 +
                address_to_public_key_hash(address) +
                OP_EQUAL)


def construct_outputs(outputs):
    outputs_obj = []

    for data in outputs:
        dest, amount = data

        # P2PKH/P2SH/Bech32
        if amount:
            script_pubkey = address_to_scriptpubkey(dest)

            amount = amount.to_bytes(8, byteorder='little')

        # Blockchain storage
        else:
            script_pubkey = (OP_RETURN +
                             len(dest).to_bytes(1, byteorder='little') +
                             dest)

            amount = b'\x00\x00\x00\x00\x00\x00\x00\x00'

        outputs_obj.append(TxOut(amount, script_pubkey))

    return outputs_obj


def sign_legacy_tx(private_key, tx, *, unspents):
    """Signs inputs in provided transaction object for which unspents
    are provided and can be signed by the private key.

    :param private_key: Private key
    :type private_key: ``PrivateKey`` or ``MultiSig``
    :param tx: Transaction object
    :type tx: ``TxObj``
    :param unspents: For inputs to be signed their corresponding Unspent objects
                     must be provided.
    :returns: The signed transaction as hex.
    :rtype: ``str``
    """

    # input_dict contains those unspents that can be signed by private_key,
    # providing additional information for segwit-inputs (the amount to spend)
    input_dict = {}
    try:
        for unspent in unspents:
            if not private_key.can_sign_unspent(unspent):
                continue
            tx_input = hex_to_bytes(unspent.txid)[::-1] + unspent.txindex.to_bytes(4, byteorder='little')
            input_dict[tx_input] = unspent.to_dict()
    except TypeError:
        raise ValueError('Please provide as unspents at least all inputs to be signed with the function call.')

    # Determine input indices to sign from input_dict (allows for transaction batching)
    sign_inputs = [j for j, i in enumerate(tx.TxIn) if i.txid+i.txindex in input_dict]

    version = tx.version
    lock_time = tx.locktime
    hash_type = HASH_TYPE

    input_count = int_to_varint(len(tx.TxIn))
    output_count = int_to_varint(len(tx.TxOut))

    output_block = b''.join([bytes(o) for o in tx.TxOut])

    for i in sign_inputs:

        public_key = private_key.public_key
        public_key_push = script_push(len(public_key))

        script_code = private_key.scriptcode
        script_code_len = int_to_varint(len(script_code))

        hashed = sha256(
            version +
            input_count +
            b''.join(ti.txid + ti.txindex + OP_0 + ti.sequence
                     for ti in islice(tx.TxIn, i)) +
            tx.TxIn[i].txid +
            tx.TxIn[i].txindex +
            script_code_len +
            script_code +
            tx.TxIn[i].sequence +
            b''.join(ti.txid + ti.txindex + OP_0 + ti.sequence
                     for ti in islice(tx.TxIn, i + 1, None)) +
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
            if tx.TxIn[i].script_sig:  # If tx is already partially signed: Make a dictionary of the provided signatures with public-keys as key-values
                sig_list = get_signatures_from_script(tx.TxIn[i].script_sig)
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
                      public_key_push +
                      public_key
                     )

        # Providing the signature(s) to the input
        tx.TxIn[i].script_sig = script_sig
        tx.TxIn[i].script_sig_len = int_to_varint(len(script_sig))

    return tx.to_hex()


def create_new_transaction(private_key, unspents, outputs):

    version = VERSION_1
    lock_time = LOCK_TIME
    outputs = construct_outputs(outputs)

    # Optimize for speed, not memory, by pre-computing values.
    inputs = []
    for unspent in unspents:
        script_sig = b''  # empty scriptSig for new unsigned transaction.
        txid = hex_to_bytes(unspent.txid)[::-1]
        txindex = unspent.txindex.to_bytes(4, byteorder='little')

        inputs.append(TxIn(script_sig, txid, txindex))

    tx_unsigned = TxObj(version, inputs, outputs, lock_time)

    tx = sign_legacy_tx(private_key, tx_unsigned, unspents=unspents)
    return tx
