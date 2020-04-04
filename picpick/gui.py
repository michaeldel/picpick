import tkinter as tk
import tkinter.ttk as ttk

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

        self._setup_input_paths_display()
        self._setup_image_display()
        self._setup_picking_buttons()

        self._update_image_display()
        self._update_input_paths_display()

    def _setup_input_paths_display(self):
        self._input_paths_display = ttk.Treeview(master=self, selectmode='browse')

        ROOT = ''
        for i, input in enumerate(self.app.inputs):
            tag = str(i)
            self._input_paths_display.insert(ROOT, tk.END, text=str(input), tags=(tag,))

        def select(event: tk.Event):
            widget = event.widget
            assert isinstance(widget, ttk.Treeview)
            selection = widget.selection()
            assert isinstance(selection, tuple) and len(selection) == 1

            # TODO: refactor this properly
            index = widget.item(selection[0])['tags'][0]
            self.app.select_image(self.app.inputs[index])

            self._update_image_display()

        self._input_paths_display.bind('<<TreeviewSelect>>', select)
        self._input_paths_display.pack(fill=tk.BOTH, side=tk.LEFT)

    def _update_input_paths_display(self):
        item = self._input_paths_display.get_children()[
            self.app._current_input_image_index
        ]
        self._input_paths_display.selection_set(item)

    def _setup_image_display(self):
        self._image_display = widgets.ImageDisplay(master=self)
        self._image_display.pack(fill=tk.BOTH, expand=True)

    def _update_image_display(self):
        path = self.app.current_image
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
                    self._update_input_paths_display()
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
