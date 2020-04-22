import pathlib
import shutil
import tempfile

from typing import Callable

import pytest

from PIL import Image as PILImage

from picpick import __version__

from picpick.controller import Controller
from picpick.model import Image, Model, Tag


def test_version():
    assert __version__ == '0.1.0'


@pytest.fixture()
def basedir() -> pathlib.Path:
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


def test_tag_some_images(basedir, model):
    controller = Controller(model=model)

    # images and tagsmust be ordered alphabetically
    assert [image.path.name for image in controller.images] == [
        'one.jpg',
        'three.jpg',
        'two.jpg',
    ]

    red = Tag(name='red')
    green = Tag(name='green')
    blue = Tag(name='blue')
    assert controller.tags == [blue, green, red]

    # initially selected image is first one
    assert controller.current_image.path.name == 'one.jpg'
    assert controller.current_image.tags == set()

    # tag image
    controller.tag_current_image(tag=red)
    controller.tag_current_image(tag=blue)
    assert controller.current_image.tags == {red, blue}

    # select next image
    controller.set_current_image(controller.images[1])
    assert controller.current_image.path.name == 'three.jpg'
    assert controller.current_image.tags == set()

    # tag and untag image
    controller.tag_current_image(red)
    controller.tag_current_image(green)
    assert controller.current_image.tags == {red, green}

    controller.untag_current_image(red)
    assert controller.current_image.tags == {green}

    # save picking to file
    controller.save(basedir / 'save.pickle')

    # add tags to last image
    controller.set_current_image(controller.images[2])
    assert controller.current_image.path.name == 'two.jpg'
    assert controller.current_image.tags == set()

    controller.tag_current_image(blue)
    assert controller.current_image.tags == {blue}

    # load previous picking and ensure tagging rollbacked
    controller.load(basedir / 'save.pickle')

    # tags an images should be the same
    assert [image.path.name for image in controller.images] == [
        'one.jpg',
        'three.jpg',
        'two.jpg',
    ]
    assert controller.tags == [blue, green, red]

    # because it's the same file, current_image should be the same as saved
    assert controller.current_image.path.name == 'three.jpg'
    assert controller.current_image.tags == {green}

    # last image tags should have been rollbacked
    controller.set_current_image(controller.images[2])
    assert controller.current_image.path.name == 'two.jpg'
    assert controller.current_image.tags == set()

    # first image tags should have remained the same
    controller.set_current_image(controller.images[0])
    assert controller.current_image.path.name == 'one.jpg'
    assert controller.current_image.tags == {red, blue}
