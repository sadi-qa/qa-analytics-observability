# QA Analytics and Observability

A professional QA portfolio project demonstrating software-quality data generation, validation, historical analytics, release-risk assessment, and live test observability.

The project uses deterministic synthetic QA data to model releases, test cases, executions, defects, automation coverage, flaky tests, and release-readiness indicators without exposing confidential production information.

## Project Highlights

- Synthetic QA dataset generation with Python
- Data-quality validation and automated tests with pytest
- Historical QA analytics with Power BI and DAX
- Live QA metrics exposed through a Python Prometheus exporter
- Prometheus time-series collection and target monitoring
- Provisioned Grafana datasource and dashboard-as-code
- Dockerized local observability stack
- Secure local credential handling with `.env`
- Documented metric definitions, architecture, validation, and troubleshooting

## Architecture

```text
                    Synthetic QA Data
                            |
                +-----------+-----------+
                |                       |
                v                       v
          CSV Historical Data     Python Metrics Exporter
                |                       |
                v                       v
             Power BI               Prometheus
                |                       |
                v                       v
      Historical QA Analytics      Grafana
                                        |
                                        v
                              Live QA Observability
```

## Technology Stack

### Data and Testing

- Python 3
- pandas
- pytest
- prometheus-client

### Analytics and Observability

- Power BI Desktop
- DAX
- Prometheus
- Grafana

### DevOps and Tooling

- Docker
- Docker Compose
- Git
- PowerShell

### Planned

- GitHub Actions

## QA Metrics

The project calculates and visualizes:

- Test pass rate
- Test failure rate
- Test execution status
- Average execution duration
- Automation coverage
- Automation gap
- Flaky-test rate
- Defects by severity
- Defects by status
- Defects by module
- Defects by detection phase
- Defect reopen rate
- Defect leakage
- Open critical defects
- Release-readiness score

## Verified Dataset

The deterministic dataset contains:

| Dataset | Rows |
|---|---:|
| Releases | 6 |
| Test cases | 72 |
| Test executions | 432 |
| Defects | 25 |

## Verified Results

| Metric | Result |
|---|---:|
| Data-validation errors | 0 |
| Automated tests | 19 passed |
| Total test executions | 432 |
| Test pass rate | 91.45% |
| Automation coverage | 83.33% |
| Automation gap | 9 |
| Flaky-test rate | 3.70% |
| Average test duration | 13.09 seconds |
| Total defects | 25 |
| Open critical defects | 1 |
| Defect leakage | 4.00% |
| Release-readiness score | 87.09 |

## Power BI Dashboard

The Power BI report provides historical analysis across releases, modules, browsers, environments, test executions, automation coverage, and defects.

### Report File

```text
dashboards/power-bi/qa-analytics-dashboard.pbix
```

### PDF Export

```text
exports/power-bi/qa-analytics-dashboard.pdf
```

### Documentation

```text
docs/power-bi-dashboard.md
```

### Report Pages

1. Executive QA Summary
2. Test Execution Analysis
3. Defect Analysis
4. Automation Coverage
5. Release Readiness

## Grafana QA Observability

The live observability stack follows this flow:

```text
QA CSV Data
    |
    v
Python Metrics Exporter
    |
    v
Prometheus
    |
    v
Grafana
```

### Dashboard Preview

![QA Test Observability Grafana dashboard](exports/grafana/qa-test-observability-dashboard.png)

### Dashboard File

```text
dashboards/grafana/qa-observability-dashboard.json
```

### Documentation

```text
docs/grafana-observability.md
```

### Dashboard Panels

The provisioned dashboard contains 13 panels covering:

- Test pass rate
- Automation coverage
- Flaky-test rate
- Open critical defects
- Defect leakage
- Release readiness
- Executions by status
- Defects by severity
- Defects by module
- Pass rate by release
- Readiness by release
- Duration by module
- Automation coverage by module

## Release-Readiness Model

The portfolio-defined release-readiness score has a maximum value of 100.

| Component | Weight |
|---|---:|
| Test pass rate | 40 |
| Automation coverage | 20 |
| Test stability | 15 |
| Defect leakage control | 15 |
| Open critical defects | 10 |

This score is a documented project assumption. It does not replace business-risk review, stakeholder approval, unresolved-defect assessment, or complete test-coverage analysis.

## Project Structure

```text
qa-analytics-observability/
├── .github/
│   └── workflows/
├── config/
│   ├── grafana/
│   │   └── provisioning/
│   │       ├── dashboards/
│   │       │   └── dashboard.yml
│   │       └── datasources/
│   │           └── prometheus.yml
│   └── prometheus/
│       └── prometheus.yml
├── dashboards/
│   ├── grafana/
│   │   └── qa-observability-dashboard.json
│   └── power-bi/
│       └── qa-analytics-dashboard.pbix
├── data/
│   ├── processed/
│   └── raw/
│       ├── defects.csv
│       ├── releases.csv
│       ├── test_cases.csv
│       └── test_executions.csv
├── docs/
│   ├── architecture.md
│   ├── data-dictionary.md
│   ├── grafana-observability.md
│   ├── metrics-catalog.md
│   └── power-bi-dashboard.md
├── exports/
│   ├── grafana/
│   │   └── qa-test-observability-dashboard.png
│   └── power-bi/
│       └── qa-analytics-dashboard.pdf
├── scripts/
│   ├── generate_qa_data.py
│   ├── qa_metrics_exporter.py
│   └── validate_qa_data.py
├── tests/
│   ├── test_data_generation.py
│   └── test_qa_metrics_exporter.py
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile.exporter
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3
- Power BI Desktop
- Docker Desktop
- Docker Compose
- Git
- PowerShell

Docker Desktop must be running with the Linux container engine before starting the observability stack.

## Local Setup

Run all commands from the repository root.

### Create a Virtual Environment

```powershell
python -m venv .venv
```

### Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

## Generate QA Data

```powershell
python scripts\generate_qa_data.py
```

Generated datasets are written to:

```text
data/raw/
```

## Validate QA Data

```powershell
python scripts\validate_qa_data.py
```

Expected result:

```text
QA data validation completed successfully.
Validation errors: 0
```

## Run Automated Tests

```powershell
python -m pytest
```

Verified result:

```text
19 passed
```

The test suite validates:

- Expected dataset sizes
- Unique identifiers
- Dataset relationships
- Test creation and execution dates
- Automation eligibility
- Supported status and browser values
- Metric formulas
- Release-readiness calculations
- Missing files and columns
- Prometheus metric publication

## Open the Power BI Report

```powershell
Start-Process "dashboards\power-bi\qa-analytics-dashboard.pbix"
```

Select **Refresh** after regenerating the CSV files.

The Power BI model currently imports local CSV paths, so the repository location should remain consistent.

## Configure Grafana Credentials

Create a local environment file:

```powershell
Copy-Item ".env.example" ".env"
```

Open the file:

```powershell
code ".env"
```

Replace the placeholder Grafana password with a strong private password.

The `.env` file is ignored by Git and must not be committed.

## Validate Docker Compose

```powershell
docker compose config --quiet
```

A successful validation produces no output.

## Start the Observability Stack

```powershell
docker compose up --detach --build
```

The stack starts:

- `qa-metrics-exporter`
- `qa-prometheus`
- `qa-grafana`

## Check Container Status

```powershell
docker compose ps
```

Expected state:

- Metrics exporter is running and healthy
- Prometheus is running
- Grafana is running

## Service URLs

| Service | URL |
|---|---|
| Grafana | `http://localhost:3000` |
| Grafana dashboard | `http://localhost:3000/d/qa-test-observability` |
| Prometheus | `http://localhost:9090` |
| Exporter metrics | `http://localhost:8000/metrics` |

## Operational Validation

### Exporter Health

```powershell
(Invoke-WebRequest "http://localhost:8000/metrics").StatusCode
```

Verified result:

```text
200
```

### Prometheus Target Health

```powershell
$response = Invoke-RestMethod "http://localhost:9090/api/v1/targets"

$response.data.activeTargets |
    Select-Object @{
        Name = "Job"
        Expression = { $_.labels.job }
    }, Health, ScrapeUrl, LastError
```

Verified target:

```text
Job: qa-metrics-exporter
Health: up
Scrape URL: http://qa-metrics-exporter:8000/metrics
```

### Grafana Health

```powershell
Invoke-RestMethod "http://localhost:3000/api/health"
```

Verified result:

```text
database: ok
version: 13.1.1
```

### Container Logs

```powershell
docker compose logs --no-color --tail 50
```

## Stop the Stack

```powershell
docker compose down
```

This removes the containers and project network while preserving the named Grafana and Prometheus volumes.

## Remove Stored Data

```powershell
docker compose down --volumes
```

This command also deletes the named volumes and their stored data. Use it only when an intentional environment reset is required.

## Documentation

- `docs/architecture.md` — analytics and observability architecture
- `docs/data-dictionary.md` — dataset columns and relationships
- `docs/metrics-catalog.md` — QA metric definitions and thresholds
- `docs/power-bi-dashboard.md` — Power BI model, measures, pages, and limitations
- `docs/grafana-observability.md` — exporter, Prometheus, Grafana, Docker, validation, and troubleshooting

## Security

- Only synthetic QA data is used.
- Grafana credentials are stored in the ignored local `.env` file.
- `.env.example` contains placeholders only.
- Passwords, tokens, API keys, private URLs, and confidential datasets must not be committed.
- The metrics exporter runs as a non-root container user.
- Grafana provisioning files and dashboard JSON are version controlled.

## Limitations

- The datasets are synthetic and intended for portfolio demonstration.
- The Power BI model uses local CSV paths.
- Automation coverage represents the current test inventory rather than a historical release snapshot.
- The release-readiness score uses project-defined weights.
- The exporter reads CSV files instead of a production CI/CD or test-management API.
- No Grafana alert rules or external notifications are currently configured.
- Prometheus history depends on the local named volume.
- GitHub Actions is not yet implemented.

## Planned Improvements

- Add GitHub Actions validation
- Add Grafana alert rules and notifications
- Publish metrics from an automated test pipeline
- Add Grafana browser, module, and environment filters
- Add Docker container vulnerability scanning
- Add HTTP integration tests for the running exporter
- Add documented backup and recovery procedures