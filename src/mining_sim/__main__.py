from mining_sim.config import parse_args
from mining_sim.simulation import Simulation


def main() -> None:
    config = parse_args()
    simulation = Simulation(config=config)
    simulation.run()


if __name__ == "__main__":
    main()
