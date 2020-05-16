import tkinter as tk

from typing import List, Tuple
from unittest import mock

from picpick import widgets
from picpick.model import Tag


class FileList(widgets.FileList):
    def __init__(self, master):
        super().__init__(master)
        self._callback = mock.Mock()
        self.bind('<<FileListSelect>>', lambda _: self._callback())

    def select_event_generated(self) -> bool:
        result = self._callback.called
        self._callback.reset_mock()
        return result

    @property
    def displayed(self) -> List[str]:
        return [self._tree.item(iid)['text'] for iid in self._tree.get_children()]


class TagList(widgets.TagList):
    @property
    def disabled(self) -> bool:
        return all(cb['state'] == tk.DISABLED for cb in self._checkboxes)

    def toggle(self, tag: Tag):
        index = self._tags.index(tag)
        checkbox = self._checkboxes[index]

        checkbox.invoke()

    @property
    def displayed(self) -> List[Tuple[str, bool]]:
        return [
            (tag.name, variable.get())
            for tag, variable in zip(self._tags, self._checked_variables)
        ]


def test_file_list(image_factory):
    file_list = FileList(None)
    assert file_list.displayed == []
    assert file_list.selected is None

    a = image_factory('a.jpg')
    b = image_factory('b.jpg')
    c = image_factory('c.jpg')

    file_list.set_images([a, b, c])
    assert file_list.displayed == ['a.jpg', 'b.jpg', 'c.jpg']
    assert file_list.selected is None

    assert not file_list.select_event_generated()

    file_list.select(a)
    file_list.update()

    assert file_list.selected == a
    assert file_list.select_event_generated()

    assert not file_list.select_event_generated()

    file_list.select(None)
    file_list.update()

    assert file_list.selected is None
    assert file_list.select_event_generated()

    file_list.select(b)
    file_list.update()

    assert file_list.selected == b
    assert file_list.select_event_generated()

    assert not file_list.select_event_generated()

    file_list.set_images([a, c])
    file_list.update()

    assert file_list.displayed == ['a.jpg', 'c.jpg']
    assert file_list.selected is None

    assert file_list.select_event_generated()

    file_list.select(None)
    file_list.update()


def test_tag_list(image_factory):
    callback = mock.Mock()
    tag_list = TagList(None, callback=callback)

    assert tag_list.displayed == []
    assert tag_list.disabled

    red = Tag(name='red')
    blue = Tag(name='blue')

    tag_list.set_tags([red, blue])

    assert tag_list.displayed == [('red', False), ('blue', False)]
    assert tag_list.disabled

    a = image_factory('a.jpg')
    b = image_factory('b.jpg')

    a.tags.add(red)
    b.tags.add(blue)

    tag_list.set_current_image(a)
    assert tag_list.displayed == [('red', True), ('blue', False)]
    assert not tag_list.disabled

    callback.assert_not_called()

    tag_list.set_current_image(b)
    assert tag_list.displayed == [('red', False), ('blue', True)]
    assert not tag_list.disabled

    callback.assert_not_called()

    tag_list.toggle(red)
    assert tag_list.displayed == [('red', True), ('blue', True)]
    callback.assert_called_once_with(red, True)
    callback.reset_mock()

    tag_list.toggle(red)
    assert tag_list.displayed == [('red', False), ('blue', True)]
    callback.assert_called_once_with(red, False)
    callback.reset_mock()
