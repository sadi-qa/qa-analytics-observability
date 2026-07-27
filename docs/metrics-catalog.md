# QA Metrics Catalog

## Purpose

This document defines the QA metrics used in the Power BI and Grafana dashboards.

## 1. Test Pass Rate

Measures the percentage of executed tests that passed.

```text
Pass Rate = Passed Tests / Executed Tests × 100
```

Executed tests exclude skipped tests.

Higher values normally indicate better test stability.

## 2. Test Failure Rate

Measures the percentage of executed tests that failed.

```text
Failure Rate = Failed Tests / Executed Tests × 100
```

A high failure rate requires investigation before release.

## 3. Automation Coverage

Measures how much of the automation-eligible test scope is automated.

```text
Automation Coverage = Automated Eligible Tests / Total Eligible Tests × 100
```

Tests that cannot reasonably be automated should not reduce this metric.

## 4. Flaky-Test Rate

Measures tests that produce inconsistent results without a confirmed product change.

```text
Flaky-Test Rate = Flaky Tests / Automated Tests × 100
```

A flaky test may pass and fail across repeated executions.

## 5. Average Test Duration

Measures the average execution time of completed tests.

```text
Average Duration = Total Execution Duration / Completed Executions
```

This metric helps identify increasing pipeline execution time.

## 6. Defects by Severity

Groups defects by business and technical impact.

Planned severity values:

- Critical
- High
- Medium
- Low

Critical and high defects receive the highest release attention.

## 7. Defects by Module

Groups defects by application area.

Planned modules:

- Authentication
- Product Catalog
- Cart
- Checkout
- Payment
- User Account

This metric helps identify high-risk application areas.

## 8. Defect Reopen Rate

Measures defects reopened after being marked resolved or closed.

```text
Reopen Rate = Reopened Defects / Resolved Defects × 100
```

A high reopen rate may indicate incomplete fixes or weak regression testing.

## 9. Defect Leakage

Measures defects discovered after production release.

```text
Defect Leakage = Production Defects / Total Confirmed Defects × 100
```

Lower leakage normally indicates stronger pre-release testing.

## 10. Release Readiness Score

Provides a simplified quality-health indicator for portfolio reporting.

The planned score uses:

- Pass rate
- Automation coverage
- Flaky-test rate
- Open critical defects
- Defect leakage

The score will not replace a real release decision.

Release approval must also consider:

- Business risk
- Unresolved defects
- Test coverage
- Environment stability
- Stakeholder approval

## Metric Interpretation Rules

- Metrics must be reviewed together, not individually.
- A high pass rate does not prove complete test coverage.
- Automation coverage does not measure test quality.
- Low defect counts may indicate weak testing.
- Historical trends are more useful than isolated values.
- Dashboard values must be traceable to source data.

## Planned Dashboard Thresholds

| Metric | Healthy | Warning | Critical |
|---|---:|---:|---:|
| Pass rate | 95% or higher | 90% to 94.99% | Below 90% |
| Automation coverage | 80% or higher | 60% to 79.99% | Below 60% |
| Flaky-test rate | Below 2% | 2% to 5% | Above 5% |
| Defect leakage | Below 5% | 5% to 10% | Above 10% |
| Open critical defects | 0 | 1 | More than 1 |

## Data Quality Requirements

Metric calculations must reject or flag:

- Missing identifiers
- Duplicate identifiers
- Unsupported status values
- Unsupported severity values
- Negative execution durations
- Invalid dates
- Broken relationships between datasets