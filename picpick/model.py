import pathlib

from dataclasses import dataclass


class Image:
    def __init__(self, path: pathlib.Path):
        self.path = path  # TODO: set as PK ?
        self.tags = set()


@dataclass(frozen=True)
class Tag:
    name: str


class Model:
    def __init__(self):
        self.images = set()
        self.tags = set()
