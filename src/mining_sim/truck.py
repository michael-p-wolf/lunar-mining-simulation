"""Representation of mining trucks and Enum for possible actions"""

from dataclasses import dataclass
from enum import StrEnum


class TruckPhase(StrEnum):
    TO_MINING = "TO_MINING"
    TO_UNLOAD = "TO_UNLOAD"
    MINING = "MINING"
    UNLOADING = "UNLOADING"
    WAITING = "WAITING"


@dataclass
class Truck:
    """
    ready_time will be None only when truck is WAITING.
    All times are measured in minutes.
    ready_time and task_started_at are absolute times.
    current_station_id is the id of the station this truck
    is unloading or waiting at.
    """

    truck_id: int
    phase: TruckPhase
    ready_time: int | None
    current_station_id: int | None = None

    # statistics for report
    task_started_at: int = 0
    time_mining: int = 0
    time_unloading: int = 0
    time_traveling: int = 0
    time_waiting: int = 0
    total_unloads: int = 0
