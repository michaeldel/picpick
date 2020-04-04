import pathlib

from dataclasses import dataclass


@dataclass(frozen=True)
class InputImage:
    path: pathlib.Path


@dataclass
class Output:
    path: pathlib.Path
