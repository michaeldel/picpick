import pathlib
import pickle

from typing import Tuple

from .model import Model


def save(destination: pathlib.Path, model: Model, current_index: int):
    assert len(model.images) > 0 and len(model.tags) > 0
    assert len(set(image.path for image in model.images)) == len(model.images)
    assert all(image.tags.issubset(model.tags) for image in model.images)
    assert 0 <= current_index < len(model.images)

    with destination.open('wb') as f:
        pickle.dump(model, f)
        pickle.dump(current_index, f)


def load(source: pathlib.Path) -> Tuple[Model, int]:
    with source.open('rb') as f:
        model = pickle.load(f)
        current_index = pickle.load(f)

    assert len(model.images) > 0 and len(model.tags) > 0
    assert all(image.tags.issubset(model.tags) for image in model.images)
    assert 0 <= current_index < len(model.images)

    return model, current_index
