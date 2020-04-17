import pathlib

from picpick import __version__

from picpick.controller import Controller
from picpick.types import Tag


def test_version():
    assert __version__ == '0.1.0'


def test_open_and_tag_some_images():
    controller = Controller()

    assert controller.images_paths == []
    assert controller.tags == set()

    paths = list(map(pathlib.Path, ('one.jpg', 'two.jpg', 'three.jpg')))

    # add an image
    controller.add_images(paths)

    # images must be ordered alphabetically
    assert controller.images_paths == [
        pathlib.Path('one.jpg'),
        pathlib.Path('three.jpg'),
        pathlib.Path('two.jpg'),
    ]
    assert controller.current_image.path == pathlib.Path('one.jpg')

    # add a tag
    tag = Tag(name='red')
    controller.add_tags((tag,))
    assert controller.tags == {tag}
    assert controller.current_image.tags == set()

    # tag image
    controller.tag_image(controller.current_image, tag)
    assert controller.current_image.tags == {tag}

    # tagging an image again should not do anything
    controller.tag_image(controller.current_image, tag)
    assert controller.current_image.tags == {tag}

    # save picking to file
    controller.save(pathlib.Path('/tmp/db.pickle'))

    # start new picking
    controller = Controller()
    assert controller.images_paths == []
    assert controller.tags == set()

    # load previously saved picking
    controller.load(pathlib.Path('/tmp/db.pickle'))
    assert controller.images_paths == [
        pathlib.Path('one.jpg'),
        pathlib.Path('three.jpg'),
        pathlib.Path('two.jpg'),
    ]
    assert controller.tags == {tag}
    assert controller.current_image.tags == {tag}
