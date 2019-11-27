import click
from flask.cli import FlaskGroup

from nairaland.app import create_app


def create_nairaland(info):
    return create_app(cli=True)


@click.group(cls=FlaskGroup, create_app=create_nairaland)
def cli():
    """Main entry point"""


if __name__ == "__main__":
    cli()
