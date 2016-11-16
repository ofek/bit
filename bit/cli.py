import click

from bit.keygen import generate_matching_address
from bit.network import InsightAPI


@click.group(invoke_without_command=True)
def bit():
    print(generate_matching_address(''))
    #print(InsightAPI.get_balance('mtrNwJxS1VyHYn3qBY1Qfsm3K3kh1mGRMS', version='test'))


@bit.command()
@click.argument('prefix')
@click.option('--cores', '-c', default='all')
def gen(prefix, cores):
    print(generate_matching_address(prefix, cores))
