from enum import auto, Enum


class Event(Enum):
    IMAGES_CHANGED = auto()
    CURRENT_IMAGE_CHANGED = auto()
