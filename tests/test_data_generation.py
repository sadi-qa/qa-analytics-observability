from __future__ import annotations

import random

import pandas as pd
import pytest

from scripts.generate_qa_data import (
    RANDOM_SEED,
    generate_defects,
    generate_releases,
    generate_test_cases,
    generate_test_executions,
)


@pytest.fixture
def generated_datasets() -> dict[str, pd.DataFrame]:
    """Generate a complete deterministic QA dataset for testing."""

    random_generator = random.Random(RANDOM_SEED)

    releases = generate_releases()
    test_cases = generate_test_cases(random_generator)

    test_executions = generate_test_executions(
        random_generator,
        releases,
        test_cases,
    )

    defects = generate_defects(
        random_generator,
        test_cases,
        test_executions,
    )

    return {
        "releases": releases,
        "test_cases": test_cases,
        "test_executions": test_executions,
        "defects": defects,
    }


def test_expected_dataset_sizes(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify that the generator creates the planned data volume."""

    assert len(generated_datasets["releases"]) == 6
    assert len(generated_datasets["test_cases"]) == 72
    assert len(generated_datasets["test_executions"]) == 432
    assert len(generated_datasets["defects"]) > 0


@pytest.mark.parametrize(
    ("dataset_name", "identifier_column"),
    [
        ("releases", "release_id"),
        ("test_cases", "test_case_id"),
        ("test_executions", "execution_id"),
        ("defects", "defect_id"),
    ],
)
def test_primary_identifiers_are_unique(
    generated_datasets: dict[str, pd.DataFrame],
    dataset_name: str,
    identifier_column: str,
) -> None:
    """Verify that primary identifiers contain no duplicates."""

    dataframe = generated_datasets[dataset_name]

    assert dataframe[identifier_column].is_unique


def test_execution_foreign_keys_are_valid(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify execution records reference valid releases and tests."""

    releases = generated_datasets["releases"]
    test_cases = generated_datasets["test_cases"]
    executions = generated_datasets["test_executions"]

    release_ids = set(releases["release_id"])
    test_case_ids = set(test_cases["test_case_id"])

    assert set(executions["release_id"]).issubset(release_ids)
    assert set(executions["test_case_id"]).issubset(test_case_ids)


def test_executions_occur_after_test_creation(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify that tests are not executed before being created."""

    test_cases = generated_datasets["test_cases"][
        ["test_case_id", "created_date"]
    ].copy()

    executions = generated_datasets["test_executions"][
        ["execution_id", "test_case_id", "execution_date"]
    ].copy()

    test_cases["created_date"] = pd.to_datetime(
        test_cases["created_date"]
    )

    executions["execution_date"] = pd.to_datetime(
        executions["execution_date"]
    )

    merged = executions.merge(
        test_cases,
        on="test_case_id",
        how="left",
    )

    invalid_executions = merged[
        merged["execution_date"] < merged["created_date"]
    ]

    assert invalid_executions.empty


def test_automated_tests_are_automation_eligible(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify that non-eligible tests are never marked automated."""

    test_cases = generated_datasets["test_cases"]

    invalid_tests = test_cases[
        test_cases["is_automated"]
        & ~test_cases["automation_eligible"]
    ]

    assert invalid_tests.empty


def test_execution_values_are_valid(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify execution results and numeric values are supported."""

    executions = generated_datasets["test_executions"]

    allowed_statuses = {
        "Passed",
        "Failed",
        "Blocked",
        "Skipped",
    }

    allowed_browsers = {
        "Chromium",
        "Firefox",
        "WebKit",
        "API",
        "Not Applicable",
    }

    assert set(executions["status"]).issubset(allowed_statuses)
    assert set(executions["browser"]).issubset(allowed_browsers)
    assert (executions["duration_seconds"] >= 0).all()
    assert (executions["retry_count"] >= 0).all()