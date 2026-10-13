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
    """All times are in minutes"""

    truck_id: int
    phase: TruckPhase
    ready_time: int | None  # absolute time
    current_station_id: int | None = None

    # statistics for report
    task_started_at: int = 0
    time_mining: int = 0
    time_unloading: int = 0
    time_traveling: int = 0
    time_waiting: int = 0
    total_unloads: int = 0
