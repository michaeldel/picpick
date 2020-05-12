from typing import List
from unittest import mock

from picpick import widgets


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
