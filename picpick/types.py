import pathlib

from dataclasses import dataclass


class Image:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.tags = set()


@dataclass(frozen=True)
class InputImage:
    path: pathlib.Path


@dataclass
class Output:
    path: pathlib.Path


@dataclass(frozen=True)
class Tag:
    name: str
