# Shoalmate

Multi-cluster data orchestrator for GLACIATION use case 4

## Testing

By default, running `pytest` will only execute unit tests. To run unit tests, use:

```bash
pytest -m e2e
```

To run e2e tests that require real connections to external systems:

```bash
source settings.env
pytest -m "e2e"
```
