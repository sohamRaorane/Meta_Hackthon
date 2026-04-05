# from pydantic import BaseModel
# from typing import List, Optional, Literal
# from openenv.core.env_server import Action, Observation, State


# class MumbaiAction(Action):
#     message: str


# class ModeInfo(BaseModel):
#     mode: Literal["train", "auto", "bus", "metro", "walk"]
#     available: bool
#     confidence: float
#     est_cost: float
#     est_time_min: int
#     est_time_max: int


# class MumbaiObservation(Observation):
#     echoed_message: str
#     current_location: str
#     destination: str
#     time_remaining_minutes: int
#     budget_remaining: float
#     weather: Literal["clear", "light_rain", "heavy_rain"]
#     available_modes: List[ModeInfo]
#     known_disruptions: List[str]
#     mid_journey_update: Optional[str] = None
#     timestep: int


# class MumbaiState(State):
#     task_name: str = ""
#     origin: str = ""
#     destination: str = ""
#     seed: int = 42


from pydantic import BaseModel
from typing import List, Optional, Literal
from openenv.core.env_server import Action, Observation, State


class MumbaiAction(Action):
    message: str


class ModeInfo(BaseModel):
    mode: Literal["train", "auto", "bus", "metro", "walk"]
    available: bool
    confidence: float
    est_cost: float
    est_time_min: int
    est_time_max: int


class MumbaiObservation(Observation):
    episode_id: Optional[str] = None
    echoed_message: str
    current_location: str
    destination: str
    time_remaining_minutes: int
    budget_remaining: float
    weather: Literal["clear", "light_rain", "heavy_rain"]
    available_modes: List[ModeInfo]
    known_disruptions: List[str]
    mid_journey_update: Optional[str] = None
    timestep: int


class MumbaiState(State):
    task_name: str = ""
    origin: str = ""
    destination: str = ""
    seed: int = 42