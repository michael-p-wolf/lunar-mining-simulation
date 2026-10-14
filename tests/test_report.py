from pathlib import Path

import pytest

from mining_sim.config import Config
from mining_sim.report import build_report, write_report
from mining_sim.simulation import Simulation


@pytest.mark.parametrize(
    "config",
    [
        Config(seed=3),
        Config(num_trucks=1, num_stations=1, seed=3),
        Config(num_trucks=10, num_stations=1, seed=3),
        Config(sim_hours=1, seed=3),  # zero unloads
    ],
)
def test_build_report(config: Config) -> None:
    trucks, stations = Simulation(config=config).run()
    report = build_report(config=config, trucks=trucks, stations=stations, sim_time=0.5)

    header = (
        f"{config.num_trucks} trucks, {config.num_stations} stations, "
        f"{config.sim_hours} hours simulated, seed = 3"
    )
    assert header in report

    total_unloads = sum(t.total_unloads for t in trucks)
    assert f"Completed unloads: {total_unloads} " in report


def test_write_report(tmp_path: Path) -> None:
    config = Config(num_trucks=4, num_stations=2, sim_hours=5)
    directory = tmp_path / "nested" / "reports"

    path = write_report("hello report\n", config=config, directory=directory)

    assert path == directory / "report_n4_m2_t5h.txt"
    assert path.read_text(encoding="utf-8") == "hello report\n"
