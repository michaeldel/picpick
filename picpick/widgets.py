import tkinter as tk
import tkinter.ttk as ttk

from typing import Callable, List, Optional

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

    def set_image(self, image: Optional[model.Image]):
        self._image = Image.open(image.path) if image else Image.new('RGB', (0, 0))
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

    def select(self, image: Optional[model.Image]):
        # prevent infinite callback loop
        if image == self.selected:
            return

        if image is None:
            self._tree.selection_set(())
            return

        assert image in self._images_index.values()

        iid = self._images_index.inverse[image]
        self._tree.selection_set((iid,))


class TagList(tk.Frame):
    def __init__(self, master, callback: Callable):
        super().__init__(master=master)
        label = tk.Label(master=self, text="Tags")
        label.pack()

        self._tags: List[model.Tag] = []
        self._checkboxes: List[tk.Checkbutton] = []
        self._checked_variables: List[tk.BooleanVar] = []

        self._callback = callback

        self.set_current_image(image=None)

    def _reset(self):
        for checkbox in self._checkboxes:
            checkbox.destroy()

        self._checkboxes = []
        self._checked_variables = []

    def set_tags(self, tags: List[model.Tag]):
        self._reset()

        for i, tag in enumerate(tags):
            variable = tk.BooleanVar(value=False)

            shortcut: Optional[int]

            if i < 9:
                shortcut = i + 1
                text = f"[{shortcut}] {tag.name}"
            else:
                shortcut = None
                text = tag.name

            def command(tag=tag, variable=variable):
                self._callback(tag, variable.get())

            checkbox = tk.Checkbutton(
                master=self, text=text, anchor=tk.W, variable=variable, command=command
            )
            checkbox.pack(fill=tk.X)

            self._checkboxes.append(checkbox)
            self._checked_variables.append(variable)

        self._tags = tags
        self.set_current_image(self._current_image)

    def set_current_image(self, image: Optional[model.Image]):
        assert image is None or image.tags.issubset(self._tags)

        state = tk.DISABLED if image is None else tk.NORMAL
        for checkbox in self._checkboxes:
            checkbox.config(state=state)

        for tag, variable in zip(self._tags, self._checked_variables):
            variable.set(tag in image.tags if image is not None else False)

        self._current_image = image
