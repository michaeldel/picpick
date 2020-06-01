import pathlib

from typing import List, Optional, Set

from . import storage
from .model import Image, Model, Tag
from .view import View


class Controller:
    def __init__(self, model: Model):
        # required to comply with static typing
        self._view = View(controller=self)
        self._init(model=model)

    def _init(self, model: Model):
        self._model = model
        self._view.model = model

        if len(model.tags) > 0:
            self._view.update_tags()

        if len(model.images) > 0:
            self._view.update_images()
            self.set_current_image(self.images[0])

    def add_image(self, image: Image):
        assert image not in self.images  # TODO: performance can be improved
        assert image.tags == set()

        if image.path in [i.path for i in self.images]:
            raise self.__class__.ImageAlreadyPresent(image)

        self._model.images.add(image)

        self._view.update_images()

        if self.current_image is None:
            self.set_current_image(image)

    def add_tag(self, tag: Tag):
        assert tag not in self._model.tags

        self._model.tags.add(tag)
        self._view.update_tags()

    def delete_tag(self, tag: Tag):
        self._model.tags.remove(tag)

        in_current_image = (
            tag in self.current_image.tags if self.current_image else False
        )

        for image in self._model.images:
            image.tags.discard(tag)

        self._view.update_tags()
        if in_current_image:
            self._view.update_current_image_tags()

    def update_tag(self, old: Tag, new: Tag):
        assert old in self._model.tags

        if new in self._model.tags:
            raise self.__class__.TagAlreadyPresent(new)

        self._model.tags.remove(old)
        self._model.tags.add(new)

        for image in self._model.images:
            if old in image.tags:
                image.tags.remove(old)
                image.tags.add(new)

        self._view.update_tags()

    def set_tags(self, tags: Set[Tag]):
        self._model.tags = tags

        for image in self._model.images:
            image.tags.intersection_update(tags)

        self._view.update_tags()

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

    def set_current_image(self, image: Optional[Image]):
        assert image is None or image in self._model.images

        if self.current_image is image:
            return

        self._current_image: Image

        if image is None:
            del self._current_image
        else:
            self._current_image = image

        self._view.update_current_image()

    def tag_current_image(self, tag: Tag):
        assert tag in self._model.tags
        assert tag not in self._current_image.tags

        self._current_image.tags.add(tag)
        self._view.update_current_image_tags()

    def untag_current_image(self, tag: Tag):
        assert tag in self._model.tags
        assert tag in self._current_image.tags

        self._current_image.tags.remove(tag)
        self._view.update_current_image_tags()

    def set_current_image_tag(self, tag: Tag, present: bool):
        if present:
            return self.tag_current_image(tag)
        return self.untag_current_image(tag)

    def save_current(self):
        assert hasattr(self, 'last_save_path')
        self.save(self.last_save_path)

    def save(self, to: pathlib.Path):
        current_index: Optional[int]

        try:
            current_index = self.images.index(self._current_image)
        except AttributeError:
            current_index = None

        storage.save(to, self._model, current_index=current_index)

        self.last_save_path = to
        self._view.mark_saved(to.name)

    def load(self, source: pathlib.Path):
        model, current_index = storage.load(source)

        self._init(model=model)

        if current_index is not None:
            self.set_current_image(self.images[current_index])
        self._view.mark_saved(source.name)

    def run(self):
        self._view.run()

    class ImageAlreadyPresent(Exception):
        def __init__(self, image: Image):
            super().__init__(f"{image.path.name} is already present")

    class TagAlreadyPresent(Exception):
        def __init__(self, tag: Tag):
            super().__init__(f"\"{tag.name}\" tag is already present")
