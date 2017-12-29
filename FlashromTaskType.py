from enum import Enum


class FlashromTaskType(Enum):
    READ = 0
    WRITE = 1
    ERASE = 3
