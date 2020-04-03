import argparse
import pathlib

from typing import List

from .gui import MainWindow


def dir_path(input: str) -> pathlib.Path:
    path = pathlib.Path(input)
    if not path.is_dir():
        print(input)
        print('---')
        print(path)
        raise NotADirectoryError
    return path


parser = argparse.ArgumentParser(prog='picpick')
parser.add_argument(
    'input',
    nargs='+',
    type=pathlib.Path,
    help="Path of input file (e.g. /tmp/pic.jpg)",
)
parser.add_argument(
    '--output',
    nargs='+',
    type=dir_path,
    help="Path of output directory (e.g. /tmp/liked/)",
)
args = parser.parse_args()

print(args)

window = MainWindow(args.input, args.output)
window.run()
