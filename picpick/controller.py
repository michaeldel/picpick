import pathlib

from typing import List, Optional

from . import storage
from .model import Image, Model, Tag
from .view import MainWindow


class Controller:
    def __init__(self, model: Model):
        # required to comply with static typing
        self._init(model=model)

    def _init(self, model: Model):
        self._model = model
        self._view: MainWindow

        if hasattr(self, '_view'):
            self._view.destroy()

        self._view = MainWindow(controller=self)

        if len(model.images) > 0:
            self.set_current_image(self.images[0])

    def add_image(self, image: Image):
        assert image not in self.images  # TODO: performance can be improved
        assert image.tags == set()

        if image.path in [i.path for i in self.images]:
            raise self.__class__.ImageAlreadyPresent(image)

        self._model.images.add(image)

        self._view.file_list.set_items(self.images)

        if self.current_image is None:
            self.set_current_image(image)

    @property
    def images(self) -> List[Image]:
        return sorted(self._model.images, key=lambda image: image.path.name)

    @property
    def tags(self) -> List[Tag]:
        return sorted(self._model.tags, key=lambda tag: tag.name)

    @property
    def current_image(self) -> Optional[Image]:
        try:
            return self._current_image
        except AttributeError:
            return None

    def set_current_image(self, image: Image):
        assert image in self._model.images

        if getattr(self, 'current_image', None) is image:
            return

        self._current_image = image

        self._view.tag_list.set_current_image(image)
        self._view.file_list.set_current_image(image)
        self._view.image_display.set_image(image)
        self._view.mark_unsaved()

    def tag_current_image(self, tag: Tag):
        assert tag in self._model.tags
        assert tag not in self._current_image.tags

        self._current_image.tags.add(tag)
        self._view.mark_unsaved()

    def untag_current_image(self, tag: Tag):
        assert tag in self._model.tags
        assert tag in self._current_image.tags

        self._current_image.tags.remove(tag)
        self._view.mark_unsaved()

    def save_current(self):
        self.save(self.last_save_path)

    def save(self, to: pathlib.Path):
        current_index: Optional[int]

        try:
            current_index = self.images.index(self._current_image)
        except AttributeError:
            current_index = None

        storage.save(to, self._model, current_index=current_index)

        self.last_save_path = to
        self._view.mark_saved()

    def load(self, source: pathlib.Path):
        model, current_index = storage.load(source)

        self._init(model=model)

        if current_index is not None:
            self.set_current_image(self.images[current_index])
        self._view.mark_saved()

    def run(self):
        self._view.mainloop()

    class ImageAlreadyPresent(Exception):
        def __init__(self, image: Image):
            super().__init__(f"{image.path.name} is already present")
