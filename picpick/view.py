import pathlib
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog
from typing import Optional, Set

import PIL

from . import types as models, widgets
from .controller import Controller


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.controller = Controller()

        self.geometry('928x640')
        self.attributes('-type', 'dialog')  # make window floating on i3wm

        self.config(menu=Menu(master=self))

        pw = ttk.PanedWindow(master=self, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        image_display = widgets.ImageDisplay(master=pw)

        ppw = ttk.PanedWindow(master=pw, orient=tk.VERTICAL)

        file_list = FileList(master=ppw, controller=self.controller)
        tag_list = TagList(master=ppw, controller=self.controller)

        file_list.bind('<<FileListSelect>>', lambda _: self.refresh())

        ppw.add(file_list)
        ppw.add(tag_list)

        pw.add(ppw)
        # pw.add(file_list)
        pw.add(image_display)

        self._file_list = file_list
        self._tag_list = tag_list
        self._image_display = image_display

        self.controller.add_tags(
            [
                models.Tag(name=name)
                for name in (
                    'red',
                    'blue',
                    'green',
                    'yellow',
                    'orange',
                    'pink',
                    'purple',
                    'white',
                    'black',
                    'grey',
                    'crimson',
                )
            ]
        )
        tag_list.refresh(None, self.controller.tags)

    def refresh(self):
        self._file_list.refresh(self.controller._current_image_index)

        path = self.controller.current_image.path
        self._image_display.set_image(PIL.Image.open(path))

        self._tag_list.refresh(self.controller.current_image, self.controller.tags)


class FileList(tk.Frame):
    def __init__(self, master, controller: Controller):
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

        tree.bind('<<TreeviewSelect>>', lambda _: self.refresh())

        self._tree = tree
        self._controller = controller

    def selection(self) -> models.Image:
        tree_selection = self._tree.selection()
        assert isinstance(tree_selection, tuple) and len(tree_selection) == 1

        # TODO: refactor this properly
        index = self._tree.item(tree_selection[0])['tags'][0]
        return self._controller._images[index]

    def selection_set(self, index: int):
        item = self._tree.get_children()[index]
        self._tree.selection_set(item)

    def refresh(self, selected_index: Optional[int] = None):
        print("refresh")
        # clear to prevent duplicates
        self._tree.delete(*self._tree.get_children())

        ROOT = ''
        items = list(enumerate(p.name for p in self._controller.images_paths))

        for tag, text in items:
            self._tree.insert(ROOT, tk.END, text=text, tags=(tag,))

        if selected_index is not None:
            self.selection_set(selected_index)


class TagList(tk.Frame):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)
        label = tk.Label(master=self, text="Tags")
        label.pack()

        self._controller = controller
        self._checkboxes = []

        self.refresh(None, set())

    def refresh(self, image: Optional[models.Image], tags: Set[models.Tag]):
        assert image is None or image.tags.issubset(tags)

        # clear previous items
        for checkbox in self._checkboxes:
            checkbox.destroy()

        for tag in sorted(tags, key=lambda t: t.name):
            text = tag.name

            var = tk.BooleanVar(master=self)
            var.set(False if image is None else tag in image.tags)

            # https://stackoverflow.com/a/3431699/1812262
            def command(tag=tag, var=var):
                if var.get():
                    self._controller.tag_image(image, tag)
                else:
                    self._controller.untag_image(image, tag)

            checkbox = tk.Checkbutton(
                master=self,
                text=text,
                anchor=tk.W,
                variable=var,
                command=command,
                state=tk.DISABLED if image is None else tk.NORMAL,
            )
            checkbox.pack(fill=tk.X)
            self._checkboxes.append(checkbox)


class Menu(tk.Menu):
    def __init__(self, master=None):
        super().__init__(master=master)

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open...", command=self._open, accelerator="Ctrl+O")
        file_menu.add_command(label="Add images...", command=self._add_images)
        file_menu.add_command(
            label="Save as...", command=self._save, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_command(label="Exit", command=master.quit, accelerator="Ctrl+Q")

        self.add_cascade(label="File", menu=file_menu)

        master.bind_all('<Control-o>', lambda _: self._open())
        master.bind_all('<Control-Shift-S>', lambda _: self._save())
        master.bind_all('<Control-q>', lambda _: master.quit())  # TODO: add confirm

    def _add_images(self):
        filenames = filedialog.askopenfilenames(
            filetypes=(
                (
                    "Image file",
                    '.jpg .jpeg .png .bmp .gif .eps .tiff .ico .ppm .pgm .pbm',
                ),
            )
        )
        if filenames == () or filenames == '':
            return

        assert isinstance(filenames, tuple)
        self.master.controller.add_images(map(pathlib.Path, filenames))
        self.master.refresh()

    def _open(self):
        filename = filedialog.askopenfilename(
            filetypes=(("picpick savefile", '.picpick'),)
        )
        if filename == () or filename == '':
            return

        path = pathlib.Path(filename)
        self.master.controller.load(path)
        self.master.refresh()

    def _save(self):
        filename = filedialog.asksaveasfilename(
            filetypes=(("picpick savefile", '.picpick'),)
        )
        if filename == () or filename == '':
            return

        path = pathlib.Path(filename)
        self.master.controller.save(path)
