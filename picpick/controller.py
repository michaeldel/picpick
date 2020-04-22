import pathlib

from typing import List

from . import storage
from .model import Image, Model, Tag
from .view import MainWindow


class NoImageError(Exception):
    pass


class Controller:
    def __init__(self, model: Model):
        assert len(model.images) > 0
        assert len(model.tags) > 0

        self._model = model
        self._view = MainWindow(controller=self)

        self.set_current_image(self.images[0])

    @property
    def images(self) -> List[Image]:
        return sorted(self._model.images, key=lambda image: image.path.name)

    @property
    def tags(self) -> List[Tag]:
        return sorted(self._model.tags, key=lambda tag: tag.name)

    @property
    def current_image(self) -> Image:
        return self._current_image

    def set_current_image(self, image: Image):
        assert image in self._model.images
        self._current_image = image

        self._view.tag_list.set_current_image(image)
        self._view.file_list.set_current_image(image)
        self._view.image_display.set_image(image)

    def tag_current_image(self, tag: Tag):
        assert tag in self._model.tags
        assert tag not in self.current_image.tags

        self.current_image.tags.add(tag)

    def untag_current_image(self, tag: Tag):
        assert tag in self._model.tags
        assert tag in self.current_image.tags

        self.current_image.tags.remove(tag)

    def save(self, to: pathlib.Path):
        current_index = self.images.index(self.current_image)
        storage.save(to, self._model, current_index=current_index)

    def load(self, source: pathlib.Path):
        model, current_index = storage.load(source)

        self.__init__(model=model)
        self.set_current_image(self.images[current_index])

    def run(self):
        self._view.mainloop()
