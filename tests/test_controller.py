import pathlib
import tkinter as tk

import pytest  # type: ignore

from picpick.controller import Controller
from picpick.model import Model


def test_current_image(model: Model):
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
