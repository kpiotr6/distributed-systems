import httpx
from Services import Services
from enums import InfoTypesEnum
from enums import in_alt


class OpenMeteoService(Services):

    def __init__(self):
        self.website = "https://api.open-meteo.com/v1/forecast"
        self.additonal_query = {"timezone": "Europe/Warsaw"}

    async def get_data(self, lat: float, lon: float, start_date: str, end_date: str, stats: InfoTypesEnum):
        params = {"latitude": lat, "longitude": lon, "start_date": start_date, "end_date": end_date}
        params.update(self.additonal_query)
        params.update(self.add_queries(stats))
        response = httpx.get(self.website, params=params)
        return response.json()

    def add_queries(self, stats: InfoTypesEnum):
        tmp_queries = {}
        if in_alt(stats, InfoTypesEnum.TEMPERATURE):
            tmp_queries.update({"daily": "temperature_2m_max,temperature_2m_min"})
        if in_alt(stats, InfoTypesEnum.RAIN):
            tmp_queries.update({"daily": "precipitation_sum," + tmp_queries.get("daily", "")})
        if in_alt(stats, InfoTypesEnum.WIND):
            tmp_queries.update({"daily": "wind_speed_10m_max," + tmp_queries.get("daily", "")})
        return tmp_queries
