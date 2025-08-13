# Shoalmate

Multi-cluster data orchestrator for GLACIATION use case 4.

## Development

### Prepare the local environment

1. `uv sync --dev`
2. `source .venv/bin/activate`
3. `pre-commit install`

### Run locally

1. Copy `example.env` to `.env` and substitute valid values
2. `PYTHONPATH=src python -m shoalmate.main`


### Test

Run static code validation for all files:
```bash
pre-commit run --all
```

Run unit tests:
```bash
pytest
```

To run e2e tests that require real connections to external systems.
```bash
source .env
pytest -m "e2e"
```

## Changelog

### [v0.3.1] - 2025-08-13
#### Added
- Now log records about file movement have additional debugging information.

#### Fixed
- Minute formatting in Time Simulator UI.

### [v0.3.0] - 2025-07-21
#### Added
- New virtual clock feature to select Green Energy Index values. Before this update chucnk filename was used instead.
- Web UI to control the virtual clock state.

#### Virtual Clock requirements
- Control plane
  - Simulated time
    - Value
    - Start, stop, and reset buttons
- No need to sync cluster times
- Every time tick should produce a log record
  - Real time and simulated time

### [v0.2.0] - 2025-07-03
#### Added
- Use only one year of Green Energy Index data.
- Added target backpressure feature. If the target bucket has more than 10 objects, Shoalmate will wait till it has
  less.

#### Changed
- Mypy and ruff static code checkers are added as Git hooks to the CI pipeline.
- Unit test coverage increased to 90%

### [v0.1.4] - 2025-06-25
The initial version of Shoalmate demonstrated in Integration cluster.
