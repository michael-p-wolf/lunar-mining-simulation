import time

from mining_sim.config import parse_args
from mining_sim.report import build_report, write_report
from mining_sim.simulation import Simulation


def main() -> None:
    config = parse_args()
    simulation = Simulation(config=config)

    start_time = time.perf_counter()
    trucks, stations = simulation.run()
    end_time = time.perf_counter()

    simulation_time = end_time - start_time
    sum_unloads = 0
    for truck in trucks:
        print(f"Truck {truck.truck_id}:")
        print(f"\ttotal unloads: {truck.total_unloads}")
        sum_unloads += truck.total_unloads

    sum_station_unloads = 0
    for station in stations:
        print(f"Station {station.station_id}:")
        print(f"\ttrucks unloaded: {station.trucks_unloaded}")
        sum_station_unloads += station.trucks_unloaded

    print(f"sum truck unloads == sum station unloads: {sum_unloads} == {sum_station_unloads}")

    write_report(
        build_report(config=config, trucks=trucks, stations=stations, sim_time=simulation_time),
        config=config,
    )


if __name__ == "__main__":
    main()
