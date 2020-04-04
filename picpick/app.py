import pathlib
import shutil

from typing import List

from .types import InputImage, Output


class App:
    def __init__(
        self,
        input_images: List[pathlib.Path],
        output_dirs: List[pathlib.Path],
        mode: str = 'move',
    ):
        assert len(input_images) > 0
        assert len(output_dirs) > 0
        assert mode in ('move', 'copy')

        self._input_images = [InputImage(path=p) for p in input_images]
        self._outputs = [Output(path=p) for p in output_dirs]
        self._mode = mode

        self._assignments = {}

        self._current_input_image_index = 0

    @property
    def inputs(self) -> List[InputImage]:
        return self._input_images

    @property
    def outputs(self) -> List[Output]:
        return self._outputs

    @property
    def current_image(self) -> InputImage:
        return self._input_images[self._current_input_image_index]

    def assign_current_image_to(self, output: Output):
        assert output in self._outputs
        self._assignments[self.current_image] = output

    def select_image(self, image: InputImage):
        assert image in self._input_images
        self._current_input_image_index = self._input_images.index(image)
        assert self.current_image == image

    def next_image(self):
        if self._current_input_image_index + 1 >= len(self._input_images):
            raise StopIteration
        self._current_input_image_index += 1

    def perform_assignments(self):
        for src, dst in self._assignments.items():
            if self._mode == 'move':
                shutil.move(str(src.path), str(dst.path))
            elif self._mode == 'copy':
                shutil.copy(str(src.path), str(dst.path))
            else:
                raise NotImplementedError
