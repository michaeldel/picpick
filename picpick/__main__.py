import pathlib

from typing import Optional

import click

from .controller import Controller
from .model import Model


@click.command()
@click.argument('filename', type=click.Path(exists=True), required=False)
def empty(filename: Optional[str]):
    model = Model()
    controller = Controller(model=model)

    if filename is not None:
        controller.load(pathlib.Path(filename))

    controller.run()


empty()
