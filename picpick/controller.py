import pathlib
import tkinter as tk

from typing import List

from . import storage
from .model import Image, Model, Tag
from .view import MainWindow


class NoImageError(Exception):
    pass


class Controller:
    def __init__(self, model: Model, view: MainWindow):
        self._model = model
        self._view = view

        current_image_index = tk.IntVar(master=view)

        def on_current_image_index_update():
            for tag, prop in self._tag_properties.items():
                if tag in self.current_image.tags:
                    prop.set(False)
                else:
                    prop.set(True)

            view.image_display.set_image_from_path(self.current_image.path)
            view.file_list.selection_set(index=current_image_index.get())

        current_image_index.trace_add('write', on_current_image_index_update)

        self._current_image_index = current_image_index
        self._current_image_tags = set()

    def add_tag(self, tag: Tag):
        assert tag not in self._tags
        assert tag not in self._tags_properties.keys()

        checked = tk.BooleanVar(value=False)

        def on_tag_check(tag: Tag):
            if checked.get():
                assert tag not in self.current_image.tags
                self.current_image.tags.add(tag)
            else:
                self.current_image.tags.remove(tag)

        checked.trace_add('write', lambda: on_tag_check(tag))

        self._tags.add(tag)
        self._tags_properties[tag] = checked

        self._view.tag_list.update_tags(self._tags_properties)

    def remove_tag(self, tag: Tag):
        assert tag in self._tags
        assert tag in self._tags_properties.keys()

        self._tags.remove(tag)
        self._tags_properties.pop(tag)

        self._view.tag_list.update_tags(self._tags_properties)

    def add_tags(self, tags: List[Tag]):
        # TODO: optimize performance
        for tag in tags:
            self.add_tag(tag)

    def load(self, source: pathlib.Path):
        model = storage.load(source)
        view = self._view

        self.__init__(model=model, view=view)

    def save(self, to: pathlib.Path):
        storage.save(to, model=self._model)

    @property
    def current_image(self) -> Image:
        return self._images[self._current_image_index.get()]
