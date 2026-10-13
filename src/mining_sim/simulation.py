import heapq
import random
from typing import NamedTuple

from mining_sim.config import (
    AVG_UNLOAD_TIME,
    MINING_MAX_HOURS,
    MINING_MIN_HOURS,
    TRUCK_TRAVEL_TIME,
    UNLOAD_MAX_TIME,
    UNLOAD_MIN_TIME,
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

        for i in range(0, self._config.num_trucks):
            truck = Truck(
                truck_id=i,
                phase=TruckPhase.MINING,
                ready_time=self._random_mining_time_min(),
            )
            self._insert_truck_heap(truck=truck)
            self._trucks.append(truck)

        for j in range(0, self._config.num_stations):
            station = Station(station_id=j)
            self._stations.append(station)

    def run(self) -> None:
        """"""

        while self._heap and self._heap[0].time <= self._config.sim_minutes:
            event = heapq.heappop(self._heap)
            self._time = event.time
            self._process_truck(event.truck)

        self._time = self._config.sim_minutes

        sum_unloads = 0
        for truck in self._trucks:
            print(f"Truck {truck.truck_id}:")
            print(f"\ttotal unloads: {truck.total_unloads}")
            sum_unloads += truck.total_unloads

        sum_station_unloads = 0
        for station in self._stations:
            print(f"Station {station.station_id}:")
            print(f"\ttrucks unloaded: {station.trucks_unloaded}")
            sum_station_unloads += station.trucks_unloaded

        print(f"sum truck unloads == sum station unloads: {sum_unloads} == {sum_station_unloads}")

        # TODO: close truck mid-task and idle stations
        # TODO: return results of stats

    def _process_truck(self, truck: Truck) -> None:
        """Move a truck onto the next phase when it has completed previous phase"""
        # waiting state cannot happen, we just popped from the heap

        current_time = self._time

        if truck.phase == TruckPhase.UNLOADING:
            # completed unloading, update truck

            if truck.current_station_id is None:
                raise RuntimeError(
                    f"Truck with id: {truck.truck_id} is unloading with no station_id"
                )

            station = self._stations[truck.current_station_id]

            if not station.queue:
                raise RuntimeError(
                    f"Station with id: {station.station_id} has a truck but queue is empty"
                )

            if station.queue.popleft() is not truck:
                raise RuntimeError(
                    f"Truck (id: {truck.truck_id}) is ready at station (id: {station.station_id}) "
                    "but is not at the front of station queue"
                )

            truck.phase = TruckPhase.TO_MINING
            truck.ready_time = current_time + TRUCK_TRAVEL_TIME
            truck.current_station_id = None

            # Updating statistics fields
            truck.time_unloading += current_time - truck.task_started_at
            truck.task_started_at = current_time
            truck.total_unloads += 1

            self._insert_truck_heap(truck=truck)

            # update unload station
            station.time_unloading += current_time - station.task_started_at
            station.task_started_at = current_time
            station.trucks_unloaded += 1

            if station.queue:
                # we have a truck in the queue, start unloading it
                new_truck = station.queue[0]
                if new_truck.phase != TruckPhase.WAITING:
                    raise RuntimeError(
                        f"Truck (id: {truck.truck_id}) was waiting at station "
                        f"(id: {station.station_id}) but not WAITING"
                    )

                unload_time = self._random.randint(UNLOAD_MIN_TIME, UNLOAD_MAX_TIME)
                new_truck.phase = TruckPhase.UNLOADING
                new_truck.current_station_id = (
                    station.station_id
                )  # shouldn't need this based on how we process waiting
                new_truck.ready_time = current_time + unload_time

                # Updating statistics fields
                new_truck.time_waiting += current_time - new_truck.task_started_at
                new_truck.task_started_at = current_time

                self._insert_truck_heap(truck=new_truck)

                # Recalculate estimated waiting time
                station.ready_time_estimate = new_truck.ready_time + AVG_UNLOAD_TIME * (
                    len(station.queue) - 1
                )

            else:
                # The station queue is empty and it now idle
                station.ready_time_estimate = current_time

        elif truck.phase == TruckPhase.TO_UNLOAD:
            # Truck has arrived to unloading station, needs to begin unloading
            truck.time_traveling += current_time - truck.task_started_at
            truck.task_started_at = current_time

            # Find the next station for a truck
            station = self._stations[0]
            min_time_ready = station.ready_time_estimate

            for s in self._stations:
                if s.ready_time_estimate < min_time_ready:
                    station = s
                    min_time_ready = s.ready_time_estimate

            truck.current_station_id = station.station_id
            station.queue.append(truck)

            if len(station.queue) == 1:
                # truck can begin unloading
                truck.phase = TruckPhase.UNLOADING
                unload_time = self._random.randint(UNLOAD_MIN_TIME, UNLOAD_MAX_TIME)
                truck.ready_time = current_time + unload_time
                self._insert_truck_heap(truck=truck)

                station.time_idle += current_time - station.task_started_at
                station.task_started_at = current_time
                station.ready_time_estimate = truck.ready_time

            else:
                # truck must wait in station queue
                truck.phase = TruckPhase.WAITING
                truck.ready_time = None
                station.ready_time_estimate += AVG_UNLOAD_TIME

        elif truck.phase == TruckPhase.TO_MINING:
            # Truck has arrived at a mine and can begin mining
            truck.phase = TruckPhase.MINING
            truck.ready_time = current_time + self._random_mining_time_min()
            truck.time_traveling += current_time - truck.task_started_at
            truck.task_started_at = current_time
            self._insert_truck_heap(truck=truck)

        elif truck.phase == TruckPhase.MINING:
            # Truck has completed mining and can begin driving to unload
            truck.phase = TruckPhase.TO_UNLOAD
            truck.ready_time = current_time + TRUCK_TRAVEL_TIME
            truck.time_mining += current_time - truck.task_started_at
            truck.task_started_at = current_time
            self._insert_truck_heap(truck=truck)
        else:
            raise RuntimeError(
                f"Truck (id: {truck.truck_id}) is ready but in "
                f"phase {truck.phase} @ time {current_time}"
            )

    def _close(self) -> None:
        """"""

        if self._time < self._config.sim_minutes:
            raise RuntimeError(
                f"calling close at time {self._time}, "
                f"before end of sim at time {self._config.sim_minutes}"
            )

        for truck in self._trucks:
            task_time = self._time - truck.task_started_at
            if truck.phase == TruckPhase.UNLOADING:
                truck.time_unloading += task_time
            elif truck.phase in (TruckPhase.TO_UNLOAD, TruckPhase.TO_MINING):
                truck.time_traveling += task_time
            elif truck.phase == TruckPhase.MINING:
                truck.time_mining += task_time
            elif truck.phase == TruckPhase.WAITING:
                truck.time_waiting += task_time

        for station in self._stations:
            task_time = self._time - station.task_started_at
            if station.queue:
                station.time_unloading += task_time
            else:
                station.time_idle += task_time

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
