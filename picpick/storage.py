import pathlib
import pickle

from .model import Model


def save(destination: pathlib.Path, model: Model):
    assert len(set(image.path for image in model.images)) == len(model.images)
    assert all(image.tags.issubset(model.tags) for image in model.images)

    with destination.open('wb') as f:
        pickle.dump(model, f)


def load(source: pathlib.Path) -> Model:
    with source.open('rb') as f:
        return pickle.load(f)
