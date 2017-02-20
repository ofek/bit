import click
import pyperclip
import time
from bit.transaction import (
    TxIn, calc_txid, create_p2pkh_transaction, construct_input_block,
    construct_output_block, estimate_tx_fee, sanitize_tx_data
)
from bit.keygen import generate_matching_address, generate_private_key
from bit.wallet import Key, PrivateKeyTestnet
MAIN_ADDRESS_USED1 = '1L2JsXHPMYuAa9ugvHGLwkdstCPUDemNCf'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'


@click.group(invoke_without_command=True)
def bit():
    k=PrivateKeyTestnet('cU6s7jckL3bZUUkb3Q2CD9vNu8F1o58K5R5a3JFtidoccMbhEGKZ')
    print(k.get_balance())
    print(k.get_unspents())
    print(len(k.get_transactions()))
    tx=k.send([('n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi', 1, 'jpy')])
    pyperclip.copy(tx)
    time.sleep(10)
    print(len(k.get_transactions()))


@bit.command()
@click.argument('prefix')
@click.option('--cores', '-c', default='all')
def gen(prefix, cores):
    click.echo(generate_matching_address(prefix, cores))
