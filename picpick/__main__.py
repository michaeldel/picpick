import argparse
import pathlib

from .controller import Controller
from .model import Image, Model, Tag


def dir_path(input: str) -> pathlib.Path:
    path = pathlib.Path(input)
    if not path.is_dir():
        raise NotADirectoryError
    return path


parser = argparse.ArgumentParser(prog='picpick')
parser.add_argument(
    'input',
    nargs='+',
    type=pathlib.Path,
    help="path of input file (e.g. /tmp/pic.jpg)",
)
parser.add_argument(
    '--tags', nargs='+', type=str, help="name of tag (e.g. red)",
)
parser.add_argument(
    '--copy', action='store_true', help="copy the input files instead of moving them"
)
args = parser.parse_args()

# TODO: enforce input and tags uniqueness
model = Model()

for path in args.input:
    model.images.add(Image(path=path))
for name in args.tags:
    model.tags.add(Tag(name=name))

controller = Controller(model=model)
controller.run()
