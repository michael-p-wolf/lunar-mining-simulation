from mining_sim.config import Config
from mining_sim.station import Station
from mining_sim.truck import Truck


def create_report(
    config: Config, trucks: list[Truck], stations: list[Station], sim_time: float
) -> None:
    filename = (
        f"reports/report_n{config.num_trucks}_m{config.num_stations}_t{config.sim_hours}h.txt"
    )

    # statistics to compute
    # 1) overall: n, m, t, total trucks unloaded, config, seed, and time
    #
    # 2) overall for trucks: Average total_unloads, average % time mining,
    #    traveling, unloading, waiting
    # Best Truck: most unloads
    # truck with least % waiting time
    #
    # 3) overall for stations, average trucks_unloaded, average time_unloading and time_idle
    # station with the most trucks unloaded
    # station with least % idle time
    #
    # 4) individual truck
    # for truck in trucks:
    #   total_unloads, % of time_*, average mining duration (time_mining / total_unloads)
    #   avg unload duration (may not be totally accurate)
    #
    # 5) individual station
    # for station in stations:
    #   trucks unloaded, % time_*, average time to unload truck
    #   (time_unloading / trucks_unloaded) same as above

    total_trucks_unloaded = 0

    with open(filename, "w") as f:
        f.write(
            f"Simulation Report:\n"
            f"{config.num_trucks} trucks, {config.num_stations} stations, "
            f"{config.sim_hours} hours simulated, seed = {config.seed}\n"
            f"Simulated unloading of {total_trucks_unloaded} trucks "
            f"in {sim_time:.3f}s of real time\n"
        )
