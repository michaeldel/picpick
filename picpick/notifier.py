from collections import defaultdict
from typing import Callable

from .events import Event


class Notifier:
    def __init__(self):
        self._callbacks = defaultdict(list)

    def register(self, event: Event, callback: Callable):
        assert callback not in self._callbacks[event]
        self._callbacks[event].append(callback)

    def notify(self, event: Event):
        for callback in self._callbacks[event]:
            callback()
