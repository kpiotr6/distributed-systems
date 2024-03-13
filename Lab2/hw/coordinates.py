import httpx

from Exceptions import StatusCodeException

website = "https://nominatim.openstreetmap.org"


async def get_cities(city: str, max_entries: int) -> list[dict]:
    params = {"city": city, "format": "json"}
    async with httpx.AsyncClient() as client:
        res = await client.get(website, params=params)
    if res.status_code != 200:
        raise StatusCodeException("Failed to retrive data from Open Street Map", res.content,
                                  res.status_code)
    if len(res.json())==0:
        raise StatusCodeException("No cities with given name", res.content, res.status_code)
    return res.json()[:max_entries]


def extract_coordinates(city_data: dict) -> tuple[int, int]:
    return city_data.get("lat"), city_data.get("lon")

