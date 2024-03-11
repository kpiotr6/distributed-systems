from enum import Enum


class InfoTypesEnum(Enum):
    TEMPERATURE = 1 << 0
    RAIN = 1 << 1
    WIND = 1 << 2
