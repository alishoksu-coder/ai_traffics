from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def get_locations(self):
        raise NotImplementedError

    @abstractmethod
    def get_records(self, start, end, step_minutes):
        raise NotImplementedError
