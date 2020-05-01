from __future__ import annotations

import pathlib
import sys
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog
from typing import List, Optional, TYPE_CHECKING

from . import model, widgets

if TYPE_CHECKING:
    from .controller import Controller


class MainWindow(tk.Tk):
    def __init__(self, controller: Controller):
        super().__init__()

        self.title("PicPick")
        self.geometry('928x640')

        if sys.platform == 'linux':
            self.attributes('-type', 'dialog')  # make window floating on i3wm

        menu = Menu(master=self, controller=controller)
        self.config(menu=menu)

        pw = ttk.PanedWindow(master=self, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        image_display = widgets.ImageDisplay(master=pw)

        sidebar = ttk.PanedWindow(master=pw, orient=tk.VERTICAL)

        file_list = FileList(master=sidebar, controller=controller)
        tag_list = TagList(master=sidebar, controller=controller)

        sidebar.add(file_list)
        sidebar.add(tag_list)

        pw.add(sidebar)
        pw.add(image_display)

        self._menu = menu

        self.file_list = file_list
        self.tag_list = tag_list
        self.image_display = image_display

    def mark_unsaved(self):
        self.title("PicPick *")

    def mark_saved(self):
        self.title("PicPick")
        self._menu.enable_save()


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

        tree.bind('<<TreeviewSelect>>', lambda _: self._on_select())

        self._tree = tree
        self._controller = controller

        self._set_items(controller.images)

    def set_current_image(self, image: model.Image):
        # avoid infinite event callback loop
        if image == self._current_selected_image:
            return

        key = self._images_index.index(image)
        for child in self._tree.get_children():
            tags = self._tree.item(child)['tags']
            if tags == [key]:
                break
        else:
            raise IndexError

        self._tree.selection_set((child,))

    def _reset(self):
        self._tree.delete(*self._tree.get_children())

    def _set_items(self, images: List[model.Image]):
        assert len(images) > 0
        self._reset()

        ROOT = ''
        for i, image in enumerate(images):
            text = image.path.name
            tag = str(i)
            self._tree.insert(ROOT, tk.END, text=text, tags=(tag,))
        self._images_index = images

    @property
    def _current_selected_image(self) -> Optional[model.Image]:
        tree_selection = self._tree.selection()

        if tree_selection == ():  # if no image selected
            return None

        assert isinstance(tree_selection, tuple) and len(tree_selection) == 1

        key = self._tree.item(tree_selection[0])['tags'][0]
        return self._images_index[key]

    def _on_select(self):
        image = self._current_selected_image
        self._controller.set_current_image(image)


class TagList(tk.Frame):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)
        label = tk.Label(master=self, text="Tags")
        label.pack()

        self._checkboxes: List[tk.Checkbutton] = []
        self._checked_variables: List[tk.BooleanVar] = []

        self._controller = controller

        self._set_tags(controller.tags)

    def set_current_image(self, image: model.Image):
        assert image.tags.issubset(self._tags)

        for tag, variable in zip(self._tags, self._checked_variables):
            variable.set(tag in image.tags)

    def _reset(self):
        for checkbox in self._checkboxes:
            checkbox.destroy()

        self._checkboxes = []
        self._checked_variables = []

    def _set_tags(self, tags: List[model.Tag]):
        self._reset()

        for i, tag in enumerate(tags):
            variable = tk.BooleanVar(value=False)

            def command(tag: model.Tag = tag, checked: tk.BooleanVar = variable):
                if checked.get():
                    self._controller.tag_current_image(tag)
                else:
                    self._controller.untag_current_image(tag)

            shortcut: Optional[int]

            if i < 9:
                shortcut = i + 1
                text = f"[{shortcut}] {tag.name}"
            else:
                shortcut = None
                text = tag.name

            checkbox = tk.Checkbutton(
                master=self, text=text, anchor=tk.W, variable=variable, command=command,
            )
            checkbox.pack(fill=tk.X)

            if shortcut:
                root = self.winfo_toplevel()
                assert isinstance(root, MainWindow)
                root.bind(str(shortcut), lambda _, cb=checkbox: cb.invoke())

            self._tags = tags
            self._checkboxes.append(checkbox)
            self._checked_variables.append(variable)


class Menu(tk.Menu):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)

        self._controller = controller

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open...", command=self._open, accelerator="Ctrl+O")
        file_menu.add_command(
            label="Save", command=self._save, accelerator="Ctrl+S", state=tk.DISABLED
        )
        file_menu.add_command(
            label="Save as...", command=self._save_as, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_command(
            label="Exit", command=master.quit, accelerator="Ctrl+Q"
        )  # TODO: add confirm

        self.add_cascade(label="File", menu=file_menu)

        master.bind_all('<Control-o>', lambda _: self._open())
        master.bind_all('<Control-S>', lambda _: self._save())
        master.bind_all('<Control-Shift-S>', lambda _: self._save_as())
        master.bind_all('<Control-q>', lambda _: master.quit())  # TODO: add confirm

        self._file_menu = file_menu

    def _open(self):
        filename = filedialog.askopenfilename(
            filetypes=(("picpick savefile", '.picpick'),)
        )
        if filename == () or filename == '':
            return

        path = pathlib.Path(filename)
        self._controller.load(path)

    def enable_save(self):
        self._file_menu.entryconfigure('Save', state=tk.NORMAL)

    def _save(self):
        self._controller.save_current()

    def _save_as(self):
        filename = filedialog.asksaveasfilename(
            filetypes=(("picpick savefile", '.picpick'),)
        )
        if filename == () or filename == '':
            return

        path = pathlib.Path(filename)
        self._controller.save(path)
