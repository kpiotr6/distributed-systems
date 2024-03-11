from abc import ABC, abstractmethod
from enums.InfoTypesEnum import InfoTypesEnum

class Services(ABC):

    @abstractmethod
    def get_data(lat: float, lon: float, start_date: str, end_date: str, stats: InfoTypesEnum):
        pass
        
