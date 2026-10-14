import pytest

from mining_sim.config import Config
from mining_sim.simulation import Simulation

CONFIGS = [(10, 3), (2, 1), (10, 1), (1, 1)]
SEEDS = [0, 1, 42]


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize(("num_trucks", "num_stations"), CONFIGS)
def test_time_adds_up(num_trucks: int, num_stations: int, seed: int) -> None:
    config = Config(num_trucks=num_trucks, num_stations=num_stations, seed=seed)
    trucks, stations = Simulation(config=config).run()

    for truck in trucks:
        total = truck.time_mining + truck.time_traveling + truck.time_unloading + truck.time_waiting
        assert total == config.sim_minutes, f"truck {truck.truck_id}"

    for station in stations:
        total = station.time_idle + station.time_unloading
        assert total == config.sim_minutes, f"station {station.station_id}"


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize(("num_trucks", "num_stations"), CONFIGS)
def test_unload_counts_match(num_trucks: int, num_stations: int, seed: int) -> None:
    config = Config(num_trucks=num_trucks, num_stations=num_stations, seed=seed)
    trucks, stations = Simulation(config=config).run()

    truck_unloads = sum(t.total_unloads for t in trucks)
    station_unloads = sum(s.trucks_unloaded for s in stations)
    assert truck_unloads == station_unloads
    assert truck_unloads > 0


def test_same_seed_is_deterministic() -> None:
    config = Config(seed=7)
    trucks_a, stations_a = Simulation(config=config).run()
    trucks_b, stations_b = Simulation(config=config).run()

    assert trucks_a == trucks_b
    assert stations_a == stations_b


def test_different_seeds_differ() -> None:
    trucks_a, _ = Simulation(config=Config(seed=1)).run()
    trucks_b, _ = Simulation(config=Config(seed=2)).run()

    assert trucks_a != trucks_b


@pytest.mark.parametrize("seed", SEEDS)
def test_queuing_happens_with_one_station(seed: int) -> None:
    config = Config(num_trucks=2, num_stations=1, seed=seed)
    trucks, _ = Simulation(config=config).run()

    assert any(t.time_waiting > 0 for t in trucks)


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("num_stations", [1, 2, 3])
def test_lone_truck_never_waits(num_stations: int, seed: int) -> None:
    config = Config(num_trucks=1, num_stations=num_stations, seed=seed)
    trucks, _ = Simulation(config=config).run()

    assert trucks[0].time_waiting == 0


@pytest.mark.parametrize(("num_trucks", "num_stations"), CONFIGS)
def test_short_sim_has_no_unloads(num_trucks: int, num_stations: int) -> None:
    # Earliest possible arrival at a station is 60 (min mining) + 30 (travel) = 90 minutes
    config = Config(num_trucks=num_trucks, num_stations=num_stations, sim_hours=1)
    trucks, stations = Simulation(config=config).run()

    for truck in trucks:
        assert truck.total_unloads == 0
        total = truck.time_mining + truck.time_traveling + truck.time_unloading + truck.time_waiting
        assert total == 60

    for station in stations:
        assert station.trucks_unloaded == 0
        assert station.time_idle == 60


# Pretend the current time is 100: an estimate below 100 is the time an idle station
# went idle, an estimate above 100 is when a busy station expects to be free
@pytest.mark.parametrize(
    ("estimates", "expected_id"),
    [
        pytest.param([70, 90, 40], 2, id="longest_idle_wins"),
        pytest.param([130, 95, 160], 1, id="idle_beats_busy"),
        pytest.param([150, 175, 120], 2, id="lowest_estimate_among_busy"),
        pytest.param([130, 90, 90], 1, id="tie_goes_to_lowest_id"),
    ],
)
def test_pick_station(estimates: list[float], expected_id: int) -> None:
    sim = Simulation(config=Config(num_stations=3))
    for station, estimate in zip(sim._stations, estimates, strict=True):
        station.ready_time_estimate = estimate

    assert sim._pick_station().station_id == expected_id
