from enum import Enum


def in_alt(alt: int, val: Enum):
    return alt & val.value == val.value
