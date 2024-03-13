from abc import ABC, abstractmethod
from enums import InfoTypesEnum

class Services(ABC):
    def __init__(self,lat: float, lon: float):
        self._lat = lat
        self._lon = lon
    @abstractmethod
    async def get_data(self, start_date: str, end_date: str, stats: list[InfoTypesEnum]):
        pass
        
