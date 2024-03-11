import coordinates
from weather_services.VisualCrossingService1 import VisualCrossingService
import asyncio
from enums.InfoTypesEnum import InfoTypesEnum


async def start():
    city = await coordinates.get_cities("Kraków", 1)
    coords = coordinates.extract_coordinates(city[0])
    meteo = VisualCrossingService()
    val = await meteo.get_data(coords[0], coords[1], "2024-01-01", "2024-01-02",
                               InfoTypesEnum.TEMPERATURE.value | InfoTypesEnum.RAIN.value | InfoTypesEnum.WIND.value)
    print(val)


if __name__ == "__main__":
    asyncio.run(start())
