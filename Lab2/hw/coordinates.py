import httpx

website = "https://nominatim.openstreetmap.org"


async def get_cities(city: str, max_entries: int) -> list[dict]:
    params = {"city": city, "format": "json"}
    res = httpx.get(website, params=params)
    return res.json()[:max_entries]


def extract_coordinates(city_data: dict) -> tuple[int, int]:
    return city_data.get("lat"), city_data.get("lon")
