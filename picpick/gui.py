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

        self._setup_paths_listbox()
        self._setup_image_display()
        self._setup_picking_buttons()

        self._update_image_display()
        self._update_paths_listbox()

    def _setup_paths_listbox(self):
        self._paths_listbox = tk.Listbox(master=self, width=50)

        values = self.app.inputs
        self._paths_listbox.insert(tk.END, *values)

        def select(event: tk.Event):
            widget = event.widget
            assert isinstance(widget, tk.Listbox)
            selection = widget.curselection()
            assert isinstance(selection, tuple) and len(selection) == 1

            self.app.select_image(values[selection[0]])
            self._update_image_display()

        self._paths_listbox.bind('<<ListboxSelect>>', select)
        self._paths_listbox.pack(fill=tk.BOTH, side=tk.LEFT)

    def _update_paths_listbox(self):
        n = self._paths_listbox.size()
        self._paths_listbox.selection_clear(0, n - 1)
        self._paths_listbox.selection_set(self.app._current_input_image_index)

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
                    self._update_paths_listbox()
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
