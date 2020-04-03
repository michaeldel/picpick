import pathlib
import tkinter as tk

from typing import Callable, List

from PIL import Image

from . import widgets


class MainWindow(tk.Tk):
    def __init__(
        self, input_paths: List[pathlib.Path], output_paths: List[pathlib.Path]
    ):
        assert len(input_paths) > 0
        assert len(output_paths) > 0

        self._input_paths = input_paths

        super().__init__()
        self.geometry('720x480')
        self.attributes('-type', 'dialog')  # make window floating on i3wm

        self._setup_paths_listbox()
        self._setup_image_display()
        self._setup_picking_buttons(output_paths)

        self._to_move = {}
        self._current_input_path_index = 0
        self.select_image(self._input_paths[self._current_input_path_index])

    def select_image(self, path: pathlib.Path):
        self._image_display.set_image(Image.open(path))

    def _setup_paths_listbox(self):
        paths_listbox = tk.Listbox(master=self, width=50)
        paths_listbox.insert(tk.END, *self._input_paths)

        def select(event: tk.Event):
            widget = event.widget
            assert isinstance(widget, tk.Listbox)
            selection = widget.curselection()
            assert isinstance(selection, tuple) and len(selection) == 1

            self.select_image(pathlib.Path(widget.get(selection[0])))

        paths_listbox.bind('<<ListboxSelect>>', select)
        paths_listbox.pack(fill=tk.BOTH, side=tk.LEFT)

    def _setup_image_display(self):
        self._image_display = widgets.ImageDisplay(master=self)
        self._image_display.pack(fill=tk.BOTH, expand=True)

    def _setup_picking_buttons(self, output_paths: List[pathlib.Path]):
        frame = tk.Frame(master=self, bg='red')
        frame.pack(fill=tk.X)

        def mark_to_move(output_path: pathlib.Path) -> Callable[[None], None]:
            def inner():
                current_input_path = self._input_paths[self._current_input_path_index]
                self._to_move[current_input_path] = output_path
                self._current_input_path_index += 1

                if self._current_input_path_index < len(self._input_paths):
                    self.select_image(self._input_paths[self._current_input_path_index])
                else:
                    print(self._to_move)

            return inner

        for output_path in output_paths:
            button = tk.Button(
                master=frame, text=output_path, command=mark_to_move(output_path),
            )
            button.pack(fill=tk.X, expand=True, side=tk.LEFT)

    def run(self):
        self.mainloop()
