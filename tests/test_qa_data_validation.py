from __future__ import annotations

import pandas as pd
import pytest

from scripts.validate_qa_data import (
    ValidationResult,
    validate_execution_chronology,
    validate_foreign_keys,
    validate_required_columns,
)


@pytest.fixture
def valid_datasets() -> dict[str, pd.DataFrame]:
    """Create a minimal valid dataset for validation tests."""

    releases = pd.DataFrame(
        [
            {
                "release_id": "REL-001",
                "release_name": "Release 1.0",
                "start_date": "2026-01-05",
                "release_date": "2026-01-29",
                "environment": "Staging",
                "release_status": "Released",
            }
        ]
    )

    test_cases = pd.DataFrame(
        [
            {
                "test_case_id": "TC-001",
                "test_name": "Authentication login test",
                "module": "Authentication",
                "test_type": "Functional",
                "priority": "High",
                "automation_eligible": True,
                "is_automated": True,
                "owner_team": "QA Automation",
                "created_date": "2026-01-01",
            }
        ]
    )

    test_executions = pd.DataFrame(
        [
            {
                "execution_id": "EXE-00001",
                "test_case_id": "TC-001",
                "release_id": "REL-001",
                "build_number": "BUILD-101",
                "execution_date": "2026-01-10 10:00:00",
                "status": "Passed",
                "browser": "Chromium",
                "environment": "Staging",
                "duration_seconds": 8.5,
                "is_flaky": False,
                "retry_count": 0,
            }
        ]
    )

    defects = pd.DataFrame(
        [
            {
                "defect_id": "BUG-001",
                "release_id": "REL-001",
                "linked_test_case_id": "TC-001",
                "title": "Authentication validation issue",
                "module": "Authentication",
                "severity": "Medium",
                "status": "Resolved",
                "detected_phase": "QA",
                "created_date": "2026-01-10",
                "resolved_date": "2026-01-12",
                "is_reopened": False,
                "root_cause": "Code",
            }
        ]
    )

    return {
        "releases": releases,
        "test_cases": test_cases,
        "test_executions": test_executions,
        "defects": defects,
    }


@pytest.mark.parametrize(
    ("dataset_name", "missing_column"),
    [
        ("releases", "release_id"),
        ("test_cases", "test_case_id"),
        ("test_executions", "release_id"),
        ("test_executions", "test_case_id"),
        ("defects", "release_id"),
        ("defects", "linked_test_case_id"),
    ],
)
def test_foreign_key_validation_handles_incomplete_schemas(
    valid_datasets: dict[str, pd.DataFrame],
    dataset_name: str,
    missing_column: str,
) -> None:
    """Verify missing relationship columns do not cause KeyError."""

    datasets = {
        name: dataframe.copy()
        for name, dataframe in valid_datasets.items()
    }

    datasets[dataset_name] = datasets[dataset_name].drop(
        columns=[missing_column]
    )

    result = ValidationResult()

    validate_required_columns(datasets, result)
    validate_foreign_keys(datasets, result)

    assert any(
        dataset_name in error
        and missing_column in error
        for error in result.errors
    )


def test_execution_chronology_handles_missing_execution_id(
    valid_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify chronology validation does not require execution ID."""

    datasets = {
        name: dataframe.copy()
        for name, dataframe in valid_datasets.items()
    }

    datasets["test_executions"] = datasets[
        "test_executions"
    ].drop(columns=["execution_id"])

    result = ValidationResult()

    validate_required_columns(datasets, result)
    validate_execution_chronology(datasets, result)

    assert any(
        "test_executions" in error
        and "execution_id" in error
        for error in result.errors
    )


def test_foreign_key_validation_reports_unknown_references(
    valid_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify invalid child references are reported."""

    datasets = {
        name: dataframe.copy()
        for name, dataframe in valid_datasets.items()
    }

    datasets["test_executions"].loc[
        0,
        "release_id",
    ] = "REL-999"

    datasets["defects"].loc[
        0,
        "linked_test_case_id",
    ] = "TC-999"

    result = ValidationResult()

    validate_foreign_keys(datasets, result)

    assert any(
        "unknown release_id" in error
        and "REL-999" in error
        for error in result.errors
    )

    assert any(
        "unknown linked_test_case_id" in error
        and "TC-999" in error
        for error in result.errors
    )