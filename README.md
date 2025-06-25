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


## Testing

By default, running `pytest` will only execute unit tests. To run unit tests, use:

```bash
pytest -m e2e
```

To run e2e tests that require real connections to external systems.

```bash
source .env
pytest -m "e2e"
```

You can use `example.env` to create `.env` file with credentials.
