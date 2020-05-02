from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import sys

from typing import List, TYPE_CHECKING

from . import model

if TYPE_CHECKING:  # required to prevent circular imports
    from .controller import Controller


class TagsManagerDialog(tk.Toplevel):
    def __init__(self, master, controller: Controller):
        super().__init__(master=master)

        if sys.platform == 'linux':
            self.attributes('-type', 'dialog')  # make window floating on i3wm

        self.grab_set()
        self.focus_set()

        self.transient(master=master)

        pad = 4

        ALL = tk.N + tk.S + tk.W + tk.E

        self._input_tag_name = tk.StringVar(master=self)
        entry = tk.Entry(master=self, textvariable=self._input_tag_name)
        entry.grid(row=0, column=0, sticky=ALL, padx=pad, pady=pad)

        add_button = tk.Button(master=self, text="Add", command=self._add)
        add_button.grid(row=0, column=1, sticky=ALL, padx=pad, pady=pad)

        import_button = tk.Button(master=self, text="Import...", command=self._import)
        import_button.grid(
            row=1, column=1, sticky=tk.N + tk.W + tk.E, padx=pad, pady=pad
        )

        export_button = tk.Button(master=self, text="Export...", command=self._export)
        export_button.grid(
            row=2, column=1, sticky=tk.N + tk.W + tk.E, padx=pad, pady=pad
        )

        delete_button = tk.Button(master=self, text="Delete", command=self._delete)
        delete_button.grid(
            row=3, column=1, sticky=tk.S + tk.W + tk.E, padx=pad, pady=pad
        )

        frame = tk.Frame(master=self)
        frame.grid(row=1, column=0, rowspan=3, sticky=ALL, padx=pad, pady=pad)

        tags_list = tk.Listbox(master=frame)
        scroll = ttk.Scrollbar(master=frame, orient=tk.VERTICAL)

        tags_list.configure(yscrollcommand=scroll.set)
        scroll.configure(command=tags_list.yview)

        scroll.pack(fill=tk.Y, side=tk.RIGHT)
        tags_list.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        items_count_display = tk.StringVar()
        items_count = tk.Label(master=self, textvariable=items_count_display)
        items_count.grid(row=4, column=0, sticky=tk.W, padx=pad, pady=pad)

        self._items_count_display = items_count_display

        button = tk.Button(master=self, text="OK", command=self.ok)
        button.grid(row=4, column=1, sticky=ALL, padx=pad, pady=pad)

        self._input_tag_name.trace(tk.W, lambda *_: self.refresh())

        self._entry = entry
        self._tags_list = tags_list

        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 1, weight=1)

        self._controller = controller
        self.refresh()

    def _add(self):
        name = self._input_tag_name.get()
        if name == "":
            return

        self._controller.add_tag(model.Tag(name=name))
        self._input_tag_name.set("")
        self.refresh()

    def _delete(self):
        self._controller.delete_tag(self._selected_tag)
        self._input_tag_name.set("")
        self.refresh()

    @property
    def _selected_tag(self) -> model.Tag:
        selection = self._tags_list.curselection()
        assert isinstance(selection, tuple) and len(selection) == 1

        index = selection[0]
        assert isinstance(index, int)

        return self._filtered_tags[index]

    def _import(self):
        raise NotImplementedError

    def _export(self):
        raise NotImplementedError

    def ok(self):
        self.destroy()

    def refresh(self):
        self._tags_list.delete(0, tk.END)
        self._items_count_display.set(f"{len(self._controller.tags)} items")

        for tag in self._filtered_tags:
            self._tags_list.insert(tk.END, tag.name)

    @property
    def _filtered_tags(self) -> List[model.Tag]:
        pattern = self._input_tag_name.get()
        if pattern == "":
            return self._controller.tags

        return [tag for tag in self._controller.tags if pattern in tag.name]
