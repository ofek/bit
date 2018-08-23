import pytest

from bit.exceptions import InsufficientFunds
from bit.network.meta import Unspent
from bit.transaction import (
    TxIn, TxOut, TxObj, calc_txid, create_new_transaction,
    construct_outputs, estimate_tx_fee, sanitize_tx_data
)
from bit.utils import hex_to_bytes
from bit.wallet import PrivateKey
from .samples import WALLET_FORMAT_MAIN, BITCOIN_ADDRESS, BITCOIN_ADDRESS_TEST


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
#        b'\x8a',
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
        txin = TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')
        assert txin.script_sig == b'script'
        assert txin.script_sig_len == b'\x06'
        assert txin.txid == b'txid'
        assert txin.txindex == b'\x04'
        assert txin.sequence == b'\xff\xff\xff\xff'

    def test_equality(self):
        txin1 = TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')
        txin2 = TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')
        txin3 = TxIn(b'script', b'txi', b'\x03', b'\xff\xff\xff\xff')
        assert txin1 == txin2
        assert txin1 != txin3

    def test_repr(self):
        txin = TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')

        assert repr(txin) == "TxIn(b'script', {}, b'txid', {}, {})" \
                             "".format(repr(b'\x06'), repr(b'\x04'), repr(b'\xff\xff\xff\xff'))

    def test_bytes_repr(self):
        txin = TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')

        assert bytes(txin) == b''.join([b'txid', b'\x04', b'\x06', b'script', b'\xff\xff\xff\xff'])


class TestTxOut:
    def test_init(self):
        txout = TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')
        assert txout.amount == b'\x88\x13\x00\x00\x00\x00\x00\x00'
        assert txout.script_pubkey_len == b'\r'
        assert txout.script_pubkey == b'script_pubkey'

    def test_equality(self):
        txout1 = TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')
        txout2 = TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')
        txout3 = TxOut(b'\x88\x14\x00\x00\x00\x00\x00\x00', b'script_pubkey')
        txout4 = TxOut(b'\x88\x14\x00\x00\x00\x00\x00\x00', b'script_pub')
        assert txout1 == txout2
        assert txout1 != txout3
        assert txout3 != txout4

    def test_repr(self):
        txout = TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')

        assert repr(txout) == "TxOut({}, b'script_pubkey', {})" \
                              "".format(repr(b'\x88\x13\x00\x00\x00\x00\x00\x00'), repr(b'\r'))

    def test_bytes_repr(self):
        txout = TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')

        assert bytes(txout) == b''.join([b'\x88\x13\x00\x00\x00\x00\x00\x00', b'\r', b'script_pubkey'])


class TestTxObj:
    def test_init(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')
        assert txobj.version == b'\x01\x00\x00\x00'
        assert txobj.TxIn == txin
        assert txobj.TxOut == txout
        assert txobj.locktime == b'\x00\x00\x00\x00'

    def test_equality(self):
        txin1 = [TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')]
        txin2 = [TxIn(b'scrip2', b'txid', b'\x04', b'\xff\xff\xff\xff')]
        txout1 = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txout2 = [TxOut(b'\x88\x14\x00\x00\x00\x00\x00\x00', b'script_pubkey')]

        txobj1 = TxObj(b'\x01\x00\x00\x00', txin1, txout1, b'\x00\x00\x00\x00')
        txobj2 = TxObj(b'\x01\x00\x00\x00', txin1, txout1, b'\x00\x00\x00\x00')
        txobj3 = TxObj(b'\x01\x00\x00\x00', txin1, txout2, b'\x00\x00\x00\x00')
        txobj4 = TxObj(b'\x01\x00\x00\x00', txin2, txout1, b'\x00\x00\x00\x00')
        txobj5 = TxObj(b'\x02\x00\x00\x00', txin1, txout1, b'\x00\x00\x00\x00')
        txobj6 = TxObj(b'\x01\x00\x00\x00', txin1, txout1, b'\x01\x00\x00\x00')

        assert txobj1 == txobj2
        assert txobj1 != txobj3
        assert txobj1 != txobj4
        assert txobj1 != txobj5
        assert txobj1 != txobj6

    def test_repr(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        assert repr(txobj) == "TxObj({}, {}, {}, {})" \
                              "".format(repr(b'\x01\x00\x00\x00'),
                                        repr(txin),
                                        repr(txout),
                                        repr(b'\x00\x00\x00\x00'))

    def test_bytes_repr(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        assert bytes(txobj) == b''.join([b'\x01\x00\x00\x00',
                                         b'\x01txid\x04\x06script\xff\xff\xff\xff',
                                         b'\x01\x88\x13\x00\x00\x00\x00\x00\x00\rscript_pubkey',
                                         b'\x00\x00\x00\x00'])


class TestSanitizeTxData:
    def test_no_input(self):
        with pytest.raises(ValueError):
            sanitize_tx_data([], [], 70, '')

    def test_message(self):
        unspents_original = [Unspent(10000, 0, '', '', 0),
                             Unspent(10000, 0, '', '', 0)]
        outputs_original = [(BITCOIN_ADDRESS_TEST, 1000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=5, leftover=RETURN_ADDRESS,
            combine=True, message='hello', version='test'
        )

        assert len(outputs) == 3
        assert outputs[2][0] == b'hello'
        assert outputs[2][1] == 0

    def test_fee_applied(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [(BITCOIN_ADDRESS, 2000, 'satoshi')]

        with pytest.raises(InsufficientFunds):
            sanitize_tx_data(
                unspents_original, outputs_original, fee=1, leftover=RETURN_ADDRESS,
                combine=True, message=None
            )

    def test_zero_remaining(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [(BITCOIN_ADDRESS_TEST, 2000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=True, message=None, version='test'
        )

        assert unspents == unspents_original
        assert outputs == [(BITCOIN_ADDRESS_TEST, 2000)]

    def test_combine_remaining(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [(BITCOIN_ADDRESS_TEST, 500, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=True, message=None, version='test'
        )

        assert unspents == unspents_original
        assert len(outputs) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == 1500

    def test_combine_insufficient_funds(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [(BITCOIN_ADDRESS_TEST, 2500, 'satoshi')]

        with pytest.raises(InsufficientFunds):
            sanitize_tx_data(
                unspents_original, outputs_original, fee=50, leftover=RETURN_ADDRESS,
                combine=True, message=None, version='test'
            )

    def test_no_combine_remaining(self):
        unspents_original = [Unspent(7000, 0, '', '', 0),
                             Unspent(3000, 0, '', '', 0)]
        outputs_original = [(BITCOIN_ADDRESS_TEST, 2000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=False, message=None, version='test'
        )

        assert unspents == [Unspent(3000, 0, '', '', 0)]
        assert len(outputs) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == 1000

    def test_no_combine_remaining_small_inputs(self):
        unspents_original = [Unspent(1500, 0, '', '', 0),
                             Unspent(1600, 0, '', '', 0),
                             Unspent(1700, 0, '', '', 0)]
        outputs_original = [(RETURN_ADDRESS, 2000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=0, leftover=RETURN_ADDRESS,
            combine=False, message=None, version='test'
        )
        assert unspents == [Unspent(1500, 0, '', '', 0), Unspent(1600, 0, '', '', 0)]
        assert len(outputs) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == 1100

    def test_no_combine_with_fee(self):
        """
        Verify that unused unspents do not increase fee.
        """
        unspents_single = [Unspent(5000, 0, '', '', 0)]
        unspents_original = [Unspent(5000, 0, '', '', 0),
                             Unspent(5000, 0, '', '', 0)]
        outputs_original = [(RETURN_ADDRESS, 1000, 'satoshi')]

        unspents, outputs = sanitize_tx_data(
            unspents_original, outputs_original, fee=1, leftover=RETURN_ADDRESS,
            combine=False, message=None, version='test'
        )

        unspents_single, outputs_single = sanitize_tx_data(
            unspents_single, outputs_original, fee=1, leftover=RETURN_ADDRESS,
            combine=False, message=None, version='test'
        )

        assert unspents == [Unspent(5000, 0, '', '', 0)]
        assert unspents_single == [Unspent(5000, 0, '', '', 0)]
        assert len(outputs) == 2
        assert len(outputs_single) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs_single[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == outputs_single[1][1]

    def test_no_combine_insufficient_funds(self):
        unspents_original = [Unspent(1000, 0, '', '', 0),
                             Unspent(1000, 0, '', '', 0)]
        outputs_original = [('test', 2500, 'satoshi')]

        with pytest.raises(InsufficientFunds):
            sanitize_tx_data(
                unspents_original, outputs_original, fee=50, leftover=RETURN_ADDRESS,
                combine=False, message=None
            )

    def test_no_combine_mainnet_with_testnet(self):
        unspents = [Unspent(20000, 0, '', '', 0)]
        outputs = [(BITCOIN_ADDRESS, 500, 'satoshi'),
                   (BITCOIN_ADDRESS_TEST, 500, 'satoshi')]

        with pytest.raises(ValueError):
            sanitize_tx_data(
                unspents, outputs, fee=50, leftover=RETURN_ADDRESS,  # leftover is a testnet-address
                combine=False, message=None, version='main'
            )

        with pytest.raises(ValueError):
            sanitize_tx_data(
                unspents, outputs, fee=50, leftover=BITCOIN_ADDRESS,  # leftover is a mainnet-address
                combine=False, message=None, version='main'
            )


class TestCreateSignedTransaction:
    def test_matching(self):
        private_key = PrivateKey(WALLET_FORMAT_MAIN)
        tx = create_new_transaction(private_key, UNSPENTS, OUTPUTS)
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
        outs = construct_outputs(OUTPUTS)
        assert outs[0].amount == hex_to_bytes(OUTPUT_BLOCK[:16])
        assert outs[0].script_pubkey == hex_to_bytes(OUTPUT_BLOCK[18:68])
        assert outs[1].amount == hex_to_bytes(OUTPUT_BLOCK[68:84])
        assert outs[1].script_pubkey == hex_to_bytes(OUTPUT_BLOCK[86:])

    def test_message(self):
        outs = construct_outputs(OUTPUTS + MESSAGES)
        assert outs[2].amount == hex_to_bytes(OUTPUT_BLOCK_MESSAGES[136:152])
        assert outs[2].script_pubkey == hex_to_bytes(OUTPUT_BLOCK_MESSAGES[154:168])
        assert outs[3].amount == hex_to_bytes(OUTPUT_BLOCK_MESSAGES[168:184])
        assert outs[3].script_pubkey == hex_to_bytes(OUTPUT_BLOCK_MESSAGES[186:])

    def test_long_message(self):
        amount = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        _, outputs = sanitize_tx_data(
            UNSPENTS, [(out[0], out[1], 'satoshi') for out in OUTPUTS], 0, RETURN_ADDRESS,
            message='hello'*9, version='test'
        )
        outs = construct_outputs(outputs)
        assert len(outs) == 5 and outs[3].amount == amount and outs[4].amount == amount


def test_calc_txid():
    assert calc_txid(FINAL_TX_1) == 'e6922a6e3f1ff422113f15543fbe1340a727441202f55519640a70ac4636c16f'
