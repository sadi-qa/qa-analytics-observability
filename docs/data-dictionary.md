# QA Data Dictionary

## Purpose

This document defines the synthetic datasets used by Power BI, Prometheus, Grafana, and the Python validation scripts.

## Data Model

The project uses four primary datasets:

```text
releases.csv
    |
    +---- test_executions.csv ---- test_cases.csv
    |
    +---- defects.csv
```

## 1. Releases Dataset

**File path:**

```text
data/raw/releases.csv
```

| Column | Type | Required | Description | Example |
|---|---|---:|---|---|
| release_id | Text | Yes | Unique release identifier | REL-001 |
| release_name | Text | Yes | Display name of the release | Release 1.0 |
| start_date | Date | Yes | Date testing started | 2026-01-05 |
| release_date | Date | Yes | Planned or actual release date | 2026-01-30 |
| environment | Text | Yes | Main release environment | Staging |
| release_status | Text | Yes | Current release status | Released |

### Allowed release statuses

- Planned
- In Testing
- Ready
- Released
- Cancelled

## 2. Test Cases Dataset

**File path:**

```text
data/raw/test_cases.csv
```

| Column | Type | Required | Description | Example |
|---|---|---:|---|---|
| test_case_id | Text | Yes | Unique test-case identifier | TC-001 |
| test_name | Text | Yes | Test-case name | Login with valid credentials |
| module | Text | Yes | Application area being tested | Authentication |
| test_type | Text | Yes | Type of testing | Functional |
| priority | Text | Yes | Business testing priority | High |
| automation_eligible | Boolean | Yes | Whether automation is appropriate | True |
| is_automated | Boolean | Yes | Whether the test is automated | True |
| owner_team | Text | Yes | Team responsible for the test | QA Automation |
| created_date | Date | Yes | Date the test case was created | 2025-12-15 |

### Allowed modules

- Authentication
- Product Catalog
- Cart
- Checkout
- Payment
- User Account

### Allowed test types

- Functional
- Regression
- Smoke
- Integration
- API
- End-to-End
- Security
- Usability

### Allowed priorities

- Critical
- High
- Medium
- Low

## 3. Test Executions Dataset

**File path:**

```text
data/raw/test_executions.csv
```

| Column | Type | Required | Description | Example |
|---|---|---:|---|---|
| execution_id | Text | Yes | Unique execution identifier | EXE-00001 |
| test_case_id | Text | Yes | Related test-case identifier | TC-001 |
| release_id | Text | Yes | Related release identifier | REL-001 |
| build_number | Text | Yes | Application build tested | BUILD-101 |
| execution_date | DateTime | Yes | Date and time of execution | 2026-01-20 10:30:00 |
| status | Text | Yes | Test execution result | Passed |
| browser | Text | Yes | Browser used during execution | Chromium |
| environment | Text | Yes | Test environment | Staging |
| duration_seconds | Decimal | Yes | Execution duration in seconds | 12.45 |
| is_flaky | Boolean | Yes | Whether inconsistent behaviour was detected | False |
| retry_count | Integer | Yes | Number of execution retries | 0 |

### Allowed execution statuses

- Passed
- Failed
- Blocked
- Skipped

### Allowed browsers

- Chromium
- Firefox
- WebKit
- API
- Not Applicable

### Allowed environments

- QA
- Staging
- UAT

## 4. Defects Dataset

**File path:**

```text
data/raw/defects.csv
```

| Column | Type | Required | Description | Example |
|---|---|---:|---|---|
| defect_id | Text | Yes | Unique defect identifier | BUG-001 |
| release_id | Text | Yes | Release where the defect was reported | REL-001 |
| linked_test_case_id | Text | No | Test case that detected the defect | TC-001 |
| title | Text | Yes | Short defect description | Login fails with valid credentials |
| module | Text | Yes | Affected application module | Authentication |
| severity | Text | Yes | Business and technical impact | High |
| status | Text | Yes | Current defect workflow status | Open |
| detected_phase | Text | Yes | Phase where the defect was found | QA |
| created_date | Date | Yes | Date the defect was reported | 2026-01-18 |
| resolved_date | Date | No | Date the defect was resolved | 2026-01-21 |
| is_reopened | Boolean | Yes | Whether the defect was reopened | False |
| root_cause | Text | Yes | General defect cause category | Code |

### Allowed severities

- Critical
- High
- Medium
- Low

### Allowed defect statuses

- Open
- In Progress
- Resolved
- Closed
- Rejected
- Deferred

### Allowed detection phases

- QA
- UAT
- Production

### Allowed root causes

- Code
- Requirement
- Configuration
- Test Data
- Environment
- Third-Party Integration

## Dataset Relationships

| Parent dataset | Parent key | Child dataset | Foreign key | Relationship |
|---|---|---|---|---|
| releases.csv | release_id | test_executions.csv | release_id | One-to-many |
| releases.csv | release_id | defects.csv | release_id | One-to-many |
| test_cases.csv | test_case_id | test_executions.csv | test_case_id | One-to-many |
| test_cases.csv | test_case_id | defects.csv | linked_test_case_id | One-to-many |

## Derived Metrics

The following metrics will be calculated from the datasets:

- Pass rate from `test_executions.csv`
- Failure rate from `test_executions.csv`
- Automation coverage from `test_cases.csv`
- Flaky-test rate from `test_executions.csv`
- Average duration from `test_executions.csv`
- Defect reopen rate from `defects.csv`
- Defect leakage from `defects.csv`
- Release-readiness score from combined datasets

## Data Quality Rules

- Every primary identifier must be unique.
- Every required field must contain a value.
- Foreign keys must match an existing parent record.
- Execution duration cannot be negative.
- Retry count cannot be negative.
- Release date cannot be earlier than start date.
- Resolved date cannot be earlier than created date.
- Automated tests must also be automation eligible.
- Production defects count toward defect leakage.
- Unsupported status, module, severity, browser, or environment values must be rejected.