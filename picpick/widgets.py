import tkinter as tk
import tkinter.ttk as ttk

from typing import List

from PIL import Image, ImageTk

from .types import InputImage

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

    def set_image(self, image: Image):
        self._image = image
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
        resized = self._image.copy()
        resized.thumbnail((width, height), Image.ANTIALIAS)

        self._set_canvas_image(resized)


class FileList(tk.Frame):
    def __init__(self, master, inputs: List[InputImage]):
        super().__init__(master=master)

        tree = ttk.Treeview(master=self, selectmode='browse')
        scroll = ttk.Scrollbar(master=self, orient=tk.VERTICAL)

        tree.configure(yscrollcommand=scroll.set)
        scroll.configure(command=tree.yview)

        tree.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        scroll.pack(fill=tk.Y, side=tk.RIGHT, expand=True)

        tree.heading('#0', text="File")
        tree.column('#0', width=200)

        ROOT = ''

        for i, input in enumerate(inputs):
            tag = str(i)
            text = input.path.name
            tree.insert(ROOT, tk.END, text=text, tags=(tag,))

        tree.bind(
            '<<TreeviewSelect>>', lambda _: self.event_generate('<<FileListSelect>>')
        )

        self._tree = tree
        self._inputs = inputs

    def selection(self) -> InputImage:
        tree_selection = self._tree.selection()
        assert isinstance(tree_selection, tuple) and len(tree_selection) == 1

        # TODO: refactor this properly
        index = self._tree.item(tree_selection[0])['tags'][0]
        return self._inputs[index]

    def selection_set(self, index: int):
        item = self._tree.get_children()[index]
        self._tree.selection_set(item)
