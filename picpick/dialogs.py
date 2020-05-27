from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import sys

from tkinter import messagebox
from typing import List, Optional, Set

from .model import Tag


class TagsManagerDialog(tk.Toplevel):  # TODO: consider simpledialogs.Dialog instead
    def __init__(self, master, tags: Set[Tag], displayed_tags: List[Tag]):
        super().__init__(master=master)
        self.master: tk.Widget

        assert all(t in tags for t in displayed_tags)
        assert len(set(displayed_tags)) == len(displayed_tags)

        self._tags = tags
        self._displayed_tags = displayed_tags

        self.title("Tags manager")

        if sys.platform == 'linux':
            self.attributes('-type', 'dialog')  # make window floating on i3wm

        self.__init_interface()

        self.refresh()

        self.__set_modal()
        self.__init_position()

        self.update_idletasks()
        self.wait_window(self)

    def __init_interface(self):
        pad = 4

        ALL = tk.N + tk.S + tk.W + tk.E

        self._input_tag_name = tk.StringVar(master=self)
        entry = tk.Entry(master=self, textvariable=self._input_tag_name)
        entry.grid(row=0, column=0, sticky=ALL, padx=pad, pady=pad)

        entry.bind('<Return>', lambda _: self._add())
        entry.focus()

        add_button = tk.Button(master=self, text="Add", command=self._add)
        add_button.grid(row=0, column=1, sticky=ALL, padx=pad, pady=pad)

        add_to_displayed_button = tk.Button(
            master=self, text=">", command=self._add_to_displayed
        )
        add_to_displayed_button.grid(row=1, column=1, sticky=ALL, padx=pad, pady=pad)
        remove_from_displayed_button = tk.Button(
            master=self, text="<", command=self._remove_from_displayed
        )
        remove_from_displayed_button.grid(
            row=2, column=1, sticky=ALL, padx=pad, pady=pad
        )

        delete_button = tk.Button(master=self, text="Delete", command=self._delete)
        delete_button.grid(
            row=3, column=1, sticky=tk.S + tk.W + tk.E, padx=pad, pady=pad
        )

        left_frame = tk.Frame(master=self)
        left_frame.grid(row=1, column=0, rowspan=3, sticky=ALL, padx=pad, pady=pad)

        tags_list = tk.Listbox(master=left_frame)
        tags_scroll = ttk.Scrollbar(master=left_frame, orient=tk.VERTICAL)

        tags_list.configure(yscrollcommand=tags_scroll.set)
        tags_scroll.configure(command=tags_list.yview)

        tags_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        tags_list.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        right_frame = tk.Frame(master=self)
        right_frame.grid(row=1, column=2, rowspan=3, sticky=ALL, padx=pad, pady=pad)

        displayed_tags_list = tk.Listbox(master=right_frame)
        displayed_tags_scroll = ttk.Scrollbar(master=right_frame, orient=tk.VERTICAL)

        displayed_tags_list.configure(yscrollcommand=displayed_tags_scroll.set)
        displayed_tags_scroll.configure(command=displayed_tags_list.yview)

        displayed_tags_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        displayed_tags_list.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        items_count_display = tk.StringVar()
        items_count = tk.Label(master=self, textvariable=items_count_display)
        items_count.grid(row=4, column=0, sticky=tk.W, padx=pad, pady=pad)

        self._items_count_display = items_count_display

        button = tk.Button(master=self, text="OK", command=self.ok)
        button.grid(row=4, column=1, sticky=ALL, padx=pad, pady=pad)

        self._input_tag_name.trace(tk.W, lambda *_: self.refresh())

        self._entry = entry
        self._tags_list = tags_list
        self._displayed_tags_list = displayed_tags_list

        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 1, weight=1)

    def __set_modal(self):
        self.grab_set()
        self.focus_set()
        self.transient(master=self.master)

    def __init_position(self):
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()

        root = self.master.winfo_toplevel()

        x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)

        self.geometry(f'+{x}+{y}')

    def _add(self):
        name = self._input_tag_name.get()
        if name == "":
            return

        if Tag(name=name) in self._tags:
            messagebox.showerror(
                "Tag already present", f"\"{name}\" tag is already present"
            )
            return

        self._tags.add(Tag(name=name))
        self._input_tag_name.set("")
        self.refresh()

    def _delete(self):
        if self._selected_tag is None:
            messagebox.showerror(
                "No tag selected", "Cannot delete tag when no tag is selected"
            )
            return

        self._tags.remove(self._selected_tag)
        self._displayed_tags.remove(self._selected_tag)

        self._input_tag_name.set("")
        self.refresh()

    def _add_to_displayed(self):
        tag = self._selected_tag

        if tag is None:
            return
        if tag in self._displayed_tags:
            messagebox.showerror(
                "Tag already displayed", f"Tag \"{tag.name}\" is already displayed"
            )
            return
        self._displayed_tags.append(tag)
        self.refresh()

    def _remove_from_displayed(self):
        tag = self._selected_displayed_tag

        if tag is None:
            return

        self._displayed_tags.remove(tag)
        self.refresh()

    @property
    def _selected_tag(self) -> Optional[Tag]:
        selection = self._tags_list.curselection()

        if selection == ():
            return None
        assert len(selection) == 1

        index = selection[0]
        assert isinstance(index, int)

        return self._filtered_tags[index]

    @property
    def _selected_displayed_tag(self) -> Optional[Tag]:
        selection = self._displayed_tags_list.curselection()

        if selection == ():
            return None
        assert len(selection) == 1

        index = selection[0]
        assert isinstance(index, int)

        return self._displayed_tags[index]

    def ok(self):
        self.destroy()

    def refresh(self):
        self._tags_list.delete(0, tk.END)
        self._displayed_tags_list.delete(0, tk.END)
        self._items_count_display.set(f"{len(self._tags)} items")

        for tag in self._filtered_tags:
            self._tags_list.insert(tk.END, tag.name)
        for tag in self._displayed_tags:
            self._displayed_tags_list.insert(tk.END, tag.name)

    @property
    def _filtered_tags(self) -> List[Tag]:
        pattern = self._input_tag_name.get()
        if pattern == "":
            return self._sorted_tags

        return [tag for tag in self._sorted_tags if pattern in tag.name]

    @property
    def _sorted_tags(self) -> List[Tag]:
        return sorted(self._tags, key=lambda tag: tag.name)

    @property
    def tags(self) -> Set[Tag]:
        return self._tags

    @property
    def displayed_tags(self) -> List[Tag]:
        return self._displayed_tags
