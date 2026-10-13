"""Build and write the simulation summary report."""

from pathlib import Path

from mining_sim.config import Config
from mining_sim.station import Station
from mining_sim.truck import Truck


def _pct(minutes: float, total_minutes: int) -> str:
    """Format a share of the simulation as a percentage."""
    return f"{minutes / total_minutes * 100:.2f}%"


def _truck_ids(trucks: list[Truck]) -> str:
    return ", ".join(f"#{t.truck_id}" for t in trucks)


def _station_ids(stations: list[Station]) -> str:
    return ", ".join(f"#{s.station_id}" for s in stations)


def build_report(
    config: Config,
    trucks: list[Truck],
    stations: list[Station],
    sim_time: float,
) -> str:
    """Return the full report as a string."""
    sim = config.sim_minutes
    n = len(trucks)
    m = len(stations)

    # --- Truck aggregates ---
    total_unloads = sum(t.total_unloads for t in trucks)

    max_truck_unloads = max(t.total_unloads for t in trucks)
    min_truck_unloads = min(t.total_unloads for t in trucks)
    trucks_most_unloads = [t for t in trucks if t.total_unloads == max_truck_unloads]
    trucks_least_unloads = [t for t in trucks if t.total_unloads == min_truck_unloads]

    # Compare raw minutes (ints), not floats, so ties are exact
    min_wait = min(t.time_waiting for t in trucks)
    max_wait = max(t.time_waiting for t in trucks)
    trucks_least_waiting = [t for t in trucks if t.time_waiting == min_wait]
    trucks_most_waiting = [t for t in trucks if t.time_waiting == max_wait]

    # --- Station aggregates ---
    total_station_unloads = sum(s.trucks_unloaded for s in stations)

    max_station_unloads = max(s.trucks_unloaded for s in stations)
    min_station_unloads = min(s.trucks_unloaded for s in stations)
    stations_most_unloads = [s for s in stations if s.trucks_unloaded == max_station_unloads]
    stations_least_unloads = [s for s in stations if s.trucks_unloaded == min_station_unloads]

    min_idle = min(s.time_idle for s in stations)
    max_idle = max(s.time_idle for s in stations)
    stations_least_idle = [s for s in stations if s.time_idle == min_idle]
    stations_most_idle = [s for s in stations if s.time_idle == max_idle]

    lines: list[str] = [
        " ----- Simulation Report -----",
        f"{config.num_trucks} trucks, {config.num_stations} stations, "
        f"{config.sim_hours} hours simulated, seed = {config.seed}",
        f"Completed unloads: {total_unloads} (simulated in {sim_time:.5f}s of real time)",
        "",
        # --- Overall trucks ---
        " --- Overall Truck Statistics ---",
        f"Average unloads per truck: {total_unloads / n:.2f} "
        f"(min {min_truck_unloads}, max {max_truck_unloads})",
        "Average share of time spent:",
        f"\tMining: {_pct(sum(t.time_mining for t in trucks) / n, sim)}",
        f"\tWaiting: {_pct(sum(t.time_waiting for t in trucks) / n, sim)}",
        f"\tUnloading: {_pct(sum(t.time_unloading for t in trucks) / n, sim)}",
        f"\tTraveling: {_pct(sum(t.time_traveling for t in trucks) / n, sim)}",
        "",
        f"Most unloads ({max_truck_unloads}): {_truck_ids(trucks_most_unloads)}",
        f"Fewest unloads ({min_truck_unloads}): {_truck_ids(trucks_least_unloads)}",
        f"Least time waiting ({_pct(min_wait, sim)}): {_truck_ids(trucks_least_waiting)}",
        f"Most time waiting ({_pct(max_wait, sim)}): {_truck_ids(trucks_most_waiting)}",
        "",
        # --- Overall stations ---
        " --- Overall Station Statistics ---",
        f"Average unloads per station: {total_station_unloads / m:.2f} "
        f"(min {min_station_unloads}, max {max_station_unloads})",
        "Average share of time spent:",
        f"\tIdle: {_pct(sum(s.time_idle for s in stations) / m, sim)}",
        f"\tUnloading: {_pct(sum(s.time_unloading for s in stations) / m, sim)}",
        "",
        f"Most unloads ({max_station_unloads}): {_station_ids(stations_most_unloads)}",
        f"Fewest unloads ({min_station_unloads}): {_station_ids(stations_least_unloads)}",
        f"Lowest time idle ({_pct(min_idle, sim)}): {_station_ids(stations_least_idle)}",
        f"Highest time idle ({_pct(max_idle, sim)}): {_station_ids(stations_most_idle)}",
        "",
        # --- Individual trucks ---
        " --- Individual Trucks ---",
    ]

    for t in trucks:
        lines += [
            f"**Truck #{t.truck_id}: {t.total_unloads} unloads",
            f"\tMining: {_pct(t.time_mining, sim)}",
            f"\tWaiting: {_pct(t.time_waiting, sim)}",
            f"\tUnloading: {_pct(t.time_unloading, sim)}",
            f"\tTraveling: {_pct(t.time_traveling, sim)}",
            "",
        ]

    lines += ["", " --- Individual Stations ---"]

    for s in stations:
        lines += [
            f"**Station #{s.station_id}: {s.trucks_unloaded} unloads",
            f"\tIdle: {_pct(s.time_idle, sim)}",
            f"\tUnloading: {_pct(s.time_unloading, sim)}",
            "",
        ]

    return "\n".join(lines) + "\n"


def write_report(report: str, config: Config, directory: Path = Path("reports")) -> Path:
    """Write the report to a file and return its path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = (
        directory / f"report_n{config.num_trucks}_m{config.num_stations}_t{config.sim_hours}h.txt"
    )
    path.write_text(report, encoding="utf-8")
    return path
