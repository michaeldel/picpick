import pathlib
import tkinter as tk

from typing import List

from PIL import Image

from . import widgets


class MainWindow(tk.Tk):
    def __init__(self, paths: List[pathlib.Path]):
        assert len(paths) > 0
        self._paths = paths

        super().__init__()
        self.geometry('720x480')
        self.attributes('-type', 'dialog')  # make window floating on i3wm

        self._setup_paths_listbox()
        self._setup_image_display()

        self.select_image(self._paths[0])

    def select_image(self, path: pathlib.Path):
        assert path in self._paths
        self._image_display.set_image(Image.open(path))

    def _setup_paths_listbox(self):
        paths_listbox = tk.Listbox(master=self)
        paths_listbox.insert(tk.END, *self._paths)

        def select(event: tk.Event):
            widget = event.widget
            assert isinstance(widget, tk.Listbox)
            selection = widget.curselection()
            assert isinstance(selection, tuple) and len(selection) == 1

            self.select_image(pathlib.Path(widget.get(selection[0])))

        paths_listbox.bind('<<ListboxSelect>>', select)
        paths_listbox.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    def _setup_image_display(self):
        self._image_display = widgets.ImageDisplay(master=self)
        self._image_display.pack(fill=tk.BOTH, expand=True)

    def run(self):
        self.mainloop()
