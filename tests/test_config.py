import dataclasses

import pytest

from mining_sim.config import Config


# Trivial test that default config values match Vast spec
def test_defaults() -> None:
    config = Config()
    assert config.num_trucks == 10
    assert config.num_stations == 3
    assert config.sim_hours == 72
    assert config.seed == 0
    assert config.sim_minutes == 72 * 60


# Test derived value of sim_minutes from sim_hours
def test_derived_sim_minutes() -> None:
    config = Config(sim_hours=10)
    assert config.sim_minutes == 10 * 60


# Tests to ensure that num_trucks, num_stations, sim_hours can't be given invalid values
@pytest.mark.parametrize("invalid", [-1, 0])
def test_negative_trucks(invalid: int) -> None:
    with pytest.raises(ValueError, match="num_trucks"):
        Config(num_trucks=invalid)


@pytest.mark.parametrize("invalid", [-1, 0])
def test_negative_stations(invalid: int) -> None:
    with pytest.raises(ValueError, match="num_stations"):
        Config(num_stations=invalid)


@pytest.mark.parametrize("invalid", [-1, 0])
def test_negative_hours(invalid: int) -> None:
    with pytest.raises(ValueError, match="sim_hours"):
        Config(sim_hours=invalid)


# Test that config is immutable after creation
def test_config_frozen() -> None:
    config = Config()
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.num_trucks = 1
