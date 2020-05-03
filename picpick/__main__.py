import pathlib

from typing import Optional

import click

from . import __version__
from .controller import Controller
from .model import Model


def version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.command()
@click.argument('filename', type=click.Path(exists=True), required=False)
@click.option(
    '--version', is_flag=True, callback=version, expose_value=False, is_eager=True
)
def run(filename: Optional[str]):
    model = Model()
    controller = Controller(model=model)

    if filename is not None:
        controller.load(pathlib.Path(filename))

    controller.run()


run()
