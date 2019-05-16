import pytest
import copy

from bit.constants import HASH_TYPE
from bit.exceptions import InsufficientFunds
from bit.network.meta import Unspent
from bit.transaction import (
    TxIn, TxOut, TxObj, calc_txid, create_new_transaction,
    construct_outputs, deserialize, estimate_tx_fee, sanitize_tx_data,
    select_coins, address_to_scriptpubkey, calculate_preimages, sign_tx
)
from bit.utils import hex_to_bytes, get_signatures_from_script
from bit.wallet import PrivateKey, PrivateKeyTestnet, MultiSigTestnet, MultiSig
from .samples import (
    WALLET_FORMAT_MAIN, WALLET_FORMAT_TEST_1,
    WALLET_FORMAT_TEST_2, BITCOIN_ADDRESS, BITCOIN_ADDRESS_TEST,
    BITCOIN_ADDRESS_PAY2SH, BITCOIN_ADDRESS_TEST_PAY2SH,
    BITCOIN_SEGWIT_ADDRESS, BITCOIN_SEGWIT_ADDRESS_PAY2SH,
    BITCOIN_SEGWIT_HASH, BITCOIN_SEGWIT_HASH_PAY2SH, BITCOIN_SEGWIT_ADDRESS_TEST,
    BITCOIN_SEGWIT_ADDRESS_TEST_PAY2SH, BITCOIN_SEGWIT_HASH_TEST,
    BITCOIN_SEGWIT_HASH_TEST_PAY2SH, PAY2SH_HASH, PAY2SH_TEST_HASH,
    BITCOIN_ADDRESS_COMPRESSED, BITCOIN_ADDRESS_TEST_COMPRESSED
)


RETURN_ADDRESS = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
RETURN_ADDRESS_MAIN = '1ELReFsTCUY2mfaDTy32qxYiT49z786eFg'

FINAL_TX_1 = ('01000000018878399d83ec25c627cfbf753ff9ca3602373eac437ab2676154a3c2'
              'da23adf3010000008a473044022068b8dce776ef1c071f4c516836cdfb358e44ef'
              '58e0bf29d6776ebdc4a6b719df02204ea4a9b0f4e6afa4c229a3f11108ff66b178'
              '95015afa0c26c4bbc2b3ba1a1cc60141043d5c2875c9bd116875a71a5db64cffcb'
              '13396b163d039b1d932782489180433476a4352a2add00ebb0d5c94c515b72eb10'
              'f1fd8f3f03b42f4a2b255bfc9aa9e3ffffffff0250c30000000000001976a914e7'
              'c1345fc8f87c68170b3aa798a956c2fe6a9eff88ac0888fc04000000001976a914'
              '92461bde6283b461ece7ddf4dbf1e0a48bd113d888ac00000000')

SEGWIT_TX_1 = ('010000000001021f9c125fc1c14ef7f4b03b4b7dad7be4c3b054d7c266689a456a'
               'daffd6ec7a31010000006a47304402201cfc264e99287d17fd19a9d8d82746b97e'
               '80a2e94e5bbe3ef73a44a3df2399e702207152926699eb4555a88a3243c6640627'
               '6e9aba808c24049e7dedba27b057b1b00121021816325d19fd34fd87a039e83e35'
               'fc9de3c9de64a501a6684b9bf9946364fbb7ffffffff6e6d2db49c4bf5bb97e888'
               '30058a58eb1c4d092e980b2bb663c81632f5dd8b0b0100000017160014175e9f8b'
               '21d4f2f76a7360458f90717e08fbcdb6ffffffff0280f0fa02000000001600140e'
               'e268c86d05f290add1bfc9bdfc3992d785bce2e84ef5050000000017a9146a45a0'
               '3574460e17a1d75d9535d90bad20d8d79b870002473044022033a25adc3230a0b9'
               '3028520b2bd089e26ce366bcf22064d41f6c5a3c200d956302201f45ef76dde3fc'
               '27f741f9fc93e6280dac991c364ee578eafb3348db662339000121037d69688686'
               '4509ed63044d8f1bcd53b8def1247bd2bbe056ff81b23e8c09280f00000000')

UNSIGNED_TX_SEGWIT = (
    '0100000000010288d3b28dbb7d24dd4ff292534dec44bdb9eca73c3c9577e4d7fc70777122'
    '9cf00000000000ffffffffcbd4b41660d8d348c15fc430deb5fd55d62cb756b36d1c5b9f3c'
    '5af9e14e2cf40000000000ffffffff0280f0fa020000000017a914ea654a94b18eb41ce290'
    'c135cccf9f348e7856a28770aaf0080000000017a9146015d175e191e6e5b99211e3ffc6ea'
    '7658cb051a87000000000000'
)

FINAL_TX_SEGWIT = ('0100000000010288d3b28dbb7d24dd4ff292534dec44bdb9eca73c3c95'
                   '77e4d7fc707771229cf0000000006b4830450221008dd5c2feb30d40dd'
                   '621afef413d3abc285d39aa0716233d7ccbc56a50678ebc4022005be97'
                   'c4e432d373885b20ae822c432f96f78ad290a191f060730997ade095b0'
                   '0121021816325d19fd34fd87a039e83e35fc9de3c9de64a501a6684b9b'
                   'f9946364fbb7ffffffffcbd4b41660d8d348c15fc430deb5fd55d62cb7'
                   '56b36d1c5b9f3c5af9e14e2cf40000000017160014905aa72f3d174709'
                   '4a24d3adbc38905bb451ffc8ffffffff0280f0fa020000000017a914ea'
                   '654a94b18eb41ce290c135cccf9f348e7856a28770aaf0080000000017'
                   'a9146015d175e191e6e5b99211e3ffc6ea7658cb051a87000247304402'
                   '2073604374fdbd121d8cf4facb19a553630d145e1a1405d8144d2c0cca'
                   '77da30ba022004a47a760b6bc68e99b88c1febfd8620d6bfd4f609b83e'
                   'e1c39f77f4689f69a20121021816325d19fd34fd87a039e83e35fc9de3'
                   'c9de64a501a6684b9bf9946364fbb700000000')

UNSIGNED_TX_BATCH = (
    '010000000001024623e78d68e72b428eb4f53f73086ad824a2c2b6be906e3113ab2afc4944'
    '06640000000000ffffffffe2ded7092c8087f18343b716586ea047c060a36952a308fabf75'
    '65133907af370100000000ffffffff0200286bee000000001600140ee268c86d05f290add1'
    'bfc9bdfc3992d785bce2505c9a3b0000000017a914d35515db546bb040e61651150343a218'
    'c87b471e87000000000000'
)

FINAL_TX_BATCH = ('010000000001024623e78d68e72b428eb4f53f73086ad824a2c2b6be90'
                  '6e3113ab2afc494406640000000023220020d3a4db6921782f78eb4f15'
                  '8f73adde471629dd5aca41c14a5bfc2ec2a8f39202ffffffffe2ded709'
                  '2c8087f18343b716586ea047c060a36952a308fabf7565133907af3701'
                  '00000017160014905aa72f3d1747094a24d3adbc38905bb451ffc8ffff'
                  'ffff0200286bee000000001600140ee268c86d05f290add1bfc9bdfc39'
                  '92d785bce2505c9a3b0000000017a914d35515db546bb040e616511503'
                  '43a218c87b471e870400473044022037e201de1f63d3f3f54bcea95a2c'
                  'afb06efd77472219dab80ed5ccf6eaf0e63902205693fa791957ca0c7f'
                  '40599913e03dd6a0cd9bb73d8dbdda7cd1c17ae5badd9f014730440220'
                  '2f4dd12673ea33fb9e7e771f59dba4d7b4a3d820bac9633ea24cdb0241'
                  '2f225002205ae28fefa3a2e9255faf17375aca5d1fe51fedf0b4dd3315'
                  '2f64df1f7f53c42501475221021816325d19fd34fd87a039e83e35fc9d'
                  'e3c9de64a501a6684b9bf9946364fbb721037d696886864509ed63044d'
                  '8f1bcd53b8def1247bd2bbe056ff81b23e8c09280f52ae024830450221'
                  '0082e63d77985503a42307cd650a0a78630eb6edd84fefada23721ec54'
                  '3614c53e0220407313344a20be5c7dfbb418d87bbd33916fe24ba5f38c'
                  '2cba96d3499410bbd90121021816325d19fd34fd87a039e83e35fc9de3'
                  'c9de64a501a6684b9bf9946364fbb700000000')

FINAL_TX_MULTISIG_MANY = (
    '010000000001040100000000000000000000000000000000000000000000000000000000'
    '0000000000000023220020d3a4db6921782f78eb4f158f73adde471629dd5aca41c14a5b'
    'fc2ec2a8f39202ffffffff02000000000000000000000000000000000000000000000000'
    '0000000000000001000000db00483045022100a9efd4418fc75749407ab9369c21a52f9e'
    '105f0dac25e8e7020f16fd0738185f0220421930e517fe2cd015a9f1e0c884f07ca0b80f'
    '0153cf413dfd926abfeb5bf81201483045022100afc30dd8dc8fc7d006458034bbd3f425'
    '4cd5783d56ef6568fb21d074f44fa3ad02200e7b1207113c59525eb7376a7bc5fea42405'
    '1152687e406fd90a435467f8b8db01475221021816325d19fd34fd87a039e83e35fc9de3'
    'c9de64a501a6684b9bf9946364fbb721037d696886864509ed63044d8f1bcd53b8def124'
    '7bd2bbe056ff81b23e8c09280f52aeffffffff0300000000000000000000000000000000'
    '0000000000000000000000000000000200000023220020d3a4db6921782f78eb4f158f73'
    'adde471629dd5aca41c14a5bfc2ec2a8f39202ffffffff04000000000000000000000000'
    '0000000000000000000000000000000000000003000000db00483045022100a324e5256d'
    'c2621e4b185112ea80d95d170b6cd13dcf7a096e5a82cd85e94bad02200e9859d4b7af52'
    '0eaab1bbcee6d25ad1e2dee1c9f428794a40fa8bcff82395c601483045022100ea77d456'
    '5fd49b113df45507ebb2f1ee101d65798ecbf9a98f99212cb05d776a02207bc44b0e1f62'
    '6c9072a6524f1459f9bc9965f75b863c705c8f6a07646ae4e9d901475221021816325d19'
    'fd34fd87a039e83e35fc9de3c9de64a501a6684b9bf9946364fbb721037d696886864509'
    'ed63044d8f1bcd53b8def1247bd2bbe056ff81b23e8c09280f52aeffffffff0200286bee'
    '000000001600140ee268c86d05f290add1bfc9bdfc3992d785bce2505c9a3b0000000017'
    'a914d35515db546bb040e61651150343a218c87b471e8704004730440220279267d5c34f'
    'f4acb9b99cf5d28b1498be2c72dee87c0f331078ef906b9163bd02203b10bda36d7182a4'
    '0c3d42df74484d5e1c32fa24b0ed708f8951e82a642c569d01483045022100c452fc9665'
    '9792ac1f36846657b54c1b1dc319ef0018db53d4b9d96e2c7dbdd602203740cc070738d6'
    '1e458be5cb330c0d221478b3564dfa3f5a7ecb82e384a2fa0601475221021816325d19fd'
    '34fd87a039e83e35fc9de3c9de64a501a6684b9bf9946364fbb721037d696886864509ed'
    '63044d8f1bcd53b8def1247bd2bbe056ff81b23e8c09280f52ae000400473044022015f6'
    '687440590aec9e5f7bf2d2f69701474dd8d3df22cc314b8b557e4cd457fb02200e0f6ec2'
    '4a125fa70fac34feb5244add0cb89b317b8da807b68cec62003d02ab0148304502210090'
    '28061143f911ab7dbcfcd8851e253a14a58dd6320296be5cafcbd5f1f8af44022043b1f9'
    '1ec311f2e351ad783a2bf9591754576a3a733917e0ce2b2a6c1e0f94c001475221021816'
    '325d19fd34fd87a039e83e35fc9de3c9de64a501a6684b9bf9946364fbb721037d696886'
    '864509ed63044d8f1bcd53b8def1247bd2bbe056ff81b23e8c09280f52ae0000000000'
)

INPUTS = [
    TxIn(
        (b"G0D\x02 E\xb7C\xdb\xaa\xaa,\xd1\xef\x0b\x914oVD\xe3-\xc7\x0c\xde\x05\t"
         b"\x1b7b\xd4\xca\xbbn\xbdq\x1a\x02 tF\x10V\xc2n\xfe\xac\x0bD\x8e\x7f\xa7"
         b"iw=\xd6\xe4Cl\xdeP\\\x8fl\xa60>\xfe1\xf0\x95\x01A\x04=\\(u\xc9\xbd\x11"
         b"hu\xa7\x1a]\xb6L\xff\xcb\x139k\x16=\x03\x9b\x1d\x93'\x82H\x91\x80C4v"
         b"\xa45**\xdd\x00\xeb\xb0\xd5\xc9LQ[r\xeb\x10\xf1\xfd\x8f?\x03\xb4/J+%["
         b"\xfc\x9a\xa9\xe3"),
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
UNSPENTS_SEGWIT = [
    Unspent(100000000,
            1,
            '76a914905aa72f3d1747094a24d3adbc38905bb451ffc888ac',
            'f09c22717770fcd7e477953c3ca7ecb9bd44ec4d5392f24fdd247dbb8db2d388',
            0,
            'p2pkh'),
    Unspent(100000000,
            1,
            'a9146015d175e191e6e5b99211e3ffc6ea7658cb051a87',
            'f42c4ee1f95a3c9f5b1c6db356b72cd655fdb5de30c45fc148d3d86016b4d4cb',
            0,
            'np2wkh')
]
UNSPENTS_BATCH = [
    Unspent(2000000000,
            1,
            'a914d35515db546bb040e61651150343a218c87b471e87',
            '64064449fc2aab13316e90beb6c2a224d86a08733ff5b48e422be7688de72346',
            0,
            'np2wsh'),
    Unspent(3000000000,
            1,
            'a9146015d175e191e6e5b99211e3ffc6ea7658cb051a87',
            '37af0739136575bffa08a35269a360c047a06e5816b74383f187802c09d7dee2',
            1,
            'np2wkh')
]
UNSPENTS_MULTISIG_MANY = [
    Unspent(2000000000,
            1,
            'a914d35515db546bb040e61651150343a218c87b471e87',
            '0000000000000000000000000000000000000000000000000000000000000001',
            0,
            'np2wsh'),
    Unspent(2000000000,
            1,
            'a914f132346e75e3a317f3090a07560fe75d74e1f51087',
            '0000000000000000000000000000000000000000000000000000000000000002',
            1,
            'p2sh'),
    Unspent(2000000000,
            1,
            'a914d35515db546bb040e61651150343a218c87b471e87',
            '0000000000000000000000000000000000000000000000000000000000000003',
            2,
            'np2wsh'),
    Unspent(2000000000,
            1,
            'a914f132346e75e3a317f3090a07560fe75d74e1f51087',
            '0000000000000000000000000000000000000000000000000000000000000004',
            3,
            'p2sh'),
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
        txin = TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')
        assert txin.script_sig == b'script'
        assert txin.script_sig_len == b'\x06'
        assert txin.txid == b'txid'
        assert txin.txindex == b'\x04'
        assert txin.witness == b''
        assert txin.sequence == b'\xff\xff\xff\xff'

    def test_init_segwit(self):
        txin = TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')
        assert txin.script_sig == b'script'
        assert txin.script_sig_len == b'\x06'
        assert txin.txid == b'txid'
        assert txin.txindex == b'\x04'
        assert txin.witness == b'witness'
        assert txin.amount == None
        assert txin.sequence == b'\xff\xff\xff\xff'

    def test_equality(self):
        txin1 = TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')
        txin2 = TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')
        txin3 = TxIn(b'script', b'txi', b'\x03', sequence=b'\xff\xff\xff\xff')
        assert txin1 == txin2
        assert txin1 != txin3

    def test_repr(self):
        txin = TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')

        assert repr(txin) == "TxIn(b'script', {}, b'txid', {}, {})" \
                             "".format(repr(b'\x06'), repr(b'\x04'), repr(b'\xff\xff\xff\xff'))

    def test_repr_segwit(self):
        txin = TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')

        assert repr(txin) == "TxIn(b'script', {}, b'txid', {}, b'witness', {}, {})" \
                             "".format(repr(b'\x06'), repr(b'\x04'), repr(None), repr(b'\xff\xff\xff\xff'))

    def test_bytes_repr(self):
        txin = TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')

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
        txin = [TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')
        assert txobj.version == b'\x01\x00\x00\x00'
        assert txobj.TxIn == txin
        assert txobj.TxOut == txout
        assert txobj.locktime == b'\x00\x00\x00\x00'

    def test_init_segwit(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')
        assert txobj.version == b'\x01\x00\x00\x00'
        assert txobj.TxIn == txin
        assert txobj.TxOut == txout
        assert txobj.locktime == b'\x00\x00\x00\x00'

    def test_equality(self):
        txin1 = [TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')]
        txin2 = [TxIn(b'scrip2', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')]
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
        txin = [TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        assert repr(txobj) == "TxObj({}, {}, {}, {})" \
                              "".format(repr(b'\x01\x00\x00\x00'),
                                        repr(txin),
                                        repr(txout),
                                        repr(b'\x00\x00\x00\x00'))

    def test_bytes_repr(self):
        txin = [TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        assert bytes(txobj) == b''.join([b'\x01\x00\x00\x00',
                                         b'\x01txid\x04\x06script\xff\xff\xff\xff',
                                         b'\x01\x88\x13\x00\x00\x00\x00\x00\x00\rscript_pubkey',
                                         b'\x00\x00\x00\x00'])

    def test_bytes_repr_segwit(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        assert bytes(txobj) == b''.join([b'\x01\x00\x00\x00', b'\x00\x01',
                                         b'\x01txid\x04\x06script\xff\xff\xff\xff',
                                         b'\x01\x88\x13\x00\x00\x00\x00\x00\x00\rscript_pubkey',
                                         b'witness',
                                         b'\x00\x00\x00\x00'])

    def test_is_segwit(self):
        txin = [TxIn(b'script', b'txid', b'\x04', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')
        assert not TxObj.is_segwit(txobj)
        assert not TxObj.is_segwit(bytes(txobj))
        assert not TxObj.is_segwit(bytes(txobj).hex())

        txin = [TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')
        assert TxObj.is_segwit(txobj)
        assert TxObj.is_segwit(bytes(txobj))
        assert TxObj.is_segwit(bytes(txobj).hex())


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

        assert(len(unspents)) == 1
        assert len(outputs) == 2
        assert outputs[1][0] == RETURN_ADDRESS
        assert outputs[1][1] == unspents[0].amount - 2000

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
        outputs_original = [(BITCOIN_ADDRESS_TEST, 2500, 'satoshi')]

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

    def test_segwit_transaction(self):
        outputs = [("2NEcbT1xeB7488HqpmXeC2u5zqYFQ5n4x5Q", 50000000),
                   ("2N21Gzex7WJCzzsA5D33nofcnm1dYSKuJzT", 149990000)]
        private_key = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        tx = create_new_transaction(private_key, UNSPENTS_SEGWIT, outputs)
        assert tx == FINAL_TX_SEGWIT

    def test_batch_and_multisig_tx(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        p = [key1.public_key.hex(), key2.public_key.hex()]
        multi1 = MultiSigTestnet(key1, p, 2)
        multi2 = MultiSigTestnet(key2, p, 2)
        tx0 = create_new_transaction(
            multi2,
            UNSPENTS_BATCH,
            [("bcrt1qpm3x3jrdqhefptw3hlymmlpejttct08zgzzd2t", 4000000000),
            ("2NCWeVbWmaUp92dSFP3RddPk6r3GTd6cDd6", 999971920)]
        )
        tx1 = key1.sign_transaction(tx0, unspents=UNSPENTS_BATCH)
        tx2 = multi1.sign_transaction(tx1, unspents=UNSPENTS_BATCH[::-1])
        assert tx2 == FINAL_TX_BATCH

    def test_multisig_tx_many_inputs(self):
        key1 = PrivateKeyTestnet(WALLET_FORMAT_TEST_1)
        key2 = PrivateKeyTestnet(WALLET_FORMAT_TEST_2)
        p = [key1.public_key.hex(), key2.public_key.hex()]
        multi1 = MultiSigTestnet(key1, p, 2)
        multi2 = MultiSigTestnet(key2, p, 2)
        tx0 = create_new_transaction(
            multi1,
            UNSPENTS_MULTISIG_MANY,
            [("bcrt1qpm3x3jrdqhefptw3hlymmlpejttct08zgzzd2t", 4000000000),
            ("2NCWeVbWmaUp92dSFP3RddPk6r3GTd6cDd6", 999971920)]
        )
        tx1 = multi2.sign_transaction(tx0, unspents=UNSPENTS_MULTISIG_MANY)
        assert tx1 == FINAL_TX_MULTISIG_MANY


class TestDeserializeTransaction:
    def test_legacy_deserialize(self):
        txobj = deserialize(FINAL_TX_1)
        assert txobj.version == hex_to_bytes(FINAL_TX_1[:8])
        assert len(txobj.TxIn) == 1
        assert txobj.TxIn[0].txid == hex_to_bytes(FINAL_TX_1[10:74])
        assert txobj.TxIn[0].txindex == hex_to_bytes(FINAL_TX_1[74:82])
        assert txobj.TxIn[0].script_sig_len == hex_to_bytes(FINAL_TX_1[82:84])
        assert txobj.TxIn[0].script_sig == hex_to_bytes(FINAL_TX_1[84:360])
        assert txobj.TxIn[0].witness == b''
        assert txobj.TxIn[0].sequence == hex_to_bytes(FINAL_TX_1[360:368])
        assert len(txobj.TxOut) == 2
        assert txobj.TxOut[0].amount == hex_to_bytes(FINAL_TX_1[370:386])
        assert txobj.TxOut[0].script_pubkey_len == hex_to_bytes(FINAL_TX_1[386:388])
        assert txobj.TxOut[0].script_pubkey == hex_to_bytes(FINAL_TX_1[388:438])
        assert txobj.TxOut[1].amount == hex_to_bytes(FINAL_TX_1[438:454])
        assert txobj.TxOut[1].script_pubkey_len == hex_to_bytes(FINAL_TX_1[454:456])
        assert txobj.TxOut[1].script_pubkey == hex_to_bytes(FINAL_TX_1[456:506])
        assert txobj.locktime == hex_to_bytes(FINAL_TX_1[506:])

    def test_segwit_deserialize(self):
        txobj = deserialize(SEGWIT_TX_1)
        assert txobj.version == hex_to_bytes(SEGWIT_TX_1[:8])
        assert len(txobj.TxIn) == 2
        assert txobj.TxIn[0].txid == hex_to_bytes(SEGWIT_TX_1[14:78])
        assert txobj.TxIn[0].txindex == hex_to_bytes(SEGWIT_TX_1[78:86])
        assert txobj.TxIn[0].script_sig_len == hex_to_bytes(SEGWIT_TX_1[86:88])
        assert txobj.TxIn[0].script_sig == hex_to_bytes(SEGWIT_TX_1[88:300])
        assert txobj.TxIn[0].sequence == hex_to_bytes(SEGWIT_TX_1[300:308])
        assert txobj.TxIn[0].witness == hex_to_bytes(SEGWIT_TX_1[564:566])
        assert txobj.TxIn[1].txid == hex_to_bytes(SEGWIT_TX_1[308:372])
        assert txobj.TxIn[1].txindex == hex_to_bytes(SEGWIT_TX_1[372:380])
        assert txobj.TxIn[1].script_sig_len == hex_to_bytes(SEGWIT_TX_1[380:382])
        assert txobj.TxIn[1].script_sig == hex_to_bytes(SEGWIT_TX_1[382:428])
        assert txobj.TxIn[1].sequence == hex_to_bytes(SEGWIT_TX_1[428:436])
        assert txobj.TxIn[1].witness == hex_to_bytes(SEGWIT_TX_1[566:780])
        assert len(txobj.TxOut) == 2
        assert txobj.TxOut[0].amount == hex_to_bytes(SEGWIT_TX_1[438:454])
        assert txobj.TxOut[0].script_pubkey_len == hex_to_bytes(SEGWIT_TX_1[454:456])
        assert txobj.TxOut[0].script_pubkey == hex_to_bytes(SEGWIT_TX_1[456:500])
        assert txobj.TxOut[1].amount == hex_to_bytes(SEGWIT_TX_1[500:516])
        assert txobj.TxOut[1].script_pubkey_len == hex_to_bytes(SEGWIT_TX_1[516:518])
        assert txobj.TxOut[1].script_pubkey == hex_to_bytes(SEGWIT_TX_1[518:564])
        assert txobj.locktime == hex_to_bytes(SEGWIT_TX_1[780:])


class TestGetSignaturesFromScript:
    def test_get_signatures_1(self):
        script = hex_to_bytes(
                  '0047304402200b526cf17f86891a62f4bd27745494005682d650c27dda87'
                  '7f35b0161c38bc9002204674a0be6275ce948812c200251802d15eaa1953'
                  '3d864d64b83b992c10b3ecf201'
                  '483045022100a57ba5464a03343bd5ebf21ce0d3d49b84710c62a421b7d5'
                  'b86de75ca10d8c7602206395d6a552fc0dbb31d3c0b1db34fa4a14cc29d6'
                  '60c8c68172c7e513cb6a0ac901'
                  '475221021816325d19fd34fd87a039e83e35fc9de3c9de64a501a6684b9b'
                  'f9946364fbb721037d696886864509ed63044d8f1bcd53b8def1247bd2bbe'
                  '056ff81b23e8c09280f52ae')
        sigs = get_signatures_from_script(script)
        assert len(sigs) == 2
        assert sigs[0][:4] == hex_to_bytes('30440220')
        assert sigs[0][-4:] == hex_to_bytes('b3ecf201')
        assert sigs[1][:4] == hex_to_bytes('30450221')
        assert sigs[1][-4:] == hex_to_bytes('6a0ac901')

    def test_get_signatures_2(self):
        script = hex_to_bytes(
              '0047304402200b526cf17f86891a62f4bd27745494005682d650c27dda87'
              '7f35b0161c38bc9002204674a0be6275ce948812c200251802d15eaa1953'
              '3d864d64b83b992c10b3ecf201'
              '00'
              '695221021816325d19fd34fd87a039e83e35fc9de3c9de64a501a6684b9b'
              'f9946364fbb721037d696886864509ed63044d8f1bcd53b8def1247bd2bb'
              'e056ff81b23e8c09280f21033dc7fb58b701fc0af63ee3a8b72ebbeed04a'
              '1c006b50007f32ec6a33a56213f853ae0400483045022100f686296df668'
              '17198feead5fa24f3f04cb7e6780187e73fc8c531254fd002c13022044ef'
              'e2ea00f31de395376d83cb122bd708116d151bdf2de61107d77447b475c6'
              '0100695221021816325d19fd34fd87a039e83e35fc9de3c9de64a501a668'
              '4b9bf9946364fbb721037d696886864509ed63044d8f1bcd53b8def1247b'
              'd2bbe056ff81b23e8c09280f21033dc7fb58b701fc0af63ee3a8b72ebbee'
              'd04a1c006b50007f32ec6a33a56213f853ae')
        sigs = get_signatures_from_script(script)
        assert len(sigs) == 1
        assert sigs[0][:4] == hex_to_bytes('30440220')
        assert sigs[0][-4:] == hex_to_bytes('b3ecf201')


class TestAddressToScriptPubKey:
    def test_address_to_scriptpubkey_legacy(self):
        want = b'v\xa9\x14\x92F\x1b\xdeb\x83\xb4a\xec\xe7\xdd\xf4\xdb\xf1\xe0\xa4\x8b\xd1\x13\xd8\x88\xac'
        assert address_to_scriptpubkey(BITCOIN_ADDRESS) == want

        want = b'v\xa9\x14\x99\x0e\xf6\rc\xb5\xb5\x96J\x1c"\x82\x06\x1a\xf4Q#\xe9?\xcb\x88\xac'
        assert address_to_scriptpubkey(BITCOIN_ADDRESS_COMPRESSED) == want

    def test_address_to_scriptpubkey_legacy_p2sh(self):
        want = b'\xa9\x14U\x13\x1e\xfbz\x0e\xddLv\xcc;\xbe\x83;\xfcY\xa6\xf7<k\x87'
        assert address_to_scriptpubkey(BITCOIN_ADDRESS_PAY2SH) == want

    def test_address_to_scriptpubkey_bech32(self):
        want = b'\x00\x14\xe8\xdf\x01\x8c~2l\xc2S\xfa\xac~F\xcd\xc5\x1ehT,B'
        assert address_to_scriptpubkey(BITCOIN_SEGWIT_ADDRESS) == want

    def test_address_to_scriptpubkey_bech32_p2sh(self):
        want = b'\x00 \xc7\xa1\xf1\xa4\xd6\xb4\xc1\x80*Yc\x19f\xa1\x83Y\xdew\x9e\x8aje\x9775\xa3\xcc\xdf\xda\xbc@}'
        assert address_to_scriptpubkey(BITCOIN_SEGWIT_ADDRESS_PAY2SH) == want

    def test_address_to_scriptpubkey_legacy_test(self):
        want = b'v\xa9\x14\x92F\x1b\xdeb\x83\xb4a\xec\xe7\xdd\xf4\xdb\xf1\xe0\xa4\x8b\xd1\x13\xd8\x88\xac'
        assert address_to_scriptpubkey(BITCOIN_ADDRESS_TEST) == want

        want = b'v\xa9\x14\x99\x0e\xf6\rc\xb5\xb5\x96J\x1c"\x82\x06\x1a\xf4Q#\xe9?\xcb\x88\xac'
        assert address_to_scriptpubkey(BITCOIN_ADDRESS_TEST_COMPRESSED) == want

    def test_address_to_scriptpubkey_legacy_p2sh_test(self):
        want = b'\xa9\x14\xf2&\x1e\x95d\xc9\xdf\xff\xa8\x15\x05\xc1S\xfb\x95\xbf\x93\x99C\x08\x87'
        assert address_to_scriptpubkey(BITCOIN_ADDRESS_TEST_PAY2SH) == want

    def test_address_to_scriptpubkey_bech32_test(self):
        want = b'\x00\x14u\x1ev\xe8\x19\x91\x96\xd4T\x94\x1cE\xd1\xb3\xa3#\xf1C;\xd6'
        assert address_to_scriptpubkey(BITCOIN_SEGWIT_ADDRESS_TEST.lower()) == want
        assert address_to_scriptpubkey(BITCOIN_SEGWIT_ADDRESS_TEST.upper()) == want

    def test_address_to_scriptpubkey_bech32_p2sh_test(self):
        want = b"\x00 \x18c\x14<\x14\xc5\x16h\x04\xbd\x19 3V\xda\x13l\x98Vx\xcdM'\xa1\xb8\xc62\x96\x04\x902b"
        assert address_to_scriptpubkey(BITCOIN_SEGWIT_ADDRESS_TEST_PAY2SH.lower()) == want
        assert address_to_scriptpubkey(BITCOIN_SEGWIT_ADDRESS_TEST_PAY2SH.upper()) == want

    def test_address_to_scriptpubkey_invalid_checksum(self):
        address_invalid = BITCOIN_ADDRESS[:6] + "error" + BITCOIN_ADDRESS[11:]
        with pytest.raises(ValueError):
            address_to_scriptpubkey(address_invalid)

        address_invalid = BITCOIN_ADDRESS_PAY2SH[:6] + "error" + BITCOIN_ADDRESS_PAY2SH[11:]
        with pytest.raises(ValueError):
            address_to_scriptpubkey(address_invalid)

        address_invalid = BITCOIN_SEGWIT_ADDRESS[:6] + "error" + BITCOIN_SEGWIT_ADDRESS[11:]
        with pytest.raises(ValueError):
            address_to_scriptpubkey(address_invalid)

    def test_address_to_scriptpubkey_invalid_address(self):
        address_invalid = "X" + BITCOIN_ADDRESS[1:]
        with pytest.raises(ValueError):
            address_to_scriptpubkey(address_invalid)

        address_invalid = "X" + BITCOIN_ADDRESS_PAY2SH[1:]
        with pytest.raises(ValueError):
            address_to_scriptpubkey(address_invalid)

        address_invalid = "X" + BITCOIN_SEGWIT_ADDRESS[1:]
        with pytest.raises(ValueError):
            address_to_scriptpubkey(address_invalid)


class TestCalculatePreimages:
    def test_calculate_preimages(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        want = b'yI\x8d\x99H\xcb\xe3\x88\xce\x83}\xc1\xfc\xaf\xf7\xd5\\\xf67\x93\x86\xb5\xc7M\xd1\xdb\xd2LyJ`<'
        assert calculate_preimages(txobj, [(0, HASH_TYPE, False)])[0] == want

        want = b'\xed\x85\xc1\x0f\xc2\xb1\xc9\x05\xbf\xa6S\x15\xba$\x84\xad\x14\x8dni\x17\x1eD\xd6\xf7e\xd8\x0e\xfb\x05\x93\x1a'
        assert calculate_preimages(txobj, [(0, HASH_TYPE, True)])[0] == want

    def test_calculate_preimages_unsupported_hashtypes(self):
        txin = [TxIn(b'script', b'txid', b'\x04', b'witness', sequence=b'\xff\xff\xff\xff')]
        txout = [TxOut(b'\x88\x13\x00\x00\x00\x00\x00\x00', b'script_pubkey')]
        txobj = TxObj(b'\x01\x00\x00\x00', txin, txout, b'\x00\x00\x00\x00')

        with pytest.raises(ValueError):
            calculate_preimages(txobj, [(0, b'\x02\x00\x00\x00', False)])

        with pytest.raises(ValueError):
            calculate_preimages(txobj, [(0, b'\x03\x00\x00\x00', False)])

        with pytest.raises(ValueError):
            calculate_preimages(txobj, [(0, b'\x81\x00\x00\x00', False)])

        with pytest.raises(ValueError):
            calculate_preimages(txobj, [(0, b'\x04\x00\x00\x00', False)])


class TestSignTx:
    def test_sign_tx_legacy_input(self):
        key = PrivateKey(WALLET_FORMAT_TEST_1)
        txobj = deserialize(UNSIGNED_TX_SEGWIT)
        tx = sign_tx(key, txobj, unspents=[UNSPENTS_SEGWIT[0]])
        assert tx[:380] == FINAL_TX_SEGWIT[:380]

    def test_sign_tx_segwit(self):
        key = PrivateKey(WALLET_FORMAT_TEST_1)
        txobj = deserialize(UNSIGNED_TX_SEGWIT)
        assert sign_tx(key, txobj, unspents=UNSPENTS_SEGWIT) == FINAL_TX_SEGWIT

    def test_sign_tx_multisig(self):
        key1 = PrivateKey(WALLET_FORMAT_TEST_1)
        key2 = PrivateKey(WALLET_FORMAT_TEST_2)
        multi = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        txobj = deserialize(UNSIGNED_TX_BATCH)
        tx = sign_tx(multi, txobj, unspents=[UNSPENTS_BATCH[0]])
        assert tx[:238] == FINAL_TX_BATCH[:238]

    def test_sign_tx_invalid_unspents(self):
        key = PrivateKey(WALLET_FORMAT_TEST_1)
        txobj = deserialize(UNSIGNED_TX_SEGWIT)
        with pytest.raises(TypeError):
            # Unspents must be presented as list:
            sign_tx(key, txobj, unspents=UNSPENTS_SEGWIT[0])

    def test_sign_tx_invalid_segwit_no_amount(self):
        key = PrivateKey(WALLET_FORMAT_TEST_1)
        txobj = deserialize(UNSIGNED_TX_SEGWIT)
        unspents = copy.deepcopy(UNSPENTS_SEGWIT)
        unspents[1].amount = None
        with pytest.raises(ValueError):
            sign_tx(key, txobj, unspents=unspents)

    def test_sign_tx_invalid_multisig_already_fully_signed(self):
        key1 = PrivateKey(WALLET_FORMAT_TEST_1)
        key2 = PrivateKey(WALLET_FORMAT_TEST_2)
        multi = MultiSig(key1, [key1.public_key, key2.public_key], 2)
        txobj = deserialize(FINAL_TX_BATCH)
        with pytest.raises(ValueError):
            sign_tx(multi, txobj, unspents=[UNSPENTS_BATCH[0]])


class TestEstimateTxFee:
    def test_accurate_compressed(self):
        assert estimate_tx_fee(148, 1, 68, 2, 70) == 15820

    def test_accurate_uncompressed(self):
        assert estimate_tx_fee(180, 1, 68, 2, 70) == 18060

    def test_none(self):
        assert estimate_tx_fee(740, 5, 170, 5, 0) == 0


class TestSelectCoins:
    def test_perfect_match(self):
        unspents, remaining = select_coins(100000000, 0, [34, 34], 0, absolute_fee=True,
            consolidate=False, unspents=UNSPENTS_SEGWIT)
        assert len(unspents) == 1
        assert remaining == 0

    def test_perfect_match_with_range(self):
        unspents, remaining = select_coins(99960000, 200, [34, 34], 0, absolute_fee=True,
            consolidate=False, unspents=UNSPENTS_SEGWIT)
        assert len(unspents) == 1
        assert remaining == 0

    def test_random_draw(self):
        print(UNSPENTS_SEGWIT)
        unspents, remaining = select_coins(150000000, 0, [34, 34], 0, absolute_fee=True,
            consolidate=False, unspents=UNSPENTS_SEGWIT)
        assert all([u in UNSPENTS_SEGWIT for u in unspents])
        assert remaining == 50000000


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
            message='hello'*18, version='test'
        )
        outs = construct_outputs(outputs)
        assert len(outs) == 5 and outs[3].amount == amount and outs[4].amount == amount

    def test_outputs_pay2sh(self):
        amount = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        _, outputs = sanitize_tx_data(
            UNSPENTS, [(BITCOIN_ADDRESS_PAY2SH, 1, 'satoshi')], 0, RETURN_ADDRESS_MAIN
        )
        outs = construct_outputs(outputs)
        assert len(outs) == 2 and outs[0].amount == amount and outs[0].script_pubkey.hex() == 'a914' + PAY2SH_HASH.hex() + '87'

    def test_outputs_pay2sh_testnet(self):
        amount = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        _, outputs = sanitize_tx_data(
            UNSPENTS, [(BITCOIN_ADDRESS_TEST_PAY2SH, 1, 'satoshi')], 0, RETURN_ADDRESS, version='test'
        )
        outs = construct_outputs(outputs)
        assert len(outs) == 2 and outs[0].amount == amount and outs[0].script_pubkey.hex() == 'a914' + PAY2SH_TEST_HASH.hex() + '87'

    def test_outputs_pay2segwit(self):
        amount = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        _, outputs = sanitize_tx_data(
            UNSPENTS, [(BITCOIN_SEGWIT_ADDRESS, 1, 'satoshi'), (BITCOIN_SEGWIT_ADDRESS_PAY2SH, 1, 'satoshi')], 0, RETURN_ADDRESS_MAIN
        )
        outs = construct_outputs(outputs)
        assert len(outs) == 3 and outs[0].amount == amount and outs[0].script_pubkey.hex() == '0014' + BITCOIN_SEGWIT_HASH
        assert outs[1].amount == amount and outs[1].script_pubkey.hex() == '0020' + BITCOIN_SEGWIT_HASH_PAY2SH

    def test_outputs_pay2segwit_testnet(self):
        amount = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        _, outputs = sanitize_tx_data(
            UNSPENTS, [(BITCOIN_SEGWIT_ADDRESS_TEST, 1, 'satoshi'), (BITCOIN_SEGWIT_ADDRESS_TEST_PAY2SH, 1, 'satoshi')], 0, RETURN_ADDRESS, version='test'
        )
        outs = construct_outputs(outputs)
        assert len(outs) == 3 and outs[0].amount == amount and outs[0].script_pubkey.hex() == '0014' + BITCOIN_SEGWIT_HASH_TEST
        assert outs[1].amount == amount and outs[1].script_pubkey.hex() == '0020' + BITCOIN_SEGWIT_HASH_TEST_PAY2SH


class TestCalcTxId:
    def test_calc_txid_legacy(self):
        assert calc_txid(FINAL_TX_1) == 'e6922a6e3f1ff422113f15543fbe1340a727441202f55519640a70ac4636c16f'

    def test_calc_txid_segwit(self):
        assert calc_txid(SEGWIT_TX_1) == 'a103ed36e9afee8b4001b1c3970ba8cd9839ff95e8b8af3fbe6016f6287bf9c6'
