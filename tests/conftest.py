import pathlib
import shutil
import tempfile

from typing import Callable, Generator

import pytest  # type: ignore

from PIL import Image as PILImage  # type: ignore

from picpick.model import Image, Model, Tag


@pytest.fixture()
def basedir() -> Generator[pathlib.Path, None, None]:
    dir = pathlib.Path(tempfile.mkdtemp())
    yield dir
    shutil.rmtree(dir)


@pytest.fixture
def image_factory(basedir) -> Callable[[str], Image]:
    def inner(name: str) -> Image:
        path = basedir / pathlib.Path(name)
        PILImage.new(mode='RGB', size=(8, 8)).save(path)
        return Image(path=path)

    return inner


@pytest.fixture
def model(image_factory) -> Model:
    m = Model()

    for filename in ('one.jpg', 'two.jpg', 'three.jpg'):
        m.images.add(image_factory(filename))
    for tagname in ('red', 'green', 'blue'):
        m.tags.add(Tag(name=tagname))

    return m
