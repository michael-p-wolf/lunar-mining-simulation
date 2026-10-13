import mining_sim
from mining_sim.__main__ import main


def test_imports() -> None:
    assert mining_sim is not None


def test_entry() -> None:
    assert callable(main)
