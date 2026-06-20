from pydantic import BaseModel

class SimulationRequest(BaseModel):
    lat: float
    lon: float
    duration_min: int = 15

class MultimodalRequest(BaseModel):
    duration_now_sec: int
    distance_meters: int

class RouteCalculateRequest(BaseModel):
    start_node_id: int
    end_node_id: int
    mode: str = "car_fast"  # car_fast, pedestrian, barrier_free, anti_stress
    horizon_min: int = 0    # Traffic prediction horizon in minutes

class LoginRequest(BaseModel):
    login: str
    password: str

class AddFriendRequest(BaseModel):
    name: str

class MeetingRequest(BaseModel):
    user_id: str
    friend_id: str
    location_id: int
    meeting_time: str

class UserEventRequest(BaseModel):
    event_type: str
    lat: float
    lng: float

from typing import List
class SmartMeetRequest(BaseModel):
    user_locations: List[dict]  # list of {lat, lng}
    meeting_time_offset_min: int = 60 # how many minutes in future
