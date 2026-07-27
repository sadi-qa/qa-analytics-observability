from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"

REQUIRED_FILES = {
    "releases": DATA_DIRECTORY / "releases.csv",
    "test_cases": DATA_DIRECTORY / "test_cases.csv",
    "test_executions": DATA_DIRECTORY / "test_executions.csv",
    "defects": DATA_DIRECTORY / "defects.csv",
}

REQUIRED_COLUMNS = {
    "releases": {
        "release_id",
        "release_name",
        "start_date",
        "release_date",
        "environment",
        "release_status",
    },
    "test_cases": {
        "test_case_id",
        "test_name",
        "module",
        "test_type",
        "priority",
        "automation_eligible",
        "is_automated",
        "owner_team",
        "created_date",
    },
    "test_executions": {
        "execution_id",
        "test_case_id",
        "release_id",
        "build_number",
        "execution_date",
        "status",
        "browser",
        "environment",
        "duration_seconds",
        "is_flaky",
        "retry_count",
    },
    "defects": {
        "defect_id",
        "release_id",
        "linked_test_case_id",
        "title",
        "module",
        "severity",
        "status",
        "detected_phase",
        "created_date",
        "resolved_date",
        "is_reopened",
        "root_cause",
    },
}

ALLOWED_VALUES = {
    "release_status": {
        "Planned",
        "In Testing",
        "Ready",
        "Released",
        "Cancelled",
    },
    "module": {
        "Authentication",
        "Product Catalog",
        "Cart",
        "Checkout",
        "Payment",
        "User Account",
    },
    "test_type": {
        "Functional",
        "Regression",
        "Smoke",
        "Integration",
        "API",
        "End-to-End",
        "Security",
        "Usability",
    },
    "priority": {
        "Critical",
        "High",
        "Medium",
        "Low",
    },
    "execution_status": {
        "Passed",
        "Failed",
        "Blocked",
        "Skipped",
    },
    "browser": {
        "Chromium",
        "Firefox",
        "WebKit",
        "API",
        "Not Applicable",
    },
    "environment": {
        "QA",
        "Staging",
        "UAT",
    },
    "severity": {
        "Critical",
        "High",
        "Medium",
        "Low",
    },
    "defect_status": {
        "Open",
        "In Progress",
        "Resolved",
        "Closed",
        "Rejected",
        "Deferred",
    },
    "detected_phase": {
        "QA",
        "UAT",
        "Production",
    },
    "root_cause": {
        "Code",
        "Requirement",
        "Configuration",
        "Test Data",
        "Environment",
        "Third-Party Integration",
    },
}


class ValidationResult:
    """Collect validation errors without stopping after the first failure."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def add_error(self, message: str) -> None:
        """Add one validation error."""

        self.errors.append(message)

    @property
    def is_valid(self) -> bool:
        """Return True when no validation errors exist."""

        return not self.errors


def load_datasets(
    result: ValidationResult,
) -> dict[str, pd.DataFrame]:
    """Load all required CSV datasets."""

    datasets: dict[str, pd.DataFrame] = {}

    for dataset_name, file_path in REQUIRED_FILES.items():
        if not file_path.exists():
            result.add_error(
                f"Missing required file: {file_path}"
            )
            continue

        try:
            datasets[dataset_name] = pd.read_csv(file_path)
        except Exception as error:
            result.add_error(
                f"Could not read {file_path.name}: {error}"
            )

    return datasets


def validate_required_columns(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Verify that each dataset contains its required columns."""

    for dataset_name, required_columns in REQUIRED_COLUMNS.items():
        dataframe = datasets.get(dataset_name)

        if dataframe is None:
            continue

        missing_columns = required_columns - set(dataframe.columns)

        if missing_columns:
            result.add_error(
                f"{dataset_name} is missing columns: "
                f"{sorted(missing_columns)}"
            )


def validate_required_values(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Verify that required fields are not empty."""

    optional_columns = {
        ("defects", "linked_test_case_id"),
        ("defects", "resolved_date"),
    }

    for dataset_name, required_columns in REQUIRED_COLUMNS.items():
        dataframe = datasets.get(dataset_name)

        if dataframe is None:
            continue

        for column in required_columns:
            if column not in dataframe.columns:
                continue

            if (dataset_name, column) in optional_columns:
                continue

            missing_count = int(
                dataframe[column].isna().sum()
            )

            if missing_count > 0:
                result.add_error(
                    f"{dataset_name}.{column} contains "
                    f"{missing_count} missing value(s)"
                )


def validate_unique_identifiers(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Verify primary identifiers are unique."""

    primary_keys = {
        "releases": "release_id",
        "test_cases": "test_case_id",
        "test_executions": "execution_id",
        "defects": "defect_id",
    }

    for dataset_name, primary_key in primary_keys.items():
        dataframe = datasets.get(dataset_name)

        if dataframe is None or primary_key not in dataframe.columns:
            continue

        duplicate_count = int(
            dataframe[primary_key].duplicated().sum()
        )

        if duplicate_count > 0:
            result.add_error(
                f"{dataset_name}.{primary_key} contains "
                f"{duplicate_count} duplicate value(s)"
            )


def validate_allowed_values(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    allowed_values: set[str],
    result: ValidationResult,
) -> None:
    """Verify one column contains only supported values."""

    if column not in dataframe.columns:
        return

    actual_values = set(
        dataframe[column].dropna().astype(str).unique()
    )

    invalid_values = actual_values - allowed_values

    if invalid_values:
        result.add_error(
            f"{dataset_name}.{column} contains unsupported "
            f"value(s): {sorted(invalid_values)}"
        )


def validate_categorical_values(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Validate status, severity, module, and similar columns."""

    releases = datasets.get("releases")
    test_cases = datasets.get("test_cases")
    executions = datasets.get("test_executions")
    defects = datasets.get("defects")

    if releases is not None:
        validate_allowed_values(
            releases,
            "releases",
            "release_status",
            ALLOWED_VALUES["release_status"],
            result,
        )

    if test_cases is not None:
        validate_allowed_values(
            test_cases,
            "test_cases",
            "module",
            ALLOWED_VALUES["module"],
            result,
        )
        validate_allowed_values(
            test_cases,
            "test_cases",
            "test_type",
            ALLOWED_VALUES["test_type"],
            result,
        )
        validate_allowed_values(
            test_cases,
            "test_cases",
            "priority",
            ALLOWED_VALUES["priority"],
            result,
        )

    if executions is not None:
        validate_allowed_values(
            executions,
            "test_executions",
            "status",
            ALLOWED_VALUES["execution_status"],
            result,
        )
        validate_allowed_values(
            executions,
            "test_executions",
            "browser",
            ALLOWED_VALUES["browser"],
            result,
        )
        validate_allowed_values(
            executions,
            "test_executions",
            "environment",
            ALLOWED_VALUES["environment"],
            result,
        )

    if defects is not None:
        validate_allowed_values(
            defects,
            "defects",
            "module",
            ALLOWED_VALUES["module"],
            result,
        )
        validate_allowed_values(
            defects,
            "defects",
            "severity",
            ALLOWED_VALUES["severity"],
            result,
        )
        validate_allowed_values(
            defects,
            "defects",
            "status",
            ALLOWED_VALUES["defect_status"],
            result,
        )
        validate_allowed_values(
            defects,
            "defects",
            "detected_phase",
            ALLOWED_VALUES["detected_phase"],
            result,
        )
        validate_allowed_values(
            defects,
            "defects",
            "root_cause",
            ALLOWED_VALUES["root_cause"],
            result,
        )


def validate_boolean_column(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    result: ValidationResult,
) -> None:
    """Verify a CSV column contains Boolean-compatible values."""

    if column not in dataframe.columns:
        return

    allowed_boolean_values = {
        "true",
        "false",
    }

    actual_values = {
        str(value).strip().lower()
        for value in dataframe[column].dropna().unique()
    }

    invalid_values = actual_values - allowed_boolean_values

    if invalid_values:
        result.add_error(
            f"{dataset_name}.{column} contains invalid Boolean "
            f"value(s): {sorted(invalid_values)}"
        )


def validate_boolean_values(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Validate all Boolean fields."""

    boolean_columns = {
        "test_cases": [
            "automation_eligible",
            "is_automated",
        ],
        "test_executions": [
            "is_flaky",
        ],
        "defects": [
            "is_reopened",
        ],
    }

    for dataset_name, columns in boolean_columns.items():
        dataframe = datasets.get(dataset_name)

        if dataframe is None:
            continue

        for column in columns:
            validate_boolean_column(
                dataframe,
                dataset_name,
                column,
                result,
            )


def validate_numeric_values(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Validate non-negative numeric execution fields."""

    executions = datasets.get("test_executions")

    if executions is None:
        return

    numeric_columns = {
        "duration_seconds": float,
        "retry_count": int,
    }

    for column, expected_type in numeric_columns.items():
        if column not in executions.columns:
            continue

        numeric_values = pd.to_numeric(
            executions[column],
            errors="coerce",
        )

        invalid_count = int(numeric_values.isna().sum())

        if invalid_count > 0:
            result.add_error(
                f"test_executions.{column} contains "
                f"{invalid_count} non-numeric value(s)"
            )
            continue

        negative_count = int((numeric_values < 0).sum())

        if negative_count > 0:
            result.add_error(
                f"test_executions.{column} contains "
                f"{negative_count} negative value(s)"
            )

        if expected_type is int:
            decimal_count = int(
                (numeric_values % 1 != 0).sum()
            )

            if decimal_count > 0:
                result.add_error(
                    f"test_executions.{column} contains "
                    f"{decimal_count} non-integer value(s)"
                )


def parse_date_column(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    result: ValidationResult,
) -> pd.Series | None:
    """Parse a date column and report invalid values."""

    if column not in dataframe.columns:
        return None

    parsed_dates = pd.to_datetime(
        dataframe[column],
        errors="coerce",
    )

    invalid_mask = (
        dataframe[column].notna()
        & parsed_dates.isna()
    )

    invalid_count = int(invalid_mask.sum())

    if invalid_count > 0:
        result.add_error(
            f"{dataset_name}.{column} contains "
            f"{invalid_count} invalid date value(s)"
        )

    return parsed_dates


def validate_dates(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Validate chronological relationships between dates."""

    releases = datasets.get("releases")
    test_cases = datasets.get("test_cases")
    executions = datasets.get("test_executions")
    defects = datasets.get("defects")

    if releases is not None:
        start_dates = parse_date_column(
            releases,
            "releases",
            "start_date",
            result,
        )
        release_dates = parse_date_column(
            releases,
            "releases",
            "release_date",
            result,
        )

        if start_dates is not None and release_dates is not None:
            invalid_count = int(
                (release_dates < start_dates).sum()
            )

            if invalid_count > 0:
                result.add_error(
                    f"releases contains {invalid_count} release(s) "
                    "where release_date is earlier than start_date"
                )

    if test_cases is not None:
        parse_date_column(
            test_cases,
            "test_cases",
            "created_date",
            result,
        )

    if executions is not None:
        parse_date_column(
            executions,
            "test_executions",
            "execution_date",
            result,
        )

    if defects is not None:
        created_dates = parse_date_column(
            defects,
            "defects",
            "created_date",
            result,
        )
        resolved_dates = parse_date_column(
            defects,
            "defects",
            "resolved_date",
            result,
        )

        if created_dates is not None and resolved_dates is not None:
            resolved_mask = resolved_dates.notna()

            invalid_count = int(
                (
                    resolved_mask
                    & (resolved_dates < created_dates)
                ).sum()
            )

            if invalid_count > 0:
                result.add_error(
                    f"defects contains {invalid_count} defect(s) "
                    "where resolved_date is earlier than created_date"
                )


def validate_foreign_keys(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Verify child records reference existing parent records."""

    required_datasets = {
        "releases",
        "test_cases",
        "test_executions",
        "defects",
    }

    if not required_datasets.issubset(datasets):
        return

    releases = datasets["releases"]
    test_cases = datasets["test_cases"]
    executions = datasets["test_executions"]
    defects = datasets["defects"]

    release_ids = set(
        releases["release_id"].dropna().astype(str)
    )
    test_case_ids = set(
        test_cases["test_case_id"].dropna().astype(str)
    )

    invalid_execution_release_ids = set(
        executions["release_id"].dropna().astype(str)
    ) - release_ids

    if invalid_execution_release_ids:
        result.add_error(
            "test_executions contains unknown release_id value(s): "
            f"{sorted(invalid_execution_release_ids)}"
        )

    invalid_execution_test_case_ids = set(
        executions["test_case_id"].dropna().astype(str)
    ) - test_case_ids

    if invalid_execution_test_case_ids:
        result.add_error(
            "test_executions contains unknown test_case_id value(s): "
            f"{sorted(invalid_execution_test_case_ids)}"
        )

    invalid_defect_release_ids = set(
        defects["release_id"].dropna().astype(str)
    ) - release_ids

    if invalid_defect_release_ids:
        result.add_error(
            "defects contains unknown release_id value(s): "
            f"{sorted(invalid_defect_release_ids)}"
        )

    linked_test_case_ids = set(
        defects["linked_test_case_id"]
        .dropna()
        .astype(str)
    )

    invalid_defect_test_case_ids = (
        linked_test_case_ids - test_case_ids
    )

    if invalid_defect_test_case_ids:
        result.add_error(
            "defects contains unknown linked_test_case_id value(s): "
            f"{sorted(invalid_defect_test_case_ids)}"
        )


def validate_automation_rules(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Verify automated tests are automation eligible."""

    test_cases = datasets.get("test_cases")

    if test_cases is None:
        return

    required_columns = {
        "automation_eligible",
        "is_automated",
    }

    if not required_columns.issubset(test_cases.columns):
        return

    eligible = (
        test_cases["automation_eligible"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    automated = (
        test_cases["is_automated"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    invalid_count = int(
        (automated & ~eligible).sum()
    )

    if invalid_count > 0:
        result.add_error(
            f"test_cases contains {invalid_count} automated "
            "test(s) that are not automation eligible"
        )


def validate_execution_chronology(
    datasets: dict[str, pd.DataFrame],
    result: ValidationResult,
) -> None:
    """Verify tests were not executed before they were created."""

    test_cases = datasets.get("test_cases")
    executions = datasets.get("test_executions")

    if test_cases is None or executions is None:
        return

    required_case_columns = {
        "test_case_id",
        "created_date",
    }

    required_execution_columns = {
        "test_case_id",
        "execution_date",
    }

    if not required_case_columns.issubset(test_cases.columns):
        return

    if not required_execution_columns.issubset(
        executions.columns
    ):
        return

    case_dates = test_cases[
        ["test_case_id", "created_date"]
    ].copy()

    execution_dates = executions[
        ["execution_id", "test_case_id", "execution_date"]
    ].copy()

    case_dates["created_date"] = pd.to_datetime(
        case_dates["created_date"],
        errors="coerce",
    )

    execution_dates["execution_date"] = pd.to_datetime(
        execution_dates["execution_date"],
        errors="coerce",
    )

    merged = execution_dates.merge(
        case_dates,
        on="test_case_id",
        how="left",
    )

    invalid_count = int(
        (
            merged["execution_date"]
            < merged["created_date"]
        ).sum()
    )

    if invalid_count > 0:
        result.add_error(
            f"test_executions contains {invalid_count} execution(s) "
            "that occurred before the test case was created"
        )


def print_dataset_summary(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Display the number of rows loaded from each dataset."""

    print("Dataset summary:")

    for dataset_name, dataframe in datasets.items():
        print(
            f"- {dataset_name}: {len(dataframe)} rows"
        )


def run_validation() -> int:
    """Run all data validation checks."""

    result = ValidationResult()

    datasets = load_datasets(result)

    validate_required_columns(datasets, result)
    validate_required_values(datasets, result)
    validate_unique_identifiers(datasets, result)
    validate_categorical_values(datasets, result)
    validate_boolean_values(datasets, result)
    validate_numeric_values(datasets, result)
    validate_dates(datasets, result)
    validate_foreign_keys(datasets, result)
    validate_automation_rules(datasets, result)
    validate_execution_chronology(datasets, result)

    print_dataset_summary(datasets)

    if result.is_valid:
        print("QA data validation completed successfully.")
        print("Validation errors: 0")
        return 0

    print("QA data validation failed.")
    print(f"Validation errors: {len(result.errors)}")

    for index, error in enumerate(result.errors, start=1):
        print(f"{index}. {error}")

    return 1


def main() -> None:
    """Execute validation and return an operating-system exit code."""

    exit_code = run_validation()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()