import tkinter as tk

from tkinter import messagebox

from PIL import Image

from . import widgets
from .app import App


class MainWindow(tk.Tk):
    def __init__(self, app: App):
        super().__init__()

        self.app = app

        self.geometry('720x480')
        self.attributes('-type', 'dialog')  # make window floating on i3wm

        self._setup_file_list()
        self._setup_image_display()
        self._setup_picking_buttons()

        self._update_image_display()
        self._update_file_list()

    def _setup_file_list(self):
        file_list = widgets.FileList(master=self, inputs=self.app.inputs)

        def select(event: tk.Event):
            widget = event.widget
            assert isinstance(widget, widgets.FileList)

            self.app.select_image(widget.selection())
            self._update_image_display()

        file_list.bind('<<FileListSelect>>', select)
        file_list.pack(fill=tk.BOTH, side=tk.LEFT)

        self._file_list = file_list

    def _update_file_list(self):
        self._file_list.selection_set(self.app._current_input_image_index)

    def _setup_image_display(self):
        self._image_display = widgets.ImageDisplay(master=self)
        self._image_display.pack(fill=tk.BOTH, expand=True)

    def _update_image_display(self):
        path = self.app.current_image.path
        self._image_display.set_image(Image.open(path))

    def _setup_picking_buttons(self):
        frame = tk.Frame(master=self, padx=4, pady=4)
        frame.pack(fill=tk.X)

        def command(output):
            def inner():
                self.app.assign_current_image_to(output)
                try:
                    self.app.next_image()
                    self._update_image_display()
                    self._update_file_list()
                except StopIteration:
                    summary = '\n'.join(
                        f"{src} -> {dst}" for src, dst in self.app._assignments.items()
                    )
                    print(summary)

                    if messagebox.askokcancel(message="Perform move ?"):
                        self.app.perform_assignments()
                        messagebox.showinfo(message="Done!")

            return inner

        for i, output in enumerate(self.app.outputs):
            key = i + 1
            func = command(output)

            button = tk.Button(
                master=frame, text=f"[{key}] {output.path}", command=func
            )
            button.pack(fill=tk.X, expand=True, side=tk.LEFT)
            self.bind(key, lambda _: func())

    def run(self):
        self.mainloop()
