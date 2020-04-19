import pathlib
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog
from typing import List, Tuple

from . import types as models
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

        file_list = FileList(master=pw)
        file_list.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self._file_list = file_list

    def refresh(self):
        tag_text_pairs = list(enumerate(p.name for p in self.controller.images_paths))
        self._file_list.refresh(tag_text_pairs, self.controller._current_image_index)


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

        tree.bind(
            '<<TreeviewSelect>>', lambda _: self.event_generate('<<FileListSelect>>')
        )

        self._tree = tree

    def selection(self) -> models.Image:
        tree_selection = self._tree.selection()
        assert isinstance(tree_selection, tuple) and len(tree_selection) == 1

        # TODO: refactor this properly
        index = self._tree.item(tree_selection[0])['tags'][0]
        return self.master.controller._images[index]

    def selection_set(self, index: int):
        item = self._tree.get_children()[index]
        self._tree.selection_set(item)

    def refresh(self, tag_text_pairs: List[Tuple[int, str]], selected_index: int):
        # clear to prevent duplicates
        self._tree.delete(*self._tree.get_children())

        ROOT = ''
        for tag, text in tag_text_pairs:
            self._tree.insert(ROOT, tk.END, text=text, tags=(tag,))

        self.selection_set(selected_index)


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
