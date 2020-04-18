import pathlib

from typing import Iterable, List, Set

from . import storage
from .types import Image, Tag


class Controller:
    def __init__(self):
        self._images = []
        self._tags = set()
        self._current_image_index = 0

    def add_images(self, paths: Iterable[str]):
        already_present = set(image.path for image in self._images)
        new_images = [Image(path=p) for p in paths if p not in already_present]
        self._images.extend(new_images)

    def add_tags(self, tags: List[Tag]):
        self._tags.update(tags)

    def load(self, source: pathlib.Path):
        self._images, self._tags = storage.load(source)
        self._current_image_index = 0

    def save(self, to: pathlib.Path):
        storage.save(to, images=self._images, tags=self._tags)

    def tag_image(self, image: Image, tag: Tag):
        assert image in self._images
        assert tag in self._tags

        image.tags.add(tag)

    def untag_image(self, image: Image, tag: Tag):
        assert image in self._images
        assert tag in self._tags

        assert tag in image.tags

        image.tags.remove(tag)

    @property
    def current_image(self) -> pathlib.Path:
        return self._images[self._current_image_index]

    @property
    def images_paths(self) -> List[pathlib.Path]:
        paths = [image.path for image in self._images]
        return list(sorted(paths))

    @property
    def tags(self) -> Set[Tag]:
        return self._tags
