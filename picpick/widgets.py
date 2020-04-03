import tkinter as tk

from PIL import Image, ImageTk

MIN_WIDTH = 128
MIN_HEIGHT = 128


class ImageDisplay(tk.Canvas):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.bind('<Configure>', lambda e: self._resize())

    def set_image(self, image: Image):
        self._image = image
        self._resize()

    def _set_canvas_image(self, image: Image):
        # keep stored as object attribute to prevent garbage collection
        self._photo = ImageTk.PhotoImage(image)
        if not hasattr(self, '_canvas_image'):
            width = self.winfo_width()
            height = self.winfo_height()

            self._canvas_image = self.create_image(
                width / 2, height / 2, anchor=tk.CENTER, image=self._photo
            )
        else:
            self.itemconfig(self._canvas_image, image=self._photo)

    def _resize(self):
        width = self.winfo_width()
        height = self.winfo_height()

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return

        # use thumbnail to maintain aspect ratio
        resized = self._image.copy()
        resized.thumbnail((width, height), Image.ANTIALIAS)

        self._set_canvas_image(resized)
