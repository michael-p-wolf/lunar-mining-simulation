from collections import deque
from dataclasses import dataclass, field

from mining_sim.truck import Truck


@dataclass
class Station:
    """Time is measured in minutes"""

    station_id: int
    queue: deque[Truck] = field(default_factory=deque)
    ready_time_estimate: float = (
        0  # accurate if 0 or 1 truck in queue, estimate if >= 2, absolute time
        # made float for config.AVG_UNLOAD_TIME
    )

    # statistics for report
    task_started_at: int = 0
    time_unloading: int = 0
    time_idle: int = 0
    trucks_unloaded: int = 0
