import click

from bit.keygen import generate_matching_address
from bit.network import satoshi_to_currency, satoshi_to_currency_cached


@click.group(invoke_without_command=True)
def bit():
    print(satoshi_to_currency(100000, 'jpy'))


@bit.command()
@click.argument('prefix')
@click.option('--cores', '-c', default='all')
def gen(prefix, cores):
    click.echo(generate_matching_address(prefix, cores))
