import argparse
import pathlib

from .app import App
from .gui import MainWindow


def dir_path(input: str) -> pathlib.Path:
    path = pathlib.Path(input)
    if not path.is_dir():
        raise NotADirectoryError
    return path


parser = argparse.ArgumentParser(prog='picpick')
# parser.add_argument(
#     '--config',
#     nargs='?',
#     type=pathlib.Path,
#     help="Path of config file (e.g. /tmp/config.ini)",
# )
parser.add_argument(
    'input',
    nargs='+',
    type=pathlib.Path,
    help="path of input file (e.g. /tmp/pic.jpg)",
)
parser.add_argument(
    '--output',
    nargs='+',
    type=dir_path,
    help="path of output directory (e.g. /tmp/liked/)",
)
parser.add_argument(
    '--copy', action='store_true', help="copy the input files instead of moving them"
)
args = parser.parse_args()

print(args)

mode = 'copy' if args.copy else 'move'
app = App(args.input, args.output, mode)

window = MainWindow(app=app)
window.run()
