import pathlib
import shutil
import tempfile

from typing import Callable, Collection, Generator, Protocol

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


class ModelFactory(Protocol):
    def __call__(
        self, *, filenames: Collection[str], tagnames: Collection[str]
    ) -> Model:
        ...


@pytest.fixture
def model_factory(image_factory) -> ModelFactory:
    def inner(
        filenames: Collection[str] = None, tagnames: Collection[str] = None
    ) -> Model:
        model = Model()

        for filename in filenames or []:
            model.images.add(image_factory(filename))
        for tagname in tagnames or []:
            model.tags.add(Tag(name=tagname))
        return model

    return inner


@pytest.fixture
def model(model_factory) -> Model:
    return model_factory(('one.jpg', 'two.jpg', 'three.jpg'), ('red', 'green', 'blue'))
