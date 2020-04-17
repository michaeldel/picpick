import pathlib
import pickle

from typing import Set, Tuple

from .types import Image, Tag


def save(destination: pathlib.Path, images: Set[Image], tags: Set[Tag]):
    assert len(set(image.path for image in images)) == len(images)
    assert all(image.tags.issubset(tags) for image in images)

    with destination.open('wb') as f:
        pickle.dump(images, f)
        pickle.dump(tags, f)


def load(source: pathlib.Path) -> Tuple[Set[Image], Set[Tag]]:
    with source.open('rb') as f:
        images = pickle.load(f)
        tags = pickle.load(f)
    return images, tags
