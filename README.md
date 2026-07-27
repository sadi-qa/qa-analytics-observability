# QA Analytics and Observability

A portfolio project demonstrating QA metrics analysis, historical reporting, live test observability, data validation, and dashboard automation.

## Project Objectives

- Analyze software quality using practical QA metrics
- Build historical QA reports with Power BI
- Build live monitoring dashboards with Grafana
- Store time-series QA metrics in Prometheus
- Generate realistic synthetic QA data with Python
- Validate data quality and metric calculations
- Run Grafana and Prometheus with Docker Compose
- Validate the project through GitHub Actions

## Technology Stack

- Python
- Power BI Desktop
- Grafana
- Prometheus
- Docker
- Docker Compose
- Git
- GitHub Actions
- PowerShell

## Planned QA Metrics

- Test pass rate
- Test failure rate
- Automation coverage
- Flaky-test rate
- Test execution duration
- Defects by severity
- Defects by module
- Defect reopen rate
- Defect leakage
- Release readiness

## Planned Dashboards

### Power BI

Power BI will provide historical analysis across releases, modules, environments, browsers, test executions, and defects.

### Grafana

Grafana will provide live visibility into automated test execution metrics collected by Prometheus.

## Project Structure

```text
qa-analytics-observability/
├── .github/
│   └── workflows/
├── config/
│   └── grafana/
├── dashboards/
│   ├── grafana/
│   └── power-bi/
├── data/
│   ├── processed/
│   └── raw/
├── docs/
├── exports/
│   ├── grafana/
│   └── power-bi/
├── scripts/
├── tests/
├── .gitignore
└── README.md
```

## Project Status

Project initialization is in progress.

## Security

This project uses synthetic data only. Credentials, tokens, private URLs, and confidential information must not be committed.