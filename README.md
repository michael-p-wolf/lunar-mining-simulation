# lunar-mining-simulation
Simulation of a lunar Helium-3 mining operation, written as a take-home programming problem for a Vast interview.

---

## Requirements
* Python 3.11 or newer
* No runtime dependencies, standard libraries only

## Installation
Clone the repository and install it into a virtual environment:

```bash
git clone https://github.com/michael-p-wolf/lunar-mining-simulation.git
cd lunar-mining-simulation

python3 -m venv .venv
source .venv/bin/activate

pip install .
```

To install development tools pytest, ruff, mypy:

```bash
pip install -e ".[dev]"
```

## Usage
To run the simulation with the default configuration (10 trucks, 3 unloading stations, 72-hour simulation):

```bash
mining-sim
```

The simulation can also be configured with command line arguments:

```bash
mining-sim --trucks=20 --stations=6 --hours=48 --seed=99
```

### Options:
 
| Option | Short | Default | Description |
| --- | --- | --- | --- |
| `--trucks` | `-n` | 10 | Number of mining trucks (must be >= 1) |
| `--stations` | `-m` | 3 | Number of unload stations (must be >= 1) |
| `--hours` | | 72 | Simulated duration in hours (must be >= 1) |
| `--seed` | | 0 | Random seed, the same seed always produces the same results |
 
### Output:

Each run of the simulation writes a report to `reports/`, relative to the directory the command is run from, using this naming convention (default configuration): `reports/report_n10_m3_t72h.txt`. Existing reports with the same configuration are overwritten.

The required report for the default configuration is committed at that path. Because the default seed is fixed, re-running the default configuration reproduces the same statistics; only the real-time runtime line will differ.

## How the Simulation Works

Mining trucks repeat the following cycle during the simulation:  
```
Mining (1-5 hrs) -> Travel to Unload Station (30 min) -> Wait (if all unload stations are active) -> Unload (30-60 min) -> Travel to Mine (30 min) -> Repeat
```

The implementation is event driven, skipping time to when the next task completes, making the simulation faster than real time.

## Design Decisions

### Project Structure
```
lunar-mining-simulation/
├── .github/
│   └── workflows/
│       └── ci.yml              # Runs lint, format check, type check, and tests on every push
├── reports/                    
│   └── report_n10_m3_t72h.txt  # Generated report for default simulation configuration
├── src/
│   └── mining_sim/
│       ├── __init__.py         # Empty
│       ├── __main__.py         # Main method to parse cli args, run simulation, generate report
│       ├── config.py           # Parses arguments and builds read-only config entity
│       ├── report.py           # Compute simulation statistics and generate report
│       ├── simulation.py       # Public run() to run simulation and internal helpers + data structures
│       ├── station.py          # Representation of unloading station
│       └── truck.py            # Representation of mining truck
├── tests/
│   ├── test_config.py          # Tests for config entity
│   ├── test_report.py          # Tests for report generation
│   └── test_simulation.py      # Tests for simulation helpers and reasonable results
├── .gitignore
├── Makefile                    # Commands for running cli checks
├── pyproject.toml              # Configure system scripts and tools
└── README.md
```

**Simulation Engine:**
* **Event driven time:** Simulation runs faster than real time because time advances to the next time an action is required (i.e., when a truck advances phase).
* **Trucks are the only source of events:** Only trucks hold a next action time to avoid double counting of trucks finishing unloading at a station.
* **Waiting trucks are not in the next event heap:** Waiting trucks have no known next event time (unload duration is generated when unloading begins), so they live only in their station's queue until handed off.
* **Unload handoff:** If there is another truck in the station's queue when the currently-unloading truck leaves, the next truck will begin unloading and be added to the event heap.
* **Event heap ordering:** Min-heap on key: (next event time, phase priority, truck id).
* **Same minute ordering:** If two trucks have an event at the same minute, priority is given in the following order: unloading complete, arrived at unload station, arrived at mine, mining complete.
    * The key interaction is that trucks that have completed unloading leave before (although at the same time) a truck arrives.
    * This allows a station to complete unloading of a truck and begin unloading the next truck in the same time step.

**Station Selection:**
* **An unload station is free when its queue is empty.** The truck actively unloading is first in the queue of that station.
* **Earliest ready time wins:** Each station tracks the absolute time it can next begin unloading. Arriving trucks pick the station with the smallest ready time. If several stations are idle, this means the one idle the longest.
* **Estimated ready time:** Updated when a truck begins unloading, joins the waiting queue, or completes unloading.
    * Estimated ready time is accurate with 0 or 1 trucks in the queue
    * If >= 2 trucks in the queue, the estimate is: time that first truck completes unloading + average unload time (45 min) * number of trucks waiting

**Data models and structures:**
* **Config:** Frozen dataclass so it is read-only; `sim_minutes` is derived from given `sim_hours`.  
* **Min heap for next event:** Chosen for constant time peeking of minimum next event time and O(log(n)) popping and insertion.
* **Station Queues:** FIFO queue for line of trucks waiting at unload station.
* **List of trucks and stations:** Lists of mining trucks and unloading stations are maintained for two reasons:
    * Selection of unloading station with earliest ready time in O(m).
    * Returned by simulation.run() for report generation.
* **Random seeding:** Seed the RNG once to allow for repeatable results for testing.


### Assumptions
* **Station chosen on arrival:** Trucks pick the earliest station ready time when they arrive at the stations, not when leaving the mine.  Assumes unloading stations are in the same place.
* **Estimate vs Actual ready time:** Because station wait times are estimated when at least 2 trucks are in its queue, a truck can pick a worse queue.
    * Example: station 1 [55 min] vs. station 2 [5 min, est. 45 min]
    * Arriving truck will pick station 2.  If the second truck generates an unload time of > 50 minutes, station 1 was better.
    * **Per spec from Vast:** A truck cannot leave the queue once it joins.
    * **Clarification with Vast:** Unload time should be generated when the truck begins unloading, estimate should be used while waiting.
* **End of simulation:** 
    * Events that complete at the end of the simulation (e.g. t = 72 hrs) are processed.
    * In-progress tasks do not receive partial credit and time spent on that task is added to the necessary statistics field.
* **Constant helium-3 per unload:** All unloads produce the same amount of Helium-3, no matter how long mining or unloading took.
* **Same minute events:** Stations can handle multiple events in the same minute.
    * Truck 1 can complete unloading and Truck 2 can begin unloading at the same station at time `t`

## Results
Comparison of simulations with 10 trucks, 72hr sim time, default seed.  Average wall-clock runtime: 0.00067s

| Stations | Unloads | Avg truck waiting % | Avg Station idle % |
| --- | --- | --- | --- |
| 1 | 89 | 36.21% | 3.75% |
| 2 | 140 | 4.34% | 27.37% |
| 3 | 146 | 0.98% | 48.88% |

These results align with expectations:  More unloading stations increase efficiency.  Output can be measured by total unloads, truck inefficiencies by the average share spent waiting, and station inefficiencies by the average time spent idle.

## Testing
Run the full test suite:

```bash
pytest
```

Run a single file, or a single test by name:

```bash
pytest tests/test_simulation.py
pytest -k pick_station
```

Show each test name as it runs:

```bash
pytest -v
```

Run everything CI runs (lint, format check, type check, and tests):

```bash
make check
```

**Strategies:**  
* Invariants are checked rather than comparing results with expected behavior
* RNG is seeded once so tests are reproducible
* Tests are run on specific configs to force edge cases

**Invariants:**  
* Total time spent in each phase for each truck and station adds up to simulation time.  Allowed because in-progress events are closed at the end.
* Total unloads across trucks == total unloads across stations.
* Simulations under the same config are deterministic.

## Development
```bash
make format # auto-format and fix lint issues
make check  # lint, format check, type check, tests (same as CI)
```

CI (GitHub Actions) runs the same checks on Python 3.11 and 3.12 for every push and pull request.