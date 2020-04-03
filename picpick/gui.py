import pathlib
import tkinter as tk

from typing import List

from PIL import Image, ImageTk


class MainWindow(tk.Tk):
    def __init__(self, paths: List[pathlib.Path]):
        assert len(paths) > 0

        super().__init__()

        image = Image.open(paths[-1])
        canvas = tk.Canvas(master=self)

        canvas_image = canvas.create_image(
            0, 0, anchor=tk.CENTER, image=ImageTk.PhotoImage(image)
        )

        def configure(event: tk.Event):
            # use thumbnail to maintain aspect ratio
            width = canvas.winfo_width()
            height = canvas.winfo_height()

            assert width <= event.width
            assert height <= event.height

            resized = image.copy()
            resized.thumbnail((width, height), Image.ANTIALIAS)

            photo = ImageTk.PhotoImage(resized)

            canvas.itemconfig(canvas_image, image=photo)
            canvas.photo = photo  # prevent garbage collection
            canvas.coords(canvas_image, (width / 2, height / 2))

        canvas.bind('<Configure>', configure)
        canvas.pack(fill=tk.BOTH, expand=True)

        self.attributes('-type', 'dialog')  # make window floating on i3wm

    def run(self):
        self.mainloop()
