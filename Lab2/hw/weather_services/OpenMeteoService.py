import httpx
from .Services import Services
from enums import InfoTypesEnum

from Exceptions import StatusCodeException

class OpenMeteoService(Services):

    def __init__(self, lat: float, lon: float):
        super().__init__(lat,lon)
        self._website = "https://api.open-meteo.com/v1/forecast"
        self._additonal_query = {"timezone": "Europe/Warsaw"}
        self._keys = {

            InfoTypesEnum.TEMPERATURE_MIN.value: "temperature_2m_min",
            InfoTypesEnum.TEMPERATURE_MAX.value: "temperature_2m_max",
            InfoTypesEnum.RAIN.value: "precipitation_sum",
            InfoTypesEnum.WIND.value: "wind_speed_10m_max",
            InfoTypesEnum.DATE.value: "time"
        }

    async def get_data(self, start_date: str, end_date: str, stats: list[InfoTypesEnum]):
        params = {"latitude": self._lat, "longitude": self._lon, "start_date": start_date, "end_date": end_date}
        params.update(self._additonal_query)
        params.update(self._add_queries(stats))
        async with httpx.AsyncClient() as client:
            response = await client.get(self._website, params=params)
        if response.status_code != 200:
            raise StatusCodeException("Failed to retrive data from Open Meteo", response.json().get("reason"), response.status_code)
        return self._format_data(response.json(), stats)

    def _format_data(self, data: dict, stats: list[InfoTypesEnum]):
        data = data.get("daily")
        data_extracted = {}
        for s_value in stats:
            outer_key = self._keys.get(s_value.value)
            data_extracted.update({s_value.value:data.get(outer_key)})
        return data_extracted

    def _add_queries(self, stats: list[InfoTypesEnum]):
        q_string = ""
        for stat in stats:
            if InfoTypesEnum.DATE != stat:
                q_string+= self._keys.get(stat.value) + ","
        q_string = q_string[:-1]
        return {"daily": q_string}
