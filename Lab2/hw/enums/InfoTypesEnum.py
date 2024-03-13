from enum import Enum


class InfoTypesEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    TEMPERATURE_MIN = "Minimum temperature (°C)"
    TEMPERATURE_MAX = "Maximum temperature (°C)"
    RAIN = "Rain (mm)"
    WIND = "Wind (km/h)"
    DATE = "Date"
