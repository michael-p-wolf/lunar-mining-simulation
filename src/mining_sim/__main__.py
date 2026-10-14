"""Main method to parse args, run sim, generate report"""

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

    path = write_report(
        build_report(config=config, trucks=trucks, stations=stations, sim_time=simulation_time),
        config=config,
    )

    print(f"Report written to {path}")


if __name__ == "__main__":
    main()
