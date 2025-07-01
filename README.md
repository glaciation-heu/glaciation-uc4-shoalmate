# Shoalmate

Multi-cluster data orchestrator for GLACIATION use case 4.

# Todo
Defined by Alex and Orestis  on 2025-06-25
1. Add a control for the time ticking in Shoalmate
   - Control plane
     - Simulated time
       - Value
       - Start, stop, and reset buttons
     - Green Index for all custers
     - How many files in `proc/` of each cluster now
     - Tune proc/ capacity
   - No need to sync cluster times
   - Every time tick should produce a log record
     - Real time and simulated time

2. Use only one year of Green Index data
3. Backpressure when `proc/` is full


## How to develop

### Prepare the local environment

1. `uv sync --dev`
2. `source .venv/bin/activate`
3. `pre-commit install`

### Run locally

1. Copy `[example.env](example.env)` to `.env` and substitute valid values
2. `PYTHONPATH=src python -m shoalmate.main`


### Testing

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
