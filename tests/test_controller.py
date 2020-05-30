import pathlib

from unittest import mock

import pytest  # type: ignore

from picpick.controller import Controller
from picpick.model import Model, Tag


def test_current_image(model: Model):
    controller = Controller(model=Model())
    assert not hasattr(controller, '_current_image')

    controller = Controller(model=model)

    assert controller._current_image.path.name == 'one.jpg'
    controller.set_current_image(controller.images[1])
    assert controller._current_image.path.name == 'three.jpg'
    controller.set_current_image(controller.images[2])
    assert controller._current_image.path.name == 'two.jpg'
    controller.set_current_image(controller.images[0])
    assert controller._current_image.path.name == 'one.jpg'

    controller.set_current_image(None)
    assert not hasattr(controller, '_current_image')


def test_add_image(image_factory):
    view = mock.MagicMock()
    controller = Controller(model=Model())
    controller._view = view
    assert not hasattr(controller, '_current_image')

    # adding the first image should automatically set it as current
    controller.add_image(image_factory('foo.jpg'))
    assert controller._current_image.path.name == 'foo.jpg'
    assert [image.path.name for image in controller.images] == ['foo.jpg']

    view.update_images.assert_called_once_with()
    view.reset_mock()

    controller.add_image(image_factory('bar.jpg'))
    assert controller._current_image.path.name == 'foo.jpg'
    assert [image.path.name for image in controller.images] == ['bar.jpg', 'foo.jpg']

    view.update_images.assert_called_once_with()
    view.reset_mock()

    # adding the same image twice should fail
    with pytest.raises(
        Controller.ImageAlreadyPresent, match="foo.jpg is already present"
    ):
        controller.add_image(image_factory('foo.jpg'))
    assert [image.path.name for image in controller.images] == ['bar.jpg', 'foo.jpg']

    view.update_images.assert_not_called()
    view.reset_mock()


def test_images(image_factory):
    controller = Controller(model=Model())
    assert controller.images == []

    for name in ('foo.jpg', 'bar.jpg', 'baz.jpg'):
        controller.add_image(image_factory(name))

    # images must be ordered alphabetically
    assert [image.path.name for image in controller.images] == [
        'bar.jpg',
        'baz.jpg',
        'foo.jpg',
    ]


def test_add_tag():
    view = mock.MagicMock()
    controller = Controller(model=Model())
    controller._view = view
    assert controller.tags == []

    controller.add_tag(Tag(name="foo"))

    view.update_tags.assert_called_once_with()
    view.reset_mock()

    controller.add_tag(Tag(name="bar"))

    view.update_tags.assert_called_once_with()
    view.reset_mock()

    assert controller.tags == [Tag(name="bar"), Tag(name="foo")]


def test_delete_tag(model_factory):
    controller = Controller(model_factory((), ("foo",)))
    assert controller.tags == [Tag(name="foo")]

    view = mock.MagicMock()
    controller._view = view

    controller.delete_tag(Tag(name="foo"))
    assert controller._model.tags == set()

    view.update_tags.assert_called_once_with()

    # no loaded image, hence should not update it
    view.update_current_image_tags.assert_not_called()
    view.reset_mock()

    controller = Controller(model_factory(('pic.jpg',), ("foo", "bar")))
    assert controller.current_image is not None
    assert controller.tags == [Tag(name="bar"), Tag(name="foo")]

    controller.current_image.tags = {Tag(name="foo"), Tag(name="bar")}

    controller._view = view

    controller.delete_tag(Tag(name="foo"))
    assert controller.tags == [Tag(name="bar")]

    assert controller._model.tags == {Tag(name="bar")}
    assert controller.current_image.tags == {Tag(name="bar")}

    view.update_tags.assert_called_once_with()
    view.update_current_image_tags.assert_called_once_with()
    view.reset_mock()

    controller.delete_tag(Tag(name="bar"))
    assert controller.tags == []

    assert controller._model.tags == set()
    assert controller.current_image.tags == set()

    view.update_tags.assert_called_once_with()
    view.update_current_image_tags.assert_called_once_with()
    view.reset_mock()


def test_update_tag(model_factory):
    controller = Controller(model_factory((), ("foo",)))
    assert controller.tags == [Tag(name="foo")]

    view = mock.MagicMock()
    controller._view = view

    controller.update_tag(old=Tag(name="foo"), new=Tag(name="bar"))
    assert controller._model.tags == {Tag(name="bar")}

    view.update_tags.assert_called_once_with()

    # no loaded image, hence should not update it
    view.update_current_image_tags.assert_not_called()
    view.reset_mock()

    controller = Controller(model_factory(('pic.jpg',), ("foo", "bar")))
    assert controller.current_image is not None

    controller.current_image.tags = {Tag(name="foo"), Tag(name="bar")}

    controller._view = view

    controller.update_tag(Tag(name="bar"), Tag(name="qux"))
    assert controller.tags == [Tag(name="foo"), Tag(name="qux")]

    assert controller._model.tags == {Tag(name="foo"), Tag(name="qux")}
    assert controller.current_image.tags == {Tag(name="foo"), Tag(name="qux")}

    view.update_tags.assert_called_once_with()
    view.update_current_image_tags.assert_not_called()
    view.reset_mock()

    with pytest.raises(
        Controller.TagAlreadyPresent, match="\"qux\" tag is already present"
    ):
        controller.update_tag(Tag(name="foo"), Tag(name="qux"))

    assert controller.tags == [Tag(name="foo"), Tag(name="qux")]

    assert controller._model.tags == {Tag(name="foo"), Tag(name="qux")}
    assert controller.current_image.tags == {Tag(name="foo"), Tag(name="qux")}

    view.update_tags.assert_not_called()
    view.update_current_image_tags.assert_not_called()
    view.reset_mock()


def test_set_tags(image_factory):
    model = Model()
    view = mock.MagicMock()
    controller = Controller(model=model)
    assert controller.tags == []

    image = image_factory('foo.jpg')
    model.images.add(image)

    controller._view = view

    controller.set_tags({Tag(name="a"), Tag(name="b")})
    assert controller.tags == [Tag(name="a"), Tag(name="b")]
    assert model.tags == {Tag(name="a"), Tag(name="b")}

    view.update_tags.assert_called_once()
    view.reset_mock()

    controller.set_tags({Tag(name="a"), Tag(name="b"), Tag(name="c")})
    assert controller.tags == [Tag(name="a"), Tag(name="b"), Tag(name="c")]
    assert model.tags == {Tag(name="a"), Tag(name="b"), Tag(name="c")}

    view.update_tags.assert_called_once()
    view.reset_mock()

    image.tags = {Tag(name="a"), Tag(name="b"), Tag(name="c")}

    controller.set_tags({Tag(name="a")})
    assert controller.tags == [Tag(name="a")]
    assert model.tags == {Tag(name="a")}

    view.update_tags.assert_called_once()
    view.reset_mock()

    assert image.tags == {Tag(name="a")}


def test_tags():
    controller = Controller(model=Model())
    assert controller.tags == []

    controller.add_tag(Tag(name="red"))
    assert controller.tags == [Tag(name="red")]

    controller.add_tag(Tag(name="blue"))
    controller.add_tag(Tag(name="green"))
    controller.add_tag(Tag(name="yellow"))

    assert controller.tags == [
        Tag(name="blue"),
        Tag(name="green"),
        Tag(name="red"),
        Tag(name="yellow"),
    ]


def test_view_model_reinitialized_on_load(basedir: pathlib.Path, model: Model):
    controller = Controller(model=model)

    controller.save(basedir / 'save.picpick')
    assert controller._view.model == model

    controller.load(basedir / 'save.picpick')
    assert controller._view.model != model


def test_load_empty_project(basedir: pathlib.Path):
    model = Model()
    controller = Controller(model=model)

    controller.save(basedir / 'save.picpick')
    controller.load(basedir / 'save.picpick')
    assert controller._model is not model

    assert controller.current_image is None
    assert controller.images == []
    assert controller.tags == []
