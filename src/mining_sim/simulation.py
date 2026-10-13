import heapq
import random
from typing import NamedTuple

from mining_sim.config import (
    MINING_MAX_HOURS,
    MINING_MIN_HOURS,
    Config,
)
from mining_sim.station import Station
from mining_sim.truck import Truck, TruckPhase

# Order for events that land on the same minute
# Unloading finishes first so a new truck can begin unloading
# WAITING is not included because waiting trucks should not be in the heap
_PHASE_PRIO: dict[TruckPhase, int] = {
    TruckPhase.UNLOADING: 0,
    TruckPhase.TO_UNLOAD: 1,
    TruckPhase.TO_MINING: 2,
    TruckPhase.MINING: 3,
}


class Event(NamedTuple):
    """Field order of Event is the sort order for the truck heap"""

    time: int
    priority: int
    truck_id: int
    truck: Truck


class Simulation:
    # TODO: docstring
    """"""

    def __init__(self, config: Config) -> None:
        """Initialize simulation with n trucks and m stations"""
        self._time = 0
        self._config = config
        self._heap: list[Event] = []
        self._random = random.Random(config.seed)
        self._stations: list[Station] = []
        self._trucks: list[Truck] = []

        for i in range(1, self._config.num_trucks + 1):
            truck = Truck(
                truck_id=i,
                phase=TruckPhase.MINING,
                ready_time=self._random_mining_time_min(),
            )
            self._insert_truck_heap(truck=truck)
            self._trucks.append(truck)

        for j in range(1, self._config.num_stations + 1):
            station = Station(station_id=j)
            self._stations.append(station)

    def _insert_truck_heap(self, truck: Truck) -> None:
        """Push truck onto heap with ready_time

        Raises Runtime Error if truck has no ready_time (waiting state)
        """
        if truck.ready_time is None:
            raise RuntimeError(
                f"ready_time is none for truck_id:{truck.truck_id}, phase:{truck.phase}"
            )

        event = Event(
            time=truck.ready_time,
            priority=_PHASE_PRIO[truck.phase],
            truck_id=truck.truck_id,
            truck=truck,
        )
        heapq.heappush(self._heap, event)

    def _random_mining_time_min(self) -> int:
        """Returns random mining time (minutes) between
        [MINING_MIN_HOURS, MINING_MAX_HOURS] (inclusive) hours (resolution 1 hour)
        """
        return 60 * self._random.randint(MINING_MIN_HOURS, MINING_MAX_HOURS)
