import click

from .controller import Controller
from .model import Model


@click.command()
def empty():
    model = Model()
    controller = Controller(model=model)
    controller.run()


empty()
