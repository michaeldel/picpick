from picpick import __version__

from picpick.controller import Controller
from picpick.model import Model, Tag


def test_version():
    assert __version__ == '0.1.0'


def test_empty_add_one_image_and_tag_it(basedir, image_factory):
    controller = Controller(model=Model())
    assert controller._view.title() == "PicPick *"
    assert controller.images == []
    assert controller.tags == []
    assert controller.current_image is None

    controller.save(basedir / 'save.picpick')
    assert controller._view.title() == "PicPick"

    controller.add_image(image_factory('foo.jpg'))
    assert [image.path.name for image in controller.images] == ['foo.jpg']


def test_tag_some_images(basedir, model: Model):
    controller = Controller(model=model)

    assert controller._view.title() == "PicPick *"

    # images and tags must be ordered alphabetically
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
    assert controller.current_image is not None
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
    assert controller._view.title() == "PicPick"

    # add tags to last image
    controller.set_current_image(controller.images[2])
    assert controller.current_image.path.name == 'two.jpg'
    assert controller.current_image.tags == set()

    controller.tag_current_image(blue)
    assert controller.current_image.tags == {blue}
    assert controller._view.title() == "PicPick *"

    # load previous picking and ensure tagging rollbacked
    controller.load(basedir / 'save.pickle')
    assert controller._view.title() == "PicPick"

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
    assert controller._view.title() == "PicPick *"

    # first image tags should have remained the same
    controller.set_current_image(controller.images[0])
    assert controller.current_image.path.name == 'one.jpg'
    assert controller.current_image.tags == {red, blue}

    # add tags to last image again
    controller.set_current_image(controller.images[2])
    assert controller.current_image.path.name == 'two.jpg'
    assert controller.current_image.tags == set()

    controller.tag_current_image(red)
    assert controller.current_image.tags == {red}

    # save with save current (not save as) function
    controller.save_current()
    assert controller._view.title() == "PicPick"

    # remove tag from last image and load again to ensure save worked
    controller.untag_current_image(red)
    assert controller.current_image.tags == set()

    controller.load(basedir / 'save.pickle')
    assert controller._view.title() == "PicPick"

    assert controller.current_image.path.name == 'two.jpg'
    assert controller.current_image.tags == {red}
