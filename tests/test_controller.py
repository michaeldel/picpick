import pathlib
import tkinter as tk

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


def test_add_image(image_factory):
    view = mock.MagicMock()
    controller = Controller(model=Model())
    controller._view = view
    assert not hasattr(controller, '_current_image')

    # adding the first image should automatically set it as current
    controller.add_image(image_factory('foo.jpg'))
    assert controller._current_image.path.name == 'foo.jpg'
    assert [image.path.name for image in controller.images] == ['foo.jpg']

    view.file_list.set_items.assert_called_once_with(controller.images)
    view.reset_mock()

    controller.add_image(image_factory('bar.jpg'))
    assert controller._current_image.path.name == 'foo.jpg'
    assert [image.path.name for image in controller.images] == ['bar.jpg', 'foo.jpg']

    view.file_list.set_items.assert_called_once_with(controller.images)
    view.reset_mock()

    # adding the same image twice should fail
    with pytest.raises(
        Controller.ImageAlreadyPresent, match="foo.jpg is already present"
    ):
        controller.add_image(image_factory('foo.jpg'))
    assert [image.path.name for image in controller.images] == ['bar.jpg', 'foo.jpg']

    view.file_list.set_items.assert_not_called()
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

    view.tag_list.set_tags.assert_called_once_with([Tag(name="foo")])
    view.reset_mock()

    controller.add_tag(Tag(name="bar"))

    view.tag_list.set_tags.assert_called_once_with([Tag(name="bar"), Tag(name="foo")])
    view.reset_mock()

    assert controller.tags == [Tag(name="bar"), Tag(name="foo")]


def test_delete_tag(image_factory):
    model = Model()
    image = image_factory("foo.jpg")

    model.tags = {Tag(name="foo"), Tag(name="bar")}
    model.images = {image}

    image.tags = {Tag(name="foo"), Tag(name="bar")}

    controller = Controller(model=model)

    assert controller.tags == [Tag(name="bar"), Tag(name="foo")]

    view = mock.MagicMock()
    controller._view = view

    controller.delete_tag(Tag(name="foo"))
    assert controller.tags == [Tag(name="bar")]

    assert model.tags == {Tag(name="bar")}
    assert image.tags == {Tag(name="bar")}

    view.tag_list.set_tags.assert_called_once_with([Tag(name="bar")])
    view.reset_mock()

    controller.delete_tag(Tag(name="bar"))
    assert controller.tags == []

    assert model.tags == set()
    assert image.tags == set()

    view.tag_list.set_tags.assert_called_once_with([])
    view.reset_mock()


def test_update_tag(image_factory):
    model = Model()

    image = image_factory("foo.jpg")

    model.tags = {Tag(name="foo"), Tag(name="bar")}
    model.images = {image}

    image.tags = {Tag(name="foo"), Tag(name="bar")}

    controller = Controller(model=model)

    view = mock.MagicMock()
    controller._view = view

    controller.update_tag(Tag(name="bar"), Tag(name="qux"))
    assert controller.tags == [Tag(name="foo"), Tag(name="qux")]

    assert model.tags == {Tag(name="foo"), Tag(name="qux")}
    assert image.tags == {Tag(name="foo"), Tag(name="qux")}

    view.tag_list.set_tags.assert_called_once_with([Tag(name="foo"), Tag(name="qux")])
    view.reset_mock()

    with pytest.raises(
        Controller.TagAlreadyPresent, match="\"qux\" tag is already present"
    ):
        controller.update_tag(Tag(name="foo"), Tag(name="qux"))

    assert controller.tags == [Tag(name="foo"), Tag(name="qux")]

    assert model.tags == {Tag(name="foo"), Tag(name="qux")}
    assert image.tags == {Tag(name="foo"), Tag(name="qux")}

    view.tag_list.set_tags.assert_not_called()
    view.reset_mock()


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


def test_view_reinitialized_on_load(basedir: pathlib.Path, model: Model):
    controller = Controller(model=model)

    controller.save(basedir / 'save.picpick')

    previous = controller._view
    assert previous.winfo_exists()

    controller.load(basedir / 'save.picpick')

    assert controller._view is not previous
    assert controller._view.winfo_exists()

    # previous window must have been destroyed
    with pytest.raises(tk.TclError, match=r'.* application has been destroyed$'):
        previous.winfo_exists()


def test_load_empty_project(basedir: pathlib.Path):
    model = Model()
    controller = Controller(model=model)

    controller.save(basedir / 'save.picpick')
    controller.load(basedir / 'save.picpick')
    assert controller._model is not model

    assert controller.current_image is None
    assert controller.images == []
    assert controller.tags == []


def test_mark_view_saved_and_unsaved(basedir: pathlib.Path, model: Model):
    controller = Controller(model=model)
    view = mock.MagicMock()
    controller._view = view

    controller.save(basedir / 'save.picpick')
    view.mark_saved.assert_called_once_with()
    view.reset_mock()

    controller.save_current()
    view.mark_saved.assert_called_once_with()
    view.reset_mock()

    # setting to new image should mark unsaved
    controller.set_current_image(controller.images[1])
    view.mark_unsaved.assert_called_once_with()
    view.reset_mock()

    controller.save_current()
    view.mark_saved.assert_called_once_with()
    view.reset_mock()

    # setting to current image should not mark unsaved
    controller.set_current_image(controller._current_image)
    view.mark_unsaved.assert_not_called()

    # tagging an image should mark unsaved
    tag = controller.tags[0]

    controller.tag_current_image(tag)
    view.mark_unsaved.assert_called_once_with()
    view.reset_mock()

    controller.save_current()
    view.mark_saved.assert_called_once_with()
    view.reset_mock()

    # untagging an image should mark unsaved
    controller.untag_current_image(tag)
    view.mark_unsaved.assert_called_once_with()
    view.reset_mock()

    controller.save_current()
    view.mark_saved.assert_called_once_with()
    view.reset_mock()
