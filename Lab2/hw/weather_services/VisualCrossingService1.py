import httpx
from Services import Services
from enums import InfoTypesEnum


class VisualCrossingService(Services):

    def __init__(self):
        self.website = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self.api_key = "CTA6DV8C2SMXU8W96Y9MCLV3D"
        self.additonal_query = {"key": self.api_key, "include": "days"}

    async def get_data(self, lat: float, lon: float, start_date: str, end_date: str, stats: InfoTypesEnum):
        params = self.additonal_query
        url = self.website + "/" + str(lat) + "," + str(lon) + "/" + start_date + "/" + end_date
        response = httpx.get(url, params=params)
        return response.json()
