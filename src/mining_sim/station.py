"""Representation of an unloading station"""

from collections import deque
from dataclasses import dataclass, field

from mining_sim.truck import Truck


@dataclass
class Station:
    """
    ready_time_estimate is accurate if 0 or 1 truck in queue,
    estimated if >= 2 trucks in the queue.  All times in minutes,
    ready_time_estimate, task_started_at are absolute times.
    queue is the queue of trucks waiting to unload,
    queue[0] is currently unloading.
    """

    station_id: int
    queue: deque[Truck] = field(default_factory=deque)
    ready_time_estimate: float = 0.0  # made float for config.AVG_UNLOAD_TIME

    # statistics for report
    task_started_at: int = 0
    time_unloading: int = 0
    time_idle: int = 0
    trucks_unloaded: int = 0
