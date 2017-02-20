import click

from bit.keygen import generate_matching_address


@click.group(invoke_without_command=True)
def bit():
    pass


@bit.command()
@click.argument('prefix')
@click.option('--cores', '-c', default='all')
def gen(prefix, cores):
    click.echo(generate_matching_address(prefix, cores))
