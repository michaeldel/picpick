import pathlib

from dataclasses import dataclass
from typing import Set


class Image:
    def __init__(self, path: pathlib.Path):
        self.path = path  # TODO: set as PK ?
        self.tags: Set[Tag] = set()


@dataclass(frozen=True)
class Tag:
    name: str


class Model:
    def __init__(self):
        self.images: Set[Image] = set()
        self.tags: Set[Tag] = set()
