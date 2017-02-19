# from bit.network import get_decoded_tx
#
# TESTNET_TX = ('01000000018878399d83ec25c627cfbf753ff9ca3602373eac437ab2676154a3c2'
#               'da23adf3010000008a473044022068b8dce776ef1c071f4c516836cdfb358e44ef'
#               '58e0bf29d6776ebdc4a6b719df02204ea4a9b0f4e6afa4c229a3f11108ff66b178'
#               '95015afa0c26c4bbc2b3ba1a1cc60141043d5c2875c9bd116875a71a5db64cffcb'
#               '13396b163d039b1d932782489180433476a4352a2add00ebb0d5c94c515b72eb10'
#               'f1fd8f3f03b42f4a2b255bfc9aa9e3ffffffff0250c30000000000001976a914e7'
#               'c1345fc8f87c68170b3aa798a956c2fe6a9eff88ac0888fc04000000001976a914'
#               '92461bde6283b461ece7ddf4dbf1e0a48bd113d888ac00000000')
#
#
# def test_get_decoded_tx():
#     tx = get_decoded_tx(TESTNET_TX, test=True)
#     assert len(tx['data']['tx']['vout']) == 2
