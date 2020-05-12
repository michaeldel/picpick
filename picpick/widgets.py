import tkinter as tk
import tkinter.ttk as ttk

from typing import List, Optional

from bidict import bidict  # type: ignore
from PIL import Image, ImageTk  # type: ignore

from . import model

MIN_WIDTH = 128
MIN_HEIGHT = 128


class ImageDisplay(tk.Canvas):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.configure(background='black')

        def configure(e: tk.Event):
            if self._image is not None:
                self._resize()

        self.bind('<Configure>', configure)
        self._image = None

    def set_image(self, image: model.Image):
        self._image = Image.open(image.path)
        self._resize()

    def _set_canvas_image(self, image: Image):
        # keep stored as object attribute to prevent garbage collection
        self._photo = ImageTk.PhotoImage(image)

        width = self.winfo_width()
        height = self.winfo_height()

        if not hasattr(self, '_canvas_image'):
            self._canvas_image = self.create_image(
                width / 2, height / 2, anchor=tk.CENTER, image=self._photo
            )
        else:
            self.itemconfig(self._canvas_image, image=self._photo)
            self.coords(self._canvas_image, width / 2, height / 2)

    def _resize(self):
        width = self.winfo_width()
        height = self.winfo_height()

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return

        # use thumbnail to maintain aspect ratio
        resized = self._image.copy()  # type: ignore
        resized.thumbnail((width, height), Image.ANTIALIAS)

        self._set_canvas_image(resized)


class FileList(tk.Frame):
    def __init__(self, master):
        super().__init__(master=master)

        tree = ttk.Treeview(master=self, selectmode='browse')
        scroll = ttk.Scrollbar(master=self, orient=tk.VERTICAL)

        tree.configure(yscrollcommand=scroll.set)
        scroll.configure(command=tree.yview)

        # pack in this order to prevent scrollbar from disappearing when
        # reducing widget size
        scroll.pack(fill=tk.Y, side=tk.RIGHT)
        tree.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        tree.heading('#0', text="File")

        tree.bind('<<TreeviewSelect>>', lambda _: self._on_select())

        self._tree = tree

    def _on_select(self):
        self.event_generate('<<FileListSelect>>')

    def _reset(self):
        self._tree.delete(*self._tree.get_children())

    def set_images(self, images: List[model.Image]):
        self._reset()

        index = bidict()

        ROOT = ''
        for image in images:
            text = image.path.name
            iid = self._tree.insert(ROOT, tk.END, text=text)
            index[iid] = image

        self._images_index = index

    @property
    def selected(self) -> Optional[model.Image]:
        selection = self._tree.selection()

        if selection == ():
            return None

        assert isinstance(selection, tuple) and len(selection) == 1
        return self._images_index[selection[0]]

    def select(self, image: model.Image):
        assert image in self._images_index.values()

        # prevent infinite callback loop
        if image == self.selected:
            return

        iid = self._images_index.inverse[image]
        self._tree.selection_set((iid,))
