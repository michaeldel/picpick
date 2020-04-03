import argparse
import pathlib

from typing import List

from .gui import MainWindow


def path(input: List[str]) -> List[pathlib.Path]:
    return [pathlib.Path(s) for s in input]


parser = argparse.ArgumentParser(prog='picpick')
parser.add_argument(
    'input', nargs='+', type=pathlib.Path, help="Path of input file (e.g. /tmp/pic.jpg)"
)
args = parser.parse_args()

print(args)

window = MainWindow(args.input)
window.run()
