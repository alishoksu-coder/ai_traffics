from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Location:
    id: int
    name: str
    lat: float
    lon: float

@dataclass(frozen=True)
class TrafficRecord:
    timestamp: datetime
    location_id: int
    traffic_value: float  # 0..100
