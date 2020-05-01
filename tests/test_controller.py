import pathlib
import tkinter as tk

from unittest import mock

import pytest  # type: ignore

from picpick.controller import Controller
from picpick.model import Model


def test_current_image(model: Model):
    controller = Controller(model=Model())
    assert controller.current_image is None

    controller = Controller(model=model)

    assert controller.current_image.path.name == 'one.jpg'
    controller.set_current_image(controller.images[1])
    assert controller.current_image.path.name == 'three.jpg'
    controller.set_current_image(controller.images[2])
    assert controller.current_image.path.name == 'two.jpg'
    controller.set_current_image(controller.images[0])
    assert controller.current_image.path.name == 'one.jpg'


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
    controller.set_current_image(controller.current_image)
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
