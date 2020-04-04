import pathlib
import shutil

from dataclasses import dataclass
from typing import List


@dataclass
class Output:
    path: pathlib.Path


class App:
    def __init__(
        self, input_images: List[pathlib.Path], output_dirs: List[pathlib.Path]
    ):
        assert len(input_images) > 0
        assert len(output_dirs) > 0

        self._input_images = input_images
        self._outputs = [Output(path=p) for p in output_dirs]
        self._assignments = {}

        self._current_input_image_index = 0

    @property
    def inputs(self) -> List[pathlib.Path]:
        return self._input_images

    @property
    def outputs(self) -> List[Output]:
        return self._outputs

    @property
    def current_image(self) -> pathlib.Path:
        return self._input_images[self._current_input_image_index]

    def assign_current_image_to(self, output: Output):
        assert output in self._outputs
        self._assignments[self.current_image] = output

    def select_image(self, path: pathlib.Path):
        assert path in self._input_images
        self._current_input_image_index = self._input_images.index(path)
        assert self.current_image == path

    def next_image(self):
        if self._current_input_image_index + 1 >= len(self._input_images):
            raise StopIteration
        self._current_input_image_index += 1

    def perform_assignments(self):
        for src, dst in self._assignments.items():
            shutil.move(str(src), str(dst))
