from __future__ import annotations

import pathlib
import sys
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

from . import dialogs, model, widgets

if TYPE_CHECKING:  # required to prevent circular imports
    from .controller import Controller
    from .model import Model


class View:
    def __init__(self, controller: Controller, model: Model):
        self._controller = controller
        self._model = model

        self._window = MainWindow(controller=controller)

    def run(self):
        self._window.mainloop()

    def mark_saved(self):
        self._window.mark_saved()

    def update_images(self):
        images = sorted(self._model.images, key=lambda image: image.path.name)
        self._window.file_list.set_images(images)
        self._window.mark_unsaved()

    def update_current_image(self):
        image = self._controller.current_image
        self._window.file_list.select(image)
        self._window.image_display.set_image(image)

        self.update_current_image_tags()
        self._window.mark_unsaved()

    def update_tags(self):
        tags = sorted(self._model.tags, key=lambda tag: tag.name)
        self._window.tag_list.set_tags(tags)
        self._window.file_list.refresh()  # TODO: add tests for this
        self._window.mark_unsaved()

    def update_current_image_tags(self):
        self._window.tag_list.set_current_image(self._controller.current_image)
        self._window.file_list.refresh()  # TODO: add tests for this
        self._window.mark_unsaved()


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
        file_list.bind(
            '<<FileListSelect>>',
            lambda _: controller.set_current_image(file_list.selected),
        )
        tag_section = TagSection(master=sidebar, controller=controller)

        sidebar.add(file_list)
        sidebar.add(tag_section)

        pw.add(sidebar)
        pw.add(image_display)

        self._menu = menu

        self.file_list = file_list
        self.tag_list: widgets.TagList = tag_section.tag_list
        self.image_display: widgets.ImageDisplay = image_display

    def mark_unsaved(self):
        self.title("PicPick *")

    def mark_saved(self):
        self.title("PicPick")
        self._menu.enable_save()


class TagSection(tk.Frame):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)

        tag_list = widgets.TagList(
            master=self, callback=controller.set_current_image_tag
        )
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
