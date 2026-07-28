# QA Analytics and Observability

A QA portfolio project demonstrating software-quality data generation, validation, historical reporting, release-risk analysis, and planned live test observability.

The project uses synthetic QA data to model test executions, defects, automation coverage, flaky tests, and release-readiness indicators without exposing confidential production information.

## Current Implementation

The following components are implemented and verified:

- Deterministic synthetic QA data generation with Python
- Release, test-case, test-execution, and defect datasets
- Dataset validation for schema, relationships, dates, and business rules
- Automated data-quality tests with pytest
- Historical QA analytics dashboard built with Power BI
- Documented DAX metrics and release-readiness calculation
- PDF export of the completed Power BI report

Grafana, Prometheus, Docker Compose, and GitHub Actions are planned as the next project milestones.

## Technology Stack

### Implemented

- Python 3
- pandas
- pytest
- Power BI Desktop
- DAX
- Git
- PowerShell

### Planned

- Grafana
- Prometheus
- Docker
- Docker Compose
- GitHub Actions

## QA Metrics

The project currently analyses:

- Test pass rate
- Test failure rate
- Automation coverage
- Automation gap
- Flaky-test rate
- Average test execution duration
- Defects by severity
- Defects by status
- Defects by module
- Defects by detection phase
- Defect reopen rate
- Defect leakage
- Open critical defects
- Release-readiness score

## Power BI Dashboard

The Power BI report is available at:

```text
dashboards/power-bi/qa-analytics-dashboard.pbix
```

A static PDF export is available at:

```text
exports/power-bi/qa-analytics-dashboard.pdf
```

Detailed dashboard documentation is available at:

```text
docs/power-bi-dashboard.md
```

### Report Pages

The report contains five pages:

1. Executive QA Summary
2. Test Execution Analysis
3. Defect Analysis
4. Automation Coverage
5. Release Readiness

### Release-Readiness Model

The portfolio-defined release-readiness score uses the following weighted components:

| Component | Weight |
|---|---:|
| Test pass rate | 40 |
| Automation coverage | 20 |
| Test stability | 15 |
| Defect leakage control | 15 |
| Open critical defects | 10 |

The readiness score is a documented project assumption rather than a universal industry standard.

## Verified Dataset

The generated dataset contains:

| Dataset | Rows |
|---|---:|
| Releases | 6 |
| Test cases | 72 |
| Test executions | 432 |
| Defects | 25 |

Verified results:

| Metric | Result |
|---|---:|
| Data validation errors | 0 |
| Automated tests | 9 passed |
| Test pass rate | 91.45% |
| Automation coverage | 83.33% |
| Flaky-test rate | 3.70% |
| Total defects | 25 |
| Open critical defects | 1 |
| Defect leakage | 4.00% |
| Release-readiness score | 87.09 |

## Project Structure

```text
qa-analytics-observability/
├── .github/
│   └── workflows/
├── config/
│   └── grafana/
│       ├── dashboards/
│       └── provisioning/
├── dashboards/
│   ├── grafana/
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
│   ├── metrics-catalog.md
│   └── power-bi-dashboard.md
├── exports/
│   ├── grafana/
│   └── power-bi/
│       └── qa-analytics-dashboard.pdf
├── scripts/
│   ├── generate_qa_data.py
│   └── validate_qa_data.py
├── tests/
│   └── test_data_generation.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3
- Power BI Desktop
- Git
- PowerShell

Docker Desktop will be required for the planned Grafana and Prometheus implementation.

## Local Setup

Run the following commands from the repository root.

### Create the virtual environment

```powershell
python -m venv .venv
```

### Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## Generate QA Data

```powershell
python scripts\generate_qa_data.py
```

The command creates deterministic CSV datasets under:

```text
data/raw/
```

## Validate QA Data

```powershell
python scripts\validate_qa_data.py
```

Expected successful result:

```text
QA data validation completed successfully.
Validation errors: 0
```

## Run Automated Tests

```powershell
python -m pytest
```

The test suite validates dataset creation, required columns, row counts, identifiers, relationships, dates, and business rules.

## Open the Power BI Report

```powershell
Start-Process "dashboards\power-bi\qa-analytics-dashboard.pbix"
```

Select **Refresh** in Power BI Desktop after regenerating the CSV files.

The local repository path should remain consistent because the Power BI model currently imports local CSV sources.

## Documentation

- `docs/architecture.md` — analytics and observability architecture
- `docs/data-dictionary.md` — dataset columns and relationships
- `docs/metrics-catalog.md` — QA metric definitions
- `docs/power-bi-dashboard.md` — Power BI model, measures, report pages, and limitations

## Limitations

- All datasets are synthetic and intended for portfolio demonstration.
- Automation coverage represents the current test-case inventory rather than a historical snapshot for every release.
- The release-readiness score uses project-defined weights.
- The Power BI model currently uses local CSV file paths.
- Grafana, Prometheus, Docker Compose, and GitHub Actions are not yet implemented.

## Planned Improvements

- Expose QA metrics through a Prometheus-compatible Python service
- Provision Prometheus and Grafana with Docker Compose
- Build live Grafana test-observability dashboards
- Add automated validation through GitHub Actions
- Export and document Grafana dashboards
- Add dashboard screenshots for repository presentation

## Security

This project uses synthetic data only.

Passwords, tokens, API keys, private URLs, confidential datasets, and local environment files must not be committed.
