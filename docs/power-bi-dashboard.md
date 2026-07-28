# Power BI QA Analytics Dashboard

## Overview

The Power BI dashboard presents historical software quality data across multiple releases. It converts generated QA datasets into interactive views for test execution, defect analysis, automation coverage, and release-readiness assessment.

The dashboard is designed as a portfolio demonstration of practical QA analytics, data modelling, metric definition, and release-quality reporting.

## Dashboard Files

- Power BI report: `dashboards/power-bi/qa-analytics-dashboard.pbix`
- PDF export: `exports/power-bi/qa-analytics-dashboard.pdf`

## Data Sources

The report imports the following generated CSV datasets:

- `data/raw/releases.csv`
- `data/raw/test_cases.csv`
- `data/raw/test_executions.csv`
- `data/raw/defects.csv`

The datasets are generated deterministically by:

- `scripts/generate_qa_data.py`

Data quality is checked by:

- `scripts/validate_qa_data.py`
- `tests/test_data_generation.py`

## Data Model

The Power BI model contains the following primary tables:

- `releases`
- `test_cases`
- `test_executions`
- `defects`
- `QA_Metrics`
- `Severity_Lookup`
- `Detection_Phase_Lookup`
- `Priority_Lookup`

### Relationships

- `releases[release_id]` to `test_executions[release_id]`
- `releases[release_id]` to `defects[release_id]`
- `test_cases[test_case_id]` to `test_executions[test_case_id]`
- `test_cases[test_case_id]` to `defects[linked_test_case_id]`
- `Severity_Lookup[severity]` to `defects[severity]`
- `Detection_Phase_Lookup[detected_phase]` to `defects[detected_phase]`
- `Priority_Lookup[priority]` to `test_cases[priority]`

All relationships use a one-to-many structure with single-direction filtering.

## Calculated Metrics

The report includes DAX measures for:

### Test Execution

- Total Test Executions
- Passed Test Executions
- Failed Test Executions
- Executed Test Executions
- Test Pass Rate
- Test Failure Rate
- Average Test Duration Seconds

### Automation

- Automation Eligible Test Cases
- Automated Test Cases
- Automation Coverage
- Automation Gap Test Cases
- Automated Test Executions
- Flaky Test Executions
- Flaky Test Rate

### Defects

- Total Defects
- Open Critical Defects
- Production Defects
- Confirmed Defects
- Defect Leakage
- Reopened Defects
- Resolved Defects
- Defect Reopen Rate

### Release Readiness

- Release Readiness Score

## Release Readiness Formula

The readiness score is a portfolio-defined composite metric with a maximum value of 100.

| Component | Weight |
|---|---:|
| Test Pass Rate | 40 |
| Automation Coverage | 20 |
| Test Stability | 15 |
| Defect Leakage Control | 15 |
| Open Critical Defects | 10 |

The score supports release-level comparison but should not be treated as a universal industry standard. Production teams should adapt the weights and thresholds to their own risk profile and release criteria.

## Report Pages

### Executive QA Summary

Provides an overall quality overview using:

- Total test executions
- Test pass rate
- Automation coverage
- Open critical defects
- Release readiness score
- Pass-rate trend by release
- Defects by severity
- Defects by module
- Release filter

### Test Execution Analysis

Analyses execution quality using:

- Passed and failed executions
- Average execution duration
- Flaky-test rate
- Execution-status distribution
- Pass rate by browser
- Duration by module
- Failure rate by environment

### Defect Analysis

Analyses product risk using:

- Total defects
- Open critical defects
- Production defects
- Defect leakage
- Defect reopen rate
- Defects by severity
- Defects by status
- Defects by module
- Defects by detection phase

### Automation Coverage

Analyses the automated regression scope using:

- Automation-eligible test cases
- Automated test cases
- Automation coverage
- Automation gap
- Flaky-test rate
- Coverage by module
- Coverage by test type
- Coverage by priority
- Automation gap by module

### Release Readiness

Supports release-level quality evaluation using:

- Release readiness score
- Test pass rate
- Automation coverage
- Open critical defects
- Defect leakage
- Flaky-test rate
- Release filter
- Readiness score by release
- Pass rate by release
- Open critical defects by release
- Defect leakage by release

## Verified Overall Results

The completed report displays the following overall values from the generated dataset:

| Metric | Result |
|---|---:|
| Total Test Executions | 432 |
| Passed Test Executions | 396 |
| Failed Test Executions | 28 |
| Test Pass Rate | 91.45% |
| Automation Coverage | 83.33% |
| Automation Gap | 9 |
| Flaky Test Rate | 3.70% |
| Average Test Duration | 13.09 seconds |
| Total Defects | 25 |
| Open Critical Defects | 1 |
| Production Defects | 1 |
| Defect Leakage | 4.00% |
| Defect Reopen Rate | 0.00% |
| Release Readiness Score | 87.09 |

## Usage

1. Generate the QA datasets.
2. Validate the generated data.
3. Open the PBIX file in Power BI Desktop.
4. Select **Refresh** if the CSV files have changed.
5. Review the report pages and release filters.
6. Export the report to PDF when documentation output is required.

## Limitations

- The datasets are synthetic and are intended for portfolio demonstration.
- Automation coverage is calculated from the current test-case inventory and is not stored as a historical snapshot for each release.
- The release-readiness formula is a documented project assumption.
- The dashboard does not currently retrieve data from a live test-management or defect-tracking system.
- The Power BI report requires local CSV paths to remain consistent when refreshing the model.

## Portfolio Value

This dashboard demonstrates:

- QA metric definition
- Test and defect data modelling
- Power BI relationship design
- DAX measure development
- Release-quality analysis
- Risk-focused reporting
- Automation-coverage assessment
- Data validation and documentation

