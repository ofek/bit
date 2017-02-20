import pytest

from bit.exceptions import InsufficientFunds
from bit.network.meta import Unspent
from bit.transaction import (
    TxIn, calc_txid, create_p2pkh_transaction, construct_input_block,
    construct_output_block, estimate_tx_fee, sanitize_tx_data
)
from bit.utils import hex_to_bytes
from bit.wallet import PrivateKey
from .samples import WALLET_FORMAT_MAIN


RETURN_ADDRESS = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'

FINAL_TX_1 = ('01000000018878399d83ec25c627cfbf753ff9ca3602373eac437ab2676154a3c2'
              'da23adf3010000008a473044022068b8dce776ef1c071f4c516836cdfb358e44ef'
              '58e0bf29d6776ebdc4a6b719df02204ea4a9b0f4e6afa4c229a3f11108ff66b178'
              '95015afa0c26c4bbc2b3ba1a1cc60141043d5c2875c9bd116875a71a5db64cffcb'
              '13396b163d039b1d932782489180433476a4352a2add00ebb0d5c94c515b72eb10'
              'f1fd8f3f03b42f4a2b255bfc9aa9e3ffffffff0250c30000000000001976a914e7'
              'c1345fc8f87c68170b3aa798a956c2fe6a9eff88ac0888fc04000000001976a914'
              '92461bde6283b461ece7ddf4dbf1e0a48bd113d888ac00000000')
INPUTS = [
    TxIn(
        (b"G0D\x02 E\xb7C\xdb\xaa\xaa,\xd1\xef\x0b\x914oVD\xe3-\xc7\x0c\xde\x05\t"
         b"\x1b7b\xd4\xca\xbbn\xbdq\x1a\x02 tF\x10V\xc2n\xfe\xac\x0bD\x8e\x7f\xa7"
         b"iw=\xd6\xe4Cl\xdeP\\\x8fl\xa60>\xfe1\xf0\x95\x01A\x04=\\(u\xc9\xbd\x11"
         b"hu\xa7\x1a]\xb6L\xff\xcb\x139k\x16=\x03\x9b\x1d\x93'\x82H\x91\x80C4v"
         b"\xa45**\xdd\x00\xeb\xb0\xd5\xc9LQ[r\xeb\x10\xf1\xfd\x8f?\x03\xb4/J+%["
         b"\xfc\x9a\xa9\xe3"),
        b'\x8a',
        (b"\x88x9\x9d\x83\xec%\xc6'\xcf\xbfu?\xf9\xca6\x027>"
         b"\xacCz\xb2gaT\xa3\xc2\xda#\xad\xf3"),
        b'\x01\x00\x00\x00'
    )
]
INPUT_BLOCK = ('8878399d83ec25c627cfbf753ff9ca3602373eac437ab2676154a3c2da23adf30'
               '10000008a473044022045b743dbaaaa2cd1ef0b91346f5644e32dc70cde05091b'
               '3762d4cabb6ebd711a022074461056c26efeac0b448e7fa769773dd6e4436cde5'
               '05c8f6ca6303efe31f0950141043d5c2875c9bd116875a71a5db64cffcb13396b'
               '163d039b1d932782489180433476a4352a2add00ebb0d5c94c515b72eb10f1fd8'
               'f3f03b42f4a2b255bfc9aa9e3ffffffff')
UNSPENTS = [
    Unspent(83727960,
            15,
            '76a91492461bde6283b461ece7ddf4dbf1e0a48bd113d888ac',
            'f3ad23dac2a3546167b27a43ac3e370236caf93f75bfcf27c625ec839d397888',
            1)
]
OUTPUTS = [
    ('n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi', 50000),
    ('mtrNwJxS1VyHYn3qBY1Qfsm3K3kh1mGRMS', 83658760)
]
MESSAGES = [
    (b'hello', 0),
    (b'there', 0)
]
OUTPUT_BLOCK = ('50c30000000000001976a914e7c1345fc8f87c68170b3aa798a956c2fe6a9eff88ac'
                '0888fc04000000001976a91492461bde6283b461ece7ddf4dbf1e0a48bd113d888ac')
OUTPUT_BLOCK_MESSAGES = ('50c30000000000001976a914e7c1345fc8f87c68170b3aa798a956c2fe6a9eff88ac'
                         '0888fc04000000001976a91492461bde6283b461ece7ddf4dbf1e0a48bd113d888ac'
                         '0000000000000000076a0568656c6c6f'
                         '0000000000000000076a057468657265')
SIGNED_DATA = (b'\x85\xc7\xf6\xc6\x80\x13\xc2g\xd3t\x8e\xb8\xb4\x1f\xcc'
               b'\x92x~\n\x1a\xac\xc0\xf0\xff\xf7\xda\xfe0\xb7!6t')


class TestTxIn:
    def test_init(self):
        txin = TxIn(b'script', b'\x06', b'txid', b'\x04')
        assert txin.script == b'script'
        assert txin.script_len == b'\x06'
        assert txin.txid == b'txid'
        assert txin.txindex == b'\x04'

    def test_equality(self):
        txin1 = TxIn(b'script', b'\x06', b'txid', b'\x04')
        txin2 = TxIn(b'script', b'\x06', b'txid', b'\x04')
        txin3 = TxIn(b'script', b'\x06', b'txi', b'\x03')
        assert txin1 == txin2
        assert txin1 != txin3

    def test_repr(self):
        txin = TxIn(b'script', b'\x06', b'txid', b'\x04')

        assert repr(txin) == "TxIn(b'script', {}, b'txid', {})" \
                             "".format(repr(b'\x06'), repr(b'\x04'))


class TestSanitizeTxData:
    def test_no_input(self):
        with pytest.raises(ValueError):
            sanitize_tx_data([], [], 70, '')

    def test_message(self):
        unspents_original = [Unspent(10000, 0, '', '', 0),
                             Unspent(10000, 0, '', '', 0)]
        outputs_original = [('test', 1000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=5, leftover=RETURN_ADDRESS,
            combine=True, message='hello'
        )

        assert len(outputs) == 3
        assert outputs[2][0] == b'hello'
        assert outputs[2][1] == 0

    def test_fee_applied(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [('test', 2000, 'satoshi')]

        with pytest.raises(InsufficientFunds):
            sanitize_tx_data(
                unspents_original, outputs_original, fee=1, leftover=RETURN_ADDRESS,
                combine=True, message=None
            )

    def test_zero_remaining(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [('test', 2000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=True, message=None
        )

        assert unspents == unspents_original
        assert outputs == [('test', 2000)]

    def test_combine_remaining(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [('test', 500, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=True, message=None
        )

        assert unspents == unspents_original
        assert len(outputs) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == 1500

    def test_combine_insufficient_funds(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [('test', 2500, 'satoshi')]

        with pytest.raises(InsufficientFunds):
            sanitize_tx_data(
                unspents_original, outputs_original, fee=50, leftover=RETURN_ADDRESS,
                combine=True, message=None
            )

    def test_no_combine_remaining(self):
        unspents_original = [Unspent(7000, 0, '', '', 0),
                             Unspent(3000, 0, '', '', 0)]
        outputs_original = [('test', 2000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=False, message=None
        )

        assert unspents == [Unspent(3000, 0, '', '', 0)]
        assert len(outputs) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == 1000

    def test_no_combine_insufficient_funds(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [('test', 2500, 'satoshi')]

        with pytest.raises(InsufficientFunds):
            sanitize_tx_data(
                unspents_original, outputs_original, fee=50, leftover=RETURN_ADDRESS,
                combine=False, message=None
            )


class TestCreateSignedTransaction:
    def test_matching(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        tx = create_p2pkh_transaction(private_key, UNSPENTS, OUTPUTS)
        assert tx[-288:] == FINAL_TX_1[-288:]


class TestEstimateTxFee:
    def test_accurate_compressed(self):
        assert estimate_tx_fee(1, 2, 70, True) == 15820

    def test_accurate_uncompressed(self):
        assert estimate_tx_fee(1, 2, 70, False) == 18060

    def test_none(self):
        assert estimate_tx_fee(5, 5, 0, True) == 0


class TestConstructOutputBlock:
    def test_no_message(self):
        assert construct_output_block(OUTPUTS) == hex_to_bytes(OUTPUT_BLOCK)

    def test_message(self):
        assert construct_output_block(OUTPUTS + MESSAGES) == hex_to_bytes(OUTPUT_BLOCK_MESSAGES)

    def test_long_message(self):
        amount = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        _, outputs = sanitize_tx_data(
            UNSPENTS, [(out[0], out[1], 'satoshi') for out in OUTPUTS], 0, RETURN_ADDRESS, message='hello'*9
        )
        assert construct_output_block(outputs).count(amount) == 2


def test_construct_input_block():
    assert construct_input_block(INPUTS) == hex_to_bytes(INPUT_BLOCK)


def test_calc_txid():
    assert calc_txid(FINAL_TX_1) == 'e6922a6e3f1ff422113f15543fbe1340a727441202f55519640a70ac4636c16f'
