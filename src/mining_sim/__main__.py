from mining_sim.config import parse_args


def main() -> None:
    config = parse_args()
    print(config)
    print(config.sim_minutes)


if __name__ == "__main__":
    main()
