from __future__ import annotations

import pathlib
import sys
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog, messagebox
from typing import List, Optional, TYPE_CHECKING

from . import dialogs, model, widgets

if TYPE_CHECKING:  # required to prevent circular imports
    from .controller import Controller


class MainWindow(tk.Tk):
    def __init__(self, controller: Controller):
        super().__init__()

        self.title("PicPick *")
        self.geometry('928x640')

        if sys.platform == 'linux':
            self.attributes('-type', 'dialog')  # make window floating on i3wm

        menu = Menu(master=self, controller=controller)
        self.config(menu=menu)

        pw = ttk.PanedWindow(master=self, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        image_display = widgets.ImageDisplay(master=pw)

        sidebar = ttk.PanedWindow(master=pw, orient=tk.VERTICAL)

        file_list = widgets.FileList(master=sidebar)
        tag_section = TagSection(master=sidebar, controller=controller)

        sidebar.add(file_list)
        sidebar.add(tag_section)

        pw.add(sidebar)
        pw.add(image_display)

        self._menu = menu

        self.file_list = file_list
        self.tag_list = tag_section.tag_list
        self.image_display = image_display

    def mark_unsaved(self):
        self.title("PicPick *")

    def mark_saved(self):
        self.title("PicPick")
        self._menu.enable_save()


class TagSection(tk.Frame):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)

        tag_list = TagList(master=self, controller=controller)
        tag_manager_button = tk.Button(
            master=self,
            text="Manage tags",
            command=lambda: dialogs.TagsManagerDialog(
                master=self, controller=controller
            ),
        )

        tag_list.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        tag_manager_button.pack(fill=tk.X, expand=0, side=tk.BOTTOM, padx=8, pady=8)

        self.tag_list = tag_list


class TagList(tk.Frame):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)
        label = tk.Label(master=self, text="Tags")
        label.pack()

        self._checkboxes: List[tk.Checkbutton] = []
        self._checked_variables: List[tk.BooleanVar] = []

        self._controller = controller

        self.set_tags(controller.tags)

    def set_current_image(self, image: model.Image):
        assert image.tags.issubset(self._tags)

        for tag, variable in zip(self._tags, self._checked_variables):
            variable.set(tag in image.tags)

    def _reset(self):
        for checkbox in self._checkboxes:
            checkbox.destroy()

        self._checkboxes = []
        self._checked_variables = []

    def set_tags(self, tags: List[model.Tag]):
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

            self._checkboxes.append(checkbox)
            self._checked_variables.append(variable)

        self._tags = tags


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
        file_menu.add_separator()
        file_menu.add_command(label="Add images...", command=self._add_image)
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit", command=master.quit, accelerator="Ctrl+Q"
        )  # TODO: add confirm

        self.add_cascade(label="File", menu=file_menu)

        master.bind_all('<Control-o>', lambda _: self._open())
        master.bind_all('<Control-s>', lambda _: self._save())
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
        if hasattr(self._controller, 'last_save_path'):
            self._controller.save_current()
        self._save_as()

    def _save_as(self):
        filename = filedialog.asksaveasfilename(
            filetypes=(("picpick savefile", '.picpick'),)
        )
        if filename == () or filename == '':
            return

        path = pathlib.Path(filename)
        self._controller.save(path)

    def _add_image(self):
        filenames = filedialog.askopenfilenames(
            filetypes=(("image file", '.jpg .jpeg .png .bmp .pgm .pbm .ppm'),)
        )
        if filenames == () or filenames == '':
            return

        from .controller import Controller

        errored = False

        for filename in filenames:
            path = pathlib.Path(filename)
            try:
                self._controller.add_image(model.Image(path=path))
            except Controller.ImageAlreadyPresent:
                errored = True

        if errored:
            messagebox.showwarning(
                "Images already present", "Some images were already present"
            )
