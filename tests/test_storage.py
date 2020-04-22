import pathlib
import secrets
import shutil
import tempfile

import pytest

from picpick import storage
from picpick.model import Image, Model, Tag


@pytest.fixture
def save_path() -> pathlib.Path:
    dir = pathlib.Path(tempfile.mkdtemp())
    filename = f'{secrets.token_urlsafe()}.pickle'

    yield dir / filename

    shutil.rmtree(dir)


def test_save_and_load(save_path: pathlib.Path):
    model = Model()

    foo = Image(path='foo.jpg')
    bar = Image(path='bar.jpg')

    red = Tag(name='red')
    blue = Tag(name='blue')

    model.images = {foo, bar}
    model.tags = {red, blue}

    current_index = 1

    storage.save(save_path, model, current_index=current_index)
    loaded_model, loaded_current_index = storage.load(save_path)

    assert loaded_model is not model
    assert loaded_current_index == current_index

    assert len(loaded_model.images) == len(model.images) == 2
    assert len(loaded_model.tags) == len(model.tags) == 2

    assert {i.path for i in loaded_model.images} == {'foo.jpg', 'bar.jpg'}
    assert loaded_model.tags == model.tags == {red, blue}
