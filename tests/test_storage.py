import pathlib

from picpick import storage
from picpick.model import Image, Model, Tag


def test_save_and_load_empty(basedir: pathlib.Path):
    model = Model()
    save_path = basedir / 'save.pickle'

    storage.save(save_path, model, current_index=None)
    loaded_model, loaded_current_index = storage.load(save_path)

    assert loaded_model is not model
    assert loaded_current_index is None

    assert loaded_model.images == model.images == set()
    assert loaded_model.tags == model.tags == set()


def test_save_and_load_some_images_and_tags(basedir: pathlib.Path):
    model = Model()

    foo = Image(path=pathlib.Path('foo.jpg'))
    bar = Image(path=pathlib.Path('bar.jpg'))

    red = Tag(name='red')
    blue = Tag(name='blue')

    model.images = {foo, bar}
    model.tags = {red, blue}

    current_index = 1

    save_path = basedir / 'save.pickle'

    storage.save(save_path, model, current_index=current_index)
    loaded_model, loaded_current_index = storage.load(save_path)

    assert loaded_model is not model
    assert loaded_current_index == current_index

    assert len(loaded_model.images) == len(model.images) == 2
    assert len(loaded_model.tags) == len(model.tags) == 2

    assert {i.path for i in loaded_model.images} == {
        pathlib.Path('foo.jpg'),
        pathlib.Path('bar.jpg'),
    }
    assert loaded_model.tags == model.tags == {red, blue}
