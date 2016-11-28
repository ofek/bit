from collections import deque, namedtuple

from bit.base58 import b58decode_check
from bit.crypto import double_sha256, ECDSA_SHA256
from bit.format import BTC, point_to_public_key
from bit.utils import flip_hex_byte_order, int_to_unknown_bytes

VERSION_1 = 0x01.to_bytes(4, byteorder='little')
SEQUENCE = 0xffffffff.to_bytes(4, byteorder='little')
LOCK_TIME = 0x00.to_bytes(4, byteorder='little')
HASH_TYPE = 0x01.to_bytes(4, byteorder='little')
ZERO = b'\x00'


Output = namedtuple('Output', ('address', 'amount'))


class UTXO:
    __slots__ = ('amount', 'confirmations', 'script', 'txid', 'txindex')

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


TxIn = namedtuple('TxIn', ('txid', 'index', 'seq'))

#
# def construct_output_block(outputs):
#     output_block = b''
#
#     for data in outputs:
#         address, amount = data
#         script = b58decode_check(address)
#         amount *= BTC
#
#         output_block += amount.to_bytes(8, byteorder='little')
#         output_block += len(script).to_bytes(1, byteorder='little')
#         output_block += script
#
#     return output_block
#
#
# def construct_input_block(utxos):
#     input_block = b''
#
#     for utxo in utxos:
#         input_block += (
#             utxo.txid +
#             utxo.txindex +
#             utxo.script_len +
#             utxo.script +
#             SEQUENCE
#         )
#
#     return input_block
#
#
# def create_signed_transaction(private_key, utxos, outputs):
#     utxos = utxos.copy()
#     num_inputs = len(utxos)
#
#     version = VERSION_1
#     input_count = num_inputs.to_bytes(1, byteorder='little')
#     output_count = len(outputs).to_bytes(1, byteorder='little')
#     output_block = construct_output_block(outputs)
#     lock_time = LOCK_TIME
#     public_key = point_to_public_key(
#         private_key.public_key().public_numbers(), compressed=False
#     )
#     public_key_len = len(public_key).to_bytes(1, byteorder='little')
#
#     for utxo in utxos:
#         utxo.txid = bytes.fromhex(utxo.txid)[::-1]
#         utxo.txindex = utxo.txindex.to_bytes(4, byteorder='little')
#         utxo.script = bytes.fromhex(utxo.script)
#         utxo.script_len = len(utxo.script).to_bytes(1, byteorder='little')
#
#     inputs_signed = deque(maxlen=num_inputs)
#     inputs_unsigned = deque((
#         utxo.txid + utxo.txindex + ZERO + SEQUENCE for utxo in utxos
#     ), maxlen=num_inputs)
#
#     for utxo in utxos:
#         null_input = inputs_unsigned.popleft()
#
#         hashed = double_sha256(
#             version +
#             input_count +
#             b''.join(inputs_signed) +
#             utxo.txid +
#             utxo.txindex +
#             utxo.script_len +
#             utxo.script +
#             SEQUENCE +
#             b''.join(inputs_unsigned) +
#             output_count +
#             output_block +
#             lock_time +
#             HASH_TYPE
#         )
#
#         signature = private_key.sign(hashed, ECDSA_SHA256) + HASH_TYPE
#
#         script_sig = (
#             len(signature).to_bytes(1, byteorder='little') +
#             signature +
#             public_key_len +
#             public_key
#         )
#
#         utxo.script = script_sig
#         utxo.script_len = int_to_unknown_bytes(script_sig, byteorder='little')
#
#         inputs_signed.append(null_input)
#
#     return (
#         version +
#         input_count +
#         construct_input_block(utxos) +
#         output_count +
#         output_block +
#         lock_time
#     )
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
