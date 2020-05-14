from enum import auto
from unittest import mock

from picpick import events
from picpick.notifier import Notifier


class Event(events.Event):
    FOO = auto()
    BAR = auto()


def test_register_and_notify():
    notifier = Notifier()

    a = mock.Mock()
    b = mock.Mock()
    c = mock.Mock()

    notifier.register(Event.FOO, a)
    notifier.register(Event.BAR, b)

    notifier.register(Event.FOO, c)
    notifier.register(Event.BAR, c)

    notifier.notify(Event.FOO)

    a.assert_called_once_with()
    b.assert_not_called()
    c.assert_called_once_with()

    a.reset_mock()
    c.reset_mock()

    notifier.notify(Event.BAR)

    a.assert_not_called()
    b.assert_called_once_with()
    c.assert_called_once_with()

    b.reset_mock()
    c.reset_mock()
