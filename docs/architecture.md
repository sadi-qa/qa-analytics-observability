# Project Architecture

## Purpose

This project separates historical QA analysis from live QA monitoring.

## Data Flow

```text
Synthetic QA Data
        |
        v
Python Data Generator
        |
        +----------------------+
        |                      |
        v                      v
CSV Files              Prometheus Metrics
        |                      |
        v                      v
Power BI                   Grafana
        |                      |
        v                      v
Historical Reports       Live Monitoring
```

## Components

### Python Data Generator

Creates realistic synthetic data for:

- Releases
- Test cases
- Test executions
- Defects
- Automation coverage
- Flaky tests

### CSV Data

Stores historical QA data used by Power BI.

### Power BI

Used for:

- Release comparison
- Test execution trends
- Defect analysis
- Automation coverage
- Release-readiness reporting

### Prometheus

Stores time-series QA metrics produced by the Python metrics exporter.

### Grafana

Queries Prometheus and displays live QA monitoring dashboards.

### Docker Compose

Runs Prometheus and Grafana as local containers.

### GitHub Actions

Validates:

- Python code
- Data structure
- Metric calculations
- Docker Compose configuration
- Required project files

## Analytics and Observability

### QA Analytics

Answers historical questions such as:

- Did test quality improve between releases?
- Which module produced the most defects?
- Is automation coverage increasing?
- Which browsers have the highest failure rate?

### QA Observability

Answers current-state questions such as:

- Are automated tests currently passing?
- Is test duration increasing?
- Are failures concentrated in one module?
- Is the release-readiness score below the threshold?

## Security

Only synthetic data will be used. Secrets, credentials, private URLs, and confidential information must not be stored in the repository.