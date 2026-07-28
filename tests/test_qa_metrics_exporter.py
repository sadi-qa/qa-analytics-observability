from __future__ import annotations

import random
from pathlib import Path

import pandas as pd
import pytest
from prometheus_client import (
    CollectorRegistry,
    generate_latest,
)

from scripts.generate_qa_data import (
    RANDOM_SEED,
    generate_defects,
    generate_releases,
    generate_test_cases,
    generate_test_executions,
)
from scripts.qa_metrics_exporter import (
    QAMetricsExporter,
    calculate_readiness_score,
    calculate_snapshot,
    load_datasets,
    safe_ratio,
)


@pytest.fixture
def generated_datasets() -> dict[str, pd.DataFrame]:
    """Generate deterministic QA datasets for exporter testing."""

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


def write_datasets(
    datasets: dict[str, pd.DataFrame],
    output_directory: Path,
) -> None:
    """Write test datasets using the exporter file names."""

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_names = {
        "releases": "releases.csv",
        "test_cases": "test_cases.csv",
        "test_executions": "test_executions.csv",
        "defects": "defects.csv",
    }

    for dataset_name, file_name in file_names.items():
        datasets[dataset_name].to_csv(
            output_directory / file_name,
            index=False,
        )


def test_safe_ratio_returns_zero_for_zero_denominator() -> None:
    """Verify metric calculations safely handle empty scopes."""

    assert safe_ratio(10, 0) == 0.0


def test_safe_ratio_returns_expected_decimal_ratio() -> None:
    """Verify ratios are returned as decimal values."""

    assert safe_ratio(3, 4) == pytest.approx(0.75)


def test_perfect_readiness_score_is_one_hundred() -> None:
    """Verify a healthy release receives the maximum score."""

    score = calculate_readiness_score(
        pass_rate=1.0,
        automation_coverage=1.0,
        flaky_test_rate=0.0,
        defect_leakage=0.0,
        open_critical_defects=0,
    )

    assert score == 100.0


def test_readiness_score_applies_critical_defect_penalty() -> None:
    """Verify multiple open critical defects remove that score."""

    score_without_critical_defects = calculate_readiness_score(
        pass_rate=1.0,
        automation_coverage=1.0,
        flaky_test_rate=0.0,
        defect_leakage=0.0,
        open_critical_defects=0,
    )

    score_with_multiple_critical_defects = (
        calculate_readiness_score(
            pass_rate=1.0,
            automation_coverage=1.0,
            flaky_test_rate=0.0,
            defect_leakage=0.0,
            open_critical_defects=2,
        )
    )

    assert (
        score_without_critical_defects
        - score_with_multiple_critical_defects
    ) == 10.0


def test_snapshot_matches_source_dataset_calculations(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify snapshot values are traceable to source data."""

    snapshot = calculate_snapshot(generated_datasets)

    executions = generated_datasets["test_executions"]
    test_cases = generated_datasets["test_cases"]
    defects = generated_datasets["defects"]

    executed_count = int(
        executions["status"].ne("Skipped").sum()
    )

    passed_count = int(
        executions["status"].eq("Passed").sum()
    )

    failed_count = int(
        executions["status"].eq("Failed").sum()
    )

    automation_eligible_count = int(
        test_cases["automation_eligible"].sum()
    )

    automated_count = int(
        test_cases["is_automated"].sum()
    )

    execution_details = executions.merge(
        test_cases[
            [
                "test_case_id",
                "is_automated",
            ]
        ],
        on="test_case_id",
        validate="many_to_one",
    )

    automated_execution_count = int(
        execution_details["is_automated"].sum()
    )

    flaky_execution_count = int(
        (
            execution_details["is_automated"]
            & execution_details["is_flaky"]
        ).sum()
    )

    production_defect_count = int(
        defects["detected_phase"]
        .eq("Production")
        .sum()
    )

    overall = snapshot["overall"]
    automation = snapshot["automation"]

    assert overall["total_executions"] == len(executions)
    assert overall["passed_executions"] == passed_count
    assert overall["failed_executions"] == failed_count

    assert overall["pass_rate"] == pytest.approx(
        passed_count / executed_count
    )

    assert overall["failure_rate"] == pytest.approx(
        failed_count / executed_count
    )

    assert automation["eligible_test_cases"] == (
        automation_eligible_count
    )

    assert automation["automated_test_cases"] == (
        automated_count
    )

    assert automation["coverage"] == pytest.approx(
        automated_count / automation_eligible_count
    )

    assert overall["flaky_test_rate"] == pytest.approx(
        flaky_execution_count / automated_execution_count
    )

    assert overall["total_defects"] == len(defects)

    assert overall["defect_leakage"] == pytest.approx(
        production_defect_count / len(defects)
    )

    assert overall["readiness_score"] == 87.09


def test_snapshot_contains_all_releases(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify every generated release receives metric values."""

    snapshot = calculate_snapshot(generated_datasets)

    release_names = [
        release["release_name"]
        for release in snapshot["releases"]
    ]

    assert release_names == [
        "Release 1.0",
        "Release 1.1",
        "Release 1.2",
        "Release 1.3",
        "Release 1.4",
        "Release 1.5",
    ]


def test_load_datasets_reads_expected_csv_files(
    generated_datasets: dict[str, pd.DataFrame],
    tmp_path: Path,
) -> None:
    """Verify the exporter loads a complete CSV dataset."""

    write_datasets(
        generated_datasets,
        tmp_path,
    )

    loaded_datasets = load_datasets(tmp_path)

    assert set(loaded_datasets) == {
        "releases",
        "test_cases",
        "test_executions",
        "defects",
    }

    assert len(loaded_datasets["test_executions"]) == 432
    assert len(loaded_datasets["defects"]) == 25


def test_load_datasets_rejects_missing_required_file(
    tmp_path: Path,
) -> None:
    """Verify startup fails when required data is unavailable."""

    with pytest.raises(
        FileNotFoundError,
        match="Required dataset was not found",
    ):
        load_datasets(tmp_path)


def test_load_datasets_rejects_missing_required_column(
    generated_datasets: dict[str, pd.DataFrame],
    tmp_path: Path,
) -> None:
    """Verify incomplete source schemas are rejected."""

    incomplete_datasets = {
        dataset_name: dataframe.copy()
        for dataset_name, dataframe
        in generated_datasets.items()
    }

    incomplete_datasets["test_executions"] = (
        incomplete_datasets["test_executions"].drop(
            columns=["status"]
        )
    )

    write_datasets(
        incomplete_datasets,
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match=(
            "test_executions is missing "
            "required columns: status"
        ),
    ):
        load_datasets(tmp_path)


def test_exporter_publishes_prometheus_metrics(
    generated_datasets: dict[str, pd.DataFrame],
) -> None:
    """Verify calculated values are exposed to Prometheus."""

    registry = CollectorRegistry()
    exporter = QAMetricsExporter(registry)

    snapshot = calculate_snapshot(generated_datasets)
    exporter.update(snapshot)

    metrics_output = generate_latest(
        registry
    ).decode("utf-8")

    expected_metrics = [
        "qa_exporter_last_refresh_success 1.0",
        "qa_test_pass_rate_ratio",
        "qa_test_failure_rate_ratio",
        "qa_automation_coverage_ratio",
        "qa_flaky_test_rate_ratio",
        "qa_defect_leakage_ratio",
        "qa_release_readiness_score 87.09",
        (
            'qa_test_pass_rate_by_release_ratio'
            '{release_name="Release 1.5"}'
        ),
        (
            'qa_defects_by_severity_total'
            '{severity="Critical"}'
        ),
        (
            'qa_automation_coverage_by_module_ratio'
            '{module="Authentication"}'
        ),
    ]

    for expected_metric in expected_metrics:
        assert expected_metric in metrics_output