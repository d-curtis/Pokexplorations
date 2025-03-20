import click
from romfile import String

@click.group()
def cli():
    """A CLI tool for encoding and decoding."""
    pass

@click.command()
@click.argument("text")
def encode(text):
    """Encodes a string into a byte array (hex)."""
    click.echo(String.from_str(text).data.hex())


@click.command()
@click.argument("hex_string")
def decode(hex_string):
    """Decodes a byte array (hex) back into a string."""
    click.echo(str(String(bytes.fromhex(hex_string))))


cli.add_command(encode)
cli.add_command(decode)

if __name__ == "__main__":
    cli()