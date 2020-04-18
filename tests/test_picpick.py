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
    red = Tag(name='red')
    blue = Tag(name='blue')
    controller.add_tags((red, blue))
    assert controller.tags == {red, blue}
    assert controller.current_image.tags == set()

    # tag image
    controller.tag_image(controller.current_image, red)
    controller.tag_image(controller.current_image, blue)
    assert controller.current_image.tags == {red, blue}

    # tagging an image with the same tag should not do anything
    controller.tag_image(controller.current_image, red)
    assert controller.current_image.tags == {red, blue}

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
    assert controller.tags == {red, blue}
    assert controller.current_image.tags == {red, blue}


def test_tag_and_untag():
    controller = Controller()

    path = pathlib.Path('foo.jpg')
    controller.add_images((path,))

    assert controller.current_image.path == path

    red = Tag(name='red')
    blue = Tag(name='blue')
    controller.add_tags((red, blue))
    assert controller.tags == {red, blue}
    assert controller.current_image.tags == set()

    image = controller.current_image

    controller.tag_image(image, red)
    controller.tag_image(image, blue)
    assert image.tags == {red, blue}

    controller.untag_image(image, red)
    assert image.tags == {blue}
