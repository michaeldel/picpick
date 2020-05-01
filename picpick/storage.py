import pathlib
import pickle

from typing import Optional, Tuple

from .model import Model


def _check_save_data_valid(model: Model, current_index: Optional[int]):
    if model.images == set():
        assert current_index is None
    else:
        assert current_index is not None
        assert 0 <= current_index < len(model.images)

    assert len(set(image.path for image in model.images)) == len(model.images)
    assert all(image.tags.issubset(model.tags) for image in model.images)


def save(destination: pathlib.Path, model: Model, current_index: Optional[int] = None):
    _check_save_data_valid(model, current_index)

    with destination.open('wb') as f:
        pickle.dump(model, f)
        pickle.dump(current_index, f)


def load(source: pathlib.Path) -> Tuple[Model, Optional[int]]:
    with source.open('rb') as f:
        model = pickle.load(f)
        current_index = pickle.load(f)

    _check_save_data_valid(model, current_index)
    return model, current_index
