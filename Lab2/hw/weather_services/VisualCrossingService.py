import httpx
from .Services import Services
from enums import InfoTypesEnum
from Exceptions import StatusCodeException
class VisualCrossingService(Services):

    def __init__(self, lat: float, lon: float):
        super().__init__(lat,lon)
        self._website = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self._api_key = "CTA6DV8C2SMXU8W96Y9MCLV3D"
        self._additonal_query = {"key": self._api_key, "include": "days", "unitGroup": "metric"}
        self._keys = {
            InfoTypesEnum.TEMPERATURE_MAX.value: "tempmax",
            InfoTypesEnum.TEMPERATURE_MIN.value: "tempmin",
            InfoTypesEnum.RAIN.value: "precip",
            InfoTypesEnum.WIND.value: "windspeedmax",
            InfoTypesEnum.DATE.value: "datetime"
        }

    async def get_data(self, start_date: str, end_date: str, stats: list[InfoTypesEnum]):
        params = self._additonal_query
        params.update(self._add_queries(stats))
        url = self._website + "/" + str(self._lat) + "," + str(self._lon) + "/" + start_date + "/" + end_date
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
        if response.status_code != 200:
            raise StatusCodeException("Failed to retrive data from Visual Crossing Weather Data", response.content, response.status_code)
        return self._format_data(response.json(), stats)

    def _format_data(self, data: dict, stats: list[InfoTypesEnum]):
        data = data.get("days")
        data_extracted = {}
        for day in data:
            for s in stats:
                value = day.get(self._keys.get(s.value))
                data_list = data_extracted.get(s.value, [])
                data_list.append(value)
                data_extracted.update({s.value: data_list})
        return data_extracted

    def _add_queries(self, stats: list[InfoTypesEnum]):
        q_string = ""
        for stat in stats:
            q_string+= self._keys.get(stat.value) + ","
        return {"elements":q_string}

