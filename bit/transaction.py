import logging
from collections import namedtuple
from itertools import islice
import math
import re
from random import randint, shuffle
from bit.crypto import double_sha256, sha256
from bit.exceptions import InsufficientFunds
from bit.format import address_to_public_key_hash, segwit_scriptpubkey
from bit.network.rates import currency_to_satoshi_cached
from bit.utils import (
    bytes_to_hex,
    chunk_data,
    hex_to_bytes,
    int_to_unknown_bytes,
    int_to_varint,
    script_push,
    get_signatures_from_script,
    read_bytes,
    read_var_int,
    read_var_string,
    read_segwit_string,
)

from bit.format import verify_sig, get_version
from bit.base58 import b58decode_check
from bit.base32 import decode as segwit_decode

from bit.constants import (
    TEST_SCRIPT_HASH,
    MAIN_SCRIPT_HASH,
    TEST_PUBKEY_HASH,
    MAIN_PUBKEY_HASH,
    VERSION_1,
    MARKER,
    FLAG,
    SEQUENCE,
    LOCK_TIME,
    HASH_TYPE,
    OP_0,
    OP_CHECKLOCKTIMEVERIFY,
    OP_CHECKSIG,
    OP_DUP,
    OP_EQUALVERIFY,
    OP_HASH160,
    OP_PUSH_20,
    OP_RETURN,
    OP_EQUAL,
    MESSAGE_LIMIT,
)


class TxIn:
    __slots__ = ('script_sig', 'script_sig_len', 'txid', 'txindex', 'witness', 'amount', 'sequence', 'segwit_input')

    def __init__(self, script_sig, txid, txindex, witness=b'', amount=None, sequence=SEQUENCE, segwit_input=False):

        self.script_sig = script_sig
        self.script_sig_len = int_to_varint(len(script_sig))
        self.txid = txid
        self.txindex = txindex
        self.witness = witness
        self.amount = amount
        self.sequence = sequence
        self.segwit_input = segwit_input

    def __eq__(self, other):
        return (
            self.script_sig == other.script_sig
            and self.script_sig_len == other.script_sig_len
            and self.txid == other.txid
            and self.txindex == other.txindex
            and self.witness == other.witness
            and self.amount == other.amount
            and self.sequence == other.sequence
            and self.segwit_input == other.segwit_input
        )

    def __repr__(self):
        if self.is_segwit():
            return 'TxIn({}, {}, {}, {}, {}, {}, {})'.format(
                repr(self.script_sig),
                repr(self.script_sig_len),
                repr(self.txid),
                repr(self.txindex),
                repr(self.witness),
                repr(self.amount),
                repr(self.sequence),
            )
        return 'TxIn({}, {}, {}, {}, {})'.format(
            repr(self.script_sig), repr(self.script_sig_len), repr(self.txid), repr(self.txindex), repr(self.sequence)
        )

    def __bytes__(self):
        return b''.join([self.txid, self.txindex, self.script_sig_len, self.script_sig, self.sequence])

    def is_segwit(self):
        return self.segwit_input or self.witness


Output = namedtuple('Output', ('address', 'amount', 'currency'))


class TxOut:
    __slots__ = ('amount', 'script_pubkey_len', 'script_pubkey')

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey
        self.script_pubkey_len = int_to_varint(len(script_pubkey))

    def __eq__(self, other):
        return (
            self.amount == other.amount
            and self.script_pubkey == other.script_pubkey
            and self.script_pubkey_len == other.script_pubkey_len
        )

    def __repr__(self):
        return 'TxOut({}, {}, {})'.format(repr(self.amount), repr(self.script_pubkey), repr(self.script_pubkey_len))

    def __bytes__(self):
        return b''.join([self.amount, self.script_pubkey_len, self.script_pubkey])


class TxObj:
    __slots__ = ('version', 'TxIn', 'TxOut', 'locktime')

    def __init__(self, version, TxIn, TxOut, locktime):
        segwit_tx = any([i.segwit_input or i.witness for i in TxIn])
        self.version = version
        self.TxIn = TxIn
        if segwit_tx:
            for i in self.TxIn:
                i.witness = i.witness if i.witness else b'\x00'
        self.TxOut = TxOut
        self.locktime = locktime

    def __eq__(self, other):
        return (
            self.version == other.version
            and self.TxIn == other.TxIn
            and self.TxOut == other.TxOut
            and self.locktime == other.locktime
        )

    def __repr__(self):
        return 'TxObj({}, {}, {}, {})'.format(
            repr(self.version), repr(self.TxIn), repr(self.TxOut), repr(self.locktime)
        )

    def __bytes__(self):
        inp = int_to_varint(len(self.TxIn)) + b''.join(map(bytes, self.TxIn))
        out = int_to_varint(len(self.TxOut)) + b''.join(map(bytes, self.TxOut))
        wit = b''.join([w.witness for w in self.TxIn])
        return b''.join([self.version, MARKER if wit else b'', FLAG if wit else b'', inp, out, wit, self.locktime])

    def legacy_repr(self):
        inp = int_to_varint(len(self.TxIn)) + b''.join(map(bytes, self.TxIn))
        out = int_to_varint(len(self.TxOut)) + b''.join(map(bytes, self.TxOut))
        return b''.join([self.version, inp, out, self.locktime])

    def to_hex(self):
        return bytes_to_hex(bytes(self))

    @classmethod
    def is_segwit(cls, tx):
        if isinstance(tx, cls):
            tx = bytes(tx)
        elif not isinstance(tx, bytes):
            tx = hex_to_bytes(tx)
        return tx[4:6] == MARKER + FLAG


def calc_txid(tx_hex):
    tx_obj = deserialize(tx_hex)
    return bytes_to_hex(double_sha256(tx_obj.legacy_repr())[::-1])


def estimate_tx_fee(in_size, n_in, out_size, n_out, satoshis, segwit=False):

    if not satoshis:
        return 0

    estimated_size = math.ceil(
        in_size
        + len(int_to_unknown_bytes(n_in, byteorder='little'))
        + out_size
        + len(int_to_unknown_bytes(n_out, byteorder='little'))
        + 8
        # Accounting for magic header vBytes ('0001') 
        + (0.5 if segwit else 0)
    )

    estimated_fee = estimated_size * satoshis

    logging.debug('Estimated fee: {} satoshis for {} bytes'.format(estimated_fee, estimated_size))

    return estimated_fee


def select_coins(target, fee, output_size, min_change, *, absolute_fee=False, consolidate=False, unspents):
    '''
    Implementation of Branch-and-Bound coin selection defined in Erhart's
    Master's thesis An Evaluation of Coin Selection Strategies here:
    http://murch.one/wp-content/uploads/2016/11/erhardt2016coinselection.pdf

    :param target: The total amount of the outputs in a transaction for which
                   we try to select the inputs to spend.
    :type target: ``int``
    :param fee: The number of satoshi per byte for the fee of the transaction.
    :type fee: ``int``
    :param output_size: A list containing as int the sizes of each output.
    :type output_size: ``list`` of ``int`
    :param min_change: The minimum amount of satoshis allowed for the
                       return/change address if there is no perfect match.
    :type min_change: ``int``
    :param absolute_fee: Whether or not the parameter ``fee`` should be
                         repurposed to denote the exact fee amount.
    :type absolute_fee: ``bool``
    :param consolidate: Whether or not the Branch-and-Bound process for finding
                        a perfect match should be skipped and all unspents
                        used directly.
    :type consolidate: ``bool``
    :param unspents: The UTXOs to use as inputs.
    :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
    :raises InsufficientFunds: If ``unspents`` does not contain enough balance
                               to allow spending matching the target.
    '''

    # The maximum number of tries for Branch-and-Bound:
    BNB_TRIES = 1000000

    # COST_OF_OVERHEAD excludes the return address of output_size (last element).
    COST_OF_OVERHEAD = (8 + sum(output_size[:-1]) + 1) * fee

    def branch_and_bound(d, selected_coins, effective_value, target, fee, sorted_unspents):  # pragma: no cover

        nonlocal COST_OF_OVERHEAD, BNB_TRIES
        BNB_TRIES -= 1
        COST_PER_INPUT = 148 * fee  # Just typical estimate values
        COST_PER_OUTPUT = 34 * fee

        # The target we want to match includes cost of overhead for transaction
        target_to_match = target + COST_OF_OVERHEAD
        # Allowing to pay fee for a whole input and output is rationally
        # correct, but increases the fee-rate dramatically for only few inputs.
        match_range = COST_PER_INPUT + COST_PER_OUTPUT
        # We could allow to spend up to X% more on the fees if we can find a
        # perfect match:
        # match_range += int(0.1 * fee * sum(u.vsize for u in selected_coins))

        # Check for solution and cut criteria:
        if effective_value > target_to_match + match_range:
            return []
        elif effective_value >= target_to_match:
            return selected_coins
        elif BNB_TRIES <= 0:
            return []
        elif d >= len(sorted_unspents):
            return []
        else:
            # Randomly explore next branch:
            binary_random = randint(0, 1)
            if binary_random:
                # Explore inclusion branch first, else omission branch:
                effective_value_new = effective_value + sorted_unspents[d].amount - fee * sorted_unspents[d].vsize

                with_this = branch_and_bound(
                    d + 1, selected_coins + [sorted_unspents[d]], effective_value_new, target, fee, sorted_unspents
                )

                if with_this != []:
                    return with_this
                else:
                    without_this = branch_and_bound(
                        d + 1, selected_coins, effective_value, target, fee, sorted_unspents
                    )

                    return without_this

            else:
                # As above but explore omission branch first:
                without_this = branch_and_bound(d + 1, selected_coins, effective_value, target, fee, sorted_unspents)

                if without_this != []:
                    return without_this
                else:
                    effective_value_new = effective_value + sorted_unspents[d].amount - fee * sorted_unspents[d].vsize

                    with_this = branch_and_bound(
                        d + 1, selected_coins + [sorted_unspents[d]], effective_value_new, target, fee, sorted_unspents
                    )

                    return with_this

    sorted_unspents = sorted(unspents, key=lambda u: u.amount, reverse=True)
    selected_coins = []

    if not consolidate and not absolute_fee:
        # Trying to find a perfect match using Branch-and-Bound:
        selected_coins = branch_and_bound(
            d=0, selected_coins=[], effective_value=0, target=target, fee=fee, sorted_unspents=sorted_unspents
        )
        remaining = 0

    # Fallback: If no match, Single Random Draw with return address:
    if selected_coins == []:
        unspents = unspents.copy()
        # Since we have no information on the user's spending habit it is
        # best practice to randomly select UTXOs until we have enough.
        if not consolidate:
            # To have a deterministic way of inserting inputs when
            # consolidating, we only shuffle the unspents otherwise.
            shuffle(unspents)
        while unspents:
            selected_coins.append(unspents.pop(0))
            estimated_fee = estimate_tx_fee(
                sum(u.vsize for u in selected_coins), len(selected_coins), sum(output_size), len(output_size), fee, any(u.segwit for u in selected_coins)
            )
            estimated_fee = fee if absolute_fee else estimated_fee
            remaining = sum(u.amount for u in selected_coins) - target - estimated_fee
            if remaining >= min_change and (not consolidate or len(unspents) == 0):
                break
        else:
            raise InsufficientFunds(
                'Balance {} is less than {} (including '
                'fee).'.format(sum(u.amount for u in selected_coins), target + min_change + estimated_fee)
            )

    return selected_coins, remaining


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


def sanitize_tx_data(
    unspents,
    outputs,
    fee,
    leftover,
    combine=True,
    message=None,
    compressed=True,
    absolute_fee=False,
    min_change=0,
    version='main',
    message_is_hex=False,
    replace_by_fee=False
):
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
        if message_is_hex:
            message_chunks = chunk_data(message, MESSAGE_LIMIT)
        else:
            message_chunks = chunk_data(message.encode('utf-8'), MESSAGE_LIMIT)

        for message in message_chunks:
            messages.append((message, 0))

    # Include return address in output count.
    # Calculate output size as a list (including return address).
    output_size = [len(address_to_scriptpubkey(o[0])) + 9 for o in outputs]
    output_size.append(len(messages) * (MESSAGE_LIMIT + 9))
    output_size.append(len(address_to_scriptpubkey(leftover)) + 9)
    sum_outputs = sum(out[1] for out in outputs)

    # Use Branch-and-Bound for coin selection:
    unspents[:], remaining = select_coins(
        sum_outputs,
        fee,
        output_size,
        min_change=min_change,
        absolute_fee=absolute_fee,
        consolidate=combine,
        unspents=unspents,
    )

    if replace_by_fee:
        for unspent in unspents:
            unspent.opt_in_for_RBF()

    if remaining > 0:
        outputs.append((leftover, remaining))

    # Sanity check: If spending from main-/testnet, then all output addresses must also be for main-/testnet.
    for output in outputs:
        dest, amount = output
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
        return OP_DUP + OP_HASH160 + OP_PUSH_20 + address_to_public_key_hash(address) + OP_EQUALVERIFY + OP_CHECKSIG
    elif version == MAIN_SCRIPT_HASH or version == TEST_SCRIPT_HASH:
        return OP_HASH160 + OP_PUSH_20 + address_to_public_key_hash(address) + OP_EQUAL


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
            script_pubkey = OP_RETURN + len(dest).to_bytes(1, byteorder='little') + dest

            amount = b'\x00\x00\x00\x00\x00\x00\x00\x00'

        outputs_obj.append(TxOut(amount, script_pubkey))

    return outputs_obj


def calculate_preimages(tx_obj, inputs_parameters):
    """Calculates preimages for provided transaction structure and input
    values.

    :param tx_obj: The transaction object used to calculate preimage from using
                   a transaction digest algorithm, such as BIP-143 for Segwit
                   inputs. This transaction object must hence have scriptCodes
                   filled into the corresponding scriptSigs in the inputs.
    :type tx_obj: :object:`~bit.transaction.TxObj`
    :param inputs_parameters: A list of tuples with input index as integer,
                              hash type as integer and a boolean flag to denote
                              if the input is spending from a Segwit output.
                              For example: [(0, 1, True), (2, 1, False), (...)]
    :type inputs_parameters: A `list` of `tuple`
    """

    # Tx object data:
    input_count = int_to_varint(len(tx_obj.TxIn))
    output_count = int_to_varint(len(tx_obj.TxOut))
    output_block = b''.join([bytes(o) for o in tx_obj.TxOut])

    hashPrevouts = double_sha256(b''.join([i.txid + i.txindex for i in tx_obj.TxIn]))
    hashSequence = double_sha256(b''.join([i.sequence for i in tx_obj.TxIn]))
    hashOutputs = double_sha256(output_block)

    preimages = []
    for input_index, hash_type, segwit_input in inputs_parameters:
        # We can only handle hashType == 1:
        if hash_type != HASH_TYPE:
            raise ValueError('Bit only support hashType of value 1.')
        # Calculate prehashes:
        if segwit_input:
            # BIP-143 preimage:
            hashed = sha256(
                tx_obj.version
                + hashPrevouts
                + hashSequence
                + tx_obj.TxIn[input_index].txid
                + tx_obj.TxIn[input_index].txindex
                + tx_obj.TxIn[input_index].script_sig_len
                + tx_obj.TxIn[input_index].script_sig  # scriptCode length
                + tx_obj.TxIn[input_index].sequence  # scriptCode (includes amount)
                + hashOutputs
                + tx_obj.locktime
                + hash_type
            )
        else:
            hashed = sha256(
                tx_obj.version
                + input_count
                + b''.join(ti.txid + ti.txindex + OP_0 + ti.sequence for ti in islice(tx_obj.TxIn, input_index))
                + tx_obj.TxIn[input_index].txid
                + tx_obj.TxIn[input_index].txindex
                + tx_obj.TxIn[input_index].script_sig_len
                + tx_obj.TxIn[input_index].script_sig  # scriptCode length
                + tx_obj.TxIn[input_index].sequence  # scriptCode
                + b''.join(
                    ti.txid + ti.txindex + OP_0 + ti.sequence for ti in islice(tx_obj.TxIn, input_index + 1, None)
                )
                + output_count
                + output_block
                + tx_obj.locktime
                + hash_type
            )
        preimages.append(hashed)
    return preimages


def sign_tx(private_key, tx, *, unspents):
    """Signs inputs in provided transaction object for which unspents
    are provided and can be signed by the private key.

    :param private_key: Private key
    :type private_key: ``PrivateKey`` or ``MultiSig``
    :param tx: Transaction object
    :type tx: ``TxObj``
    :param unspents: For inputs to be signed their corresponding Unspent objects
                     must be provided.
    :type unspents: ``list`` of :class:`~bit.network.meta.Unspent`
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
        raise TypeError(
            'Please provide as unspents at least all inputs to be signed with the function call in a list.'
        )

    # Determine input indices to sign from input_dict (allows for transaction batching)
    sign_inputs = [j for j, i in enumerate(tx.TxIn) if i.txid + i.txindex in input_dict]

    segwit_tx = TxObj.is_segwit(tx)
    public_key = private_key.public_key
    public_key_push = script_push(len(public_key))
    hash_type = HASH_TYPE

    # Make input parameters for preimage calculation
    inputs_parameters = []

    # The TxObj in `tx` will below be modified to contain the scriptCodes used
    # for the transaction structure to be signed

    # `input_script_field` copies the scriptSigs for partially signed
    # transactions to later extract signatures from it:
    input_script_field = [tx.TxIn[i].script_sig for i in range(len(tx.TxIn))]

    for i in sign_inputs:
        # Create transaction object for preimage calculation
        tx_input = tx.TxIn[i].txid + tx.TxIn[i].txindex
        segwit_input = input_dict[tx_input]['segwit']
        tx.TxIn[i].segwit_input = segwit_input

        script_code = private_key.scriptcode
        script_code_len = int_to_varint(len(script_code))

        # Use scriptCode for preimage calculation of transaction object:
        tx.TxIn[i].script_sig = script_code
        tx.TxIn[i].script_sig_len = script_code_len

        if segwit_input:
            try:
                tx.TxIn[i].script_sig += input_dict[tx_input]['amount'].to_bytes(8, byteorder='little')

                # For partially signed Segwit transactions the signatures must
                # be extracted from the witnessScript field:
                input_script_field[i] = tx.TxIn[i].witness
            except AttributeError:
                raise ValueError(
                    'Cannot sign a segwit input when the input\'s amount is '
                    'unknown. Maybe no network connection or the input is '
                    'already spent? Then please provide all inputs to sign as '
                    '`Unspent` objects to the function call.'
                )

        inputs_parameters.append([i, hash_type, segwit_input])
    preimages = calculate_preimages(tx, inputs_parameters)

    # Calculate signature scripts:
    for hash, (i, _, segwit_input) in zip(preimages, inputs_parameters):
        signature = private_key.sign(hash) + b'\x01'

        # ------------------------------------------------------------------
        if private_key.instance == 'MultiSig' or private_key.instance == 'MultiSigTestnet':
            # P2(W)SH input

            script_blob = b''
            sigs = {}
            # Initial number of witness items (OP_0 + one signature + redeemscript).
            witness_count = 3
            if input_script_field[i]:
                sig_list = get_signatures_from_script(input_script_field[i])
                # Bitcoin Core convention: Every missing signature is denoted
                # by 0x00. Only used for already partially-signed scriptSigs:
                script_blob += b'\x00' * (private_key.m - len(sig_list) - 1)
                # Total number of witness items when partially or fully signed:
                witness_count = private_key.m + 2
                # For a partially signed input make a dictionary containing
                # all the provided signatures with public-keys as keys:
                for sig in sig_list:
                    for pub in private_key.public_keys:
                        if verify_sig(sig[:-1], hash, pub):
                            # If we already found a valid signature for pubkey
                            # we just overwrite it and don't care.
                            sigs[pub] = sig
                if len(sigs) >= private_key.m:
                    raise ValueError('Transaction is already signed with sufficiently needed signatures.')

            sigs[public_key] = signature

            witness = b''
            # Sort ingthe signatures according to the public-key list:
            for pub in private_key.public_keys:
                if pub in sigs:
                    sig = sigs[pub]
                    length = int_to_varint(len(sig)) if segwit_input else script_push(len(sig))
                    witness += length + sig

            script_sig = b'\x22' + private_key.segwit_scriptcode

            witness = (int_to_varint(witness_count) if segwit_input else b'') + b'\x00' + witness + script_blob
            witness += (
                int_to_varint(len(private_key.redeemscript))
                if segwit_input
                else script_push(len(private_key.redeemscript))
            ) + private_key.redeemscript

            script_sig = script_sig if segwit_input else witness
            witness = witness if segwit_input else b'\x00' if segwit_tx else b''

        # ------------------------------------------------------------------
        else:
            # P2(W)PKH input

            script_sig = b'\x16' + private_key.segwit_scriptcode

            witness = (
                (b'\x02' if segwit_input else b'')
                + len(signature).to_bytes(1, byteorder='little')  # witness counter
                + signature
                + public_key_push
                + public_key
            )

            script_sig = script_sig if segwit_input else witness
            witness = witness if segwit_input else b'\x00' if segwit_tx else b''

        # Providing the signature(s) to the input
        tx.TxIn[i].script_sig = script_sig
        tx.TxIn[i].script_sig_len = int_to_varint(len(script_sig))
        tx.TxIn[i].witness = witness

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
        amount = int(unspent.amount).to_bytes(8, byteorder='little')
        sequence = unspent.sequence.to_bytes(4, byteorder='little')
        inputs.append(TxIn(script_sig, txid, txindex, amount=amount, segwit_input=unspent.segwit,
                           sequence=sequence))

    tx_unsigned = TxObj(version, inputs, outputs, lock_time)

    tx = sign_tx(private_key, tx_unsigned, unspents=unspents)
    return tx
