"""Define read-only values the simulation will use"""

import argparse
from dataclasses import dataclass

# Times will be based in minutes as that is the smallest unit
TRUCK_TRAVEL_TIME = 30

# Kept as hours to preserve the 1 hour resolution
MINING_MIN_HOURS = 1
MINING_MAX_HOURS = 5

UNLOAD_MIN_TIME = 30
UNLOAD_MAX_TIME = 60

# expected unload time for truck waiting in queue at a station
AVG_UNLOAD_TIME = (UNLOAD_MIN_TIME + UNLOAD_MAX_TIME) / 2

# private defaults, should not be used elsewhere
_DEFAULT_NUM_TRUCKS = 10
_DEFAULT_NUM_STATIONS = 3
_DEFAULT_SIM_HOURS = 72
_DEFAULT_SEED = 0


@dataclass(frozen=True)
class Config:
    """Assign default values if none provided, check cli args valid"""

    num_trucks: int = _DEFAULT_NUM_TRUCKS
    num_stations: int = _DEFAULT_NUM_STATIONS
    sim_hours: int = _DEFAULT_SIM_HOURS
    seed: int = _DEFAULT_SEED

    def __post_init__(self) -> None:
        if self.num_trucks < 1:
            raise ValueError("num_trucks must be at least 1")
        if self.num_stations < 1:
            raise ValueError("num_stations must be at least 1")
        if self.sim_hours < 1:
            raise ValueError("sim_hours must be at least 1")

    @property
    def sim_minutes(self) -> int:
        return self.sim_hours * 60


def parse_args(argv: list[str] | None = None) -> Config:
    """parse cli args and create config for sim"""
    default = Config()
    parser = argparse.ArgumentParser(prog="mining_sim")
    parser.add_argument("--hours", type=int, default=default.sim_hours)
    parser.add_argument("-n", "--trucks", type=int, default=default.num_trucks)
    parser.add_argument("-m", "--stations", type=int, default=default.num_stations)
    parser.add_argument("--seed", type=int, default=default.seed)
    args = parser.parse_args(argv)
    try:
        return Config(
            num_trucks=args.trucks, num_stations=args.stations, sim_hours=args.hours, seed=args.seed
        )
    except ValueError as e:
        parser.error(str(e))
