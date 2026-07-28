from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api.types import is_bool_dtype
from prometheus_client import (
    CollectorRegistry,
    Gauge,
    start_http_server,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_REFRESH_SECONDS = 30

OPEN_DEFECT_STATUSES = {
    "Open",
    "In Progress",
    "Deferred",
}

RESOLVED_DEFECT_STATUSES = {
    "Resolved",
    "Closed",
}

REQUIRED_COLUMNS = {
    "releases": {
        "release_id",
        "release_name",
        "release_status",
    },
    "test_cases": {
        "test_case_id",
        "module",
        "test_type",
        "priority",
        "automation_eligible",
        "is_automated",
    },
    "test_executions": {
        "execution_id",
        "test_case_id",
        "release_id",
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
        "module",
        "severity",
        "status",
        "detected_phase",
        "is_reopened",
    },
}


def parse_arguments() -> argparse.Namespace:
    """Parse command-line configuration for the metrics exporter."""

    parser = argparse.ArgumentParser(
        description=(
            "Expose synthetic QA analytics data as "
            "Prometheus metrics."
        )
    )

    parser.add_argument(
        "--data-directory",
        type=Path,
        default=DEFAULT_DATA_DIRECTORY,
        help="Directory containing the generated QA CSV files.",
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Network interface used by the metrics HTTP server.",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port used by the Prometheus metrics endpoint.",
    )

    parser.add_argument(
        "--refresh-seconds",
        type=int,
        default=DEFAULT_REFRESH_SECONDS,
        help="Number of seconds between CSV data refreshes.",
    )

    return parser.parse_args()


def safe_ratio(
    numerator: int | float,
    denominator: int | float,
) -> float:
    """Return a decimal ratio while preventing division by zero."""

    if denominator == 0:
        return 0.0

    return float(numerator) / float(denominator)


def to_boolean_series(series: pd.Series) -> pd.Series:
    """Convert supported CSV boolean values into real booleans."""

    if is_bool_dtype(series):
        return series.fillna(False).astype(bool)

    normalized_values = (
        series.astype(str)
        .str.strip()
        .str.lower()
    )

    allowed_values = {
        "true",
        "false",
        "1",
        "0",
        "yes",
        "no",
    }

    invalid_values = normalized_values[
        ~normalized_values.isin(allowed_values)
    ]

    if not invalid_values.empty:
        unique_invalid_values = sorted(
            invalid_values.unique().tolist()
        )

        raise ValueError(
            "Unsupported boolean values found: "
            f"{unique_invalid_values}"
        )

    return normalized_values.isin(
        {
            "true",
            "1",
            "yes",
        }
    )


def validate_dataset_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Verify that one dataset contains all required columns."""

    required_columns = REQUIRED_COLUMNS[dataset_name]
    missing_columns = required_columns.difference(
        dataframe.columns
    )

    if missing_columns:
        formatted_columns = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{formatted_columns}"
        )


def load_datasets(
    data_directory: Path,
) -> dict[str, pd.DataFrame]:
    """Load and validate the QA datasets from CSV files."""

    dataset_files = {
        "releases": "releases.csv",
        "test_cases": "test_cases.csv",
        "test_executions": "test_executions.csv",
        "defects": "defects.csv",
    }

    datasets: dict[str, pd.DataFrame] = {}

    for dataset_name, file_name in dataset_files.items():
        file_path = data_directory / file_name

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Required dataset was not found: {file_path}"
            )

        dataframe = pd.read_csv(file_path)

        validate_dataset_columns(
            dataset_name,
            dataframe,
        )

        datasets[dataset_name] = dataframe

    return datasets


def calculate_readiness_score(
    pass_rate: float,
    automation_coverage: float,
    flaky_test_rate: float,
    defect_leakage: float,
    open_critical_defects: int,
) -> float:
    """Calculate the documented release-readiness score."""

    pass_rate_score = pass_rate * 40
    automation_score = automation_coverage * 20

    stability_score = max(
        0.0,
        1.0 - flaky_test_rate,
    ) * 15

    leakage_score = max(
        0.0,
        1.0 - defect_leakage,
    ) * 15

    if open_critical_defects == 0:
        critical_defect_score = 10
    elif open_critical_defects == 1:
        critical_defect_score = 5
    else:
        critical_defect_score = 0

    return round(
        pass_rate_score
        + automation_score
        + stability_score
        + leakage_score
        + critical_defect_score,
        2,
    )


def calculate_scope_metrics(
    test_executions: pd.DataFrame,
    defects: pd.DataFrame,
    test_cases: pd.DataFrame,
    automation_coverage: float,
) -> dict[str, float]:
    """Calculate QA metrics for the supplied execution scope."""

    execution_statuses = test_executions["status"]

    total_executions = len(test_executions)

    passed_executions = int(
        execution_statuses.eq("Passed").sum()
    )

    failed_executions = int(
        execution_statuses.eq("Failed").sum()
    )

    executed_executions = int(
        execution_statuses.ne("Skipped").sum()
    )

    average_duration_seconds = (
        float(test_executions["duration_seconds"].mean())
        if total_executions > 0
        else 0.0
    )

    execution_details = test_executions.merge(
        test_cases[
            [
                "test_case_id",
                "is_automated",
            ]
        ],
        on="test_case_id",
        how="left",
        validate="many_to_one",
    )

    if execution_details["is_automated"].isna().any():
        raise ValueError(
            "One or more executions reference an unknown test case."
        )

    automated_execution_flags = to_boolean_series(
        execution_details["is_automated"]
    )

    flaky_execution_flags = to_boolean_series(
        execution_details["is_flaky"]
    )

    automated_executions = int(
        automated_execution_flags.sum()
    )

    flaky_executions = int(
        (
            automated_execution_flags
            & flaky_execution_flags
        ).sum()
    )

    defect_statuses = defects["status"]
    defect_severities = defects["severity"]
    detection_phases = defects["detected_phase"]

    open_critical_defects = int(
        (
            defect_severities.eq("Critical")
            & defect_statuses.isin(
                OPEN_DEFECT_STATUSES
            )
        ).sum()
    )

    production_defects = int(
        detection_phases.eq("Production").sum()
    )

    confirmed_defects = int(
        defect_statuses.ne("Rejected").sum()
    )

    reopened_defects = int(
        to_boolean_series(
            defects["is_reopened"]
        ).sum()
    )

    resolved_defects = int(
        defect_statuses.isin(
            RESOLVED_DEFECT_STATUSES
        ).sum()
    )

    pass_rate = safe_ratio(
        passed_executions,
        executed_executions,
    )

    failure_rate = safe_ratio(
        failed_executions,
        executed_executions,
    )

    flaky_test_rate = safe_ratio(
        flaky_executions,
        automated_executions,
    )

    defect_leakage = safe_ratio(
        production_defects,
        confirmed_defects,
    )

    defect_reopen_rate = safe_ratio(
        reopened_defects,
        resolved_defects,
    )

    readiness_score = calculate_readiness_score(
        pass_rate=pass_rate,
        automation_coverage=automation_coverage,
        flaky_test_rate=flaky_test_rate,
        defect_leakage=defect_leakage,
        open_critical_defects=open_critical_defects,
    )

    return {
        "total_executions": float(total_executions),
        "passed_executions": float(passed_executions),
        "failed_executions": float(failed_executions),
        "executed_executions": float(executed_executions),
        "pass_rate": pass_rate,
        "failure_rate": failure_rate,
        "average_duration_seconds": (
            average_duration_seconds
        ),
        "automated_executions": float(
            automated_executions
        ),
        "flaky_executions": float(flaky_executions),
        "flaky_test_rate": flaky_test_rate,
        "total_defects": float(len(defects)),
        "open_critical_defects": float(
            open_critical_defects
        ),
        "production_defects": float(
            production_defects
        ),
        "defect_leakage": defect_leakage,
        "reopened_defects": float(reopened_defects),
        "resolved_defects": float(resolved_defects),
        "defect_reopen_rate": defect_reopen_rate,
        "readiness_score": readiness_score,
    }


def calculate_snapshot(
    datasets: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Calculate global, release, and breakdown metrics."""

    releases = datasets["releases"]
    test_cases = datasets["test_cases"].copy()
    test_executions = datasets[
        "test_executions"
    ].copy()
    defects = datasets["defects"].copy()

    automation_eligible_flags = to_boolean_series(
        test_cases["automation_eligible"]
    )

    automated_test_flags = to_boolean_series(
        test_cases["is_automated"]
    )

    automation_eligible_test_cases = int(
        automation_eligible_flags.sum()
    )

    automated_test_cases = int(
        automated_test_flags.sum()
    )

    automation_coverage = safe_ratio(
        automated_test_cases,
        automation_eligible_test_cases,
    )

    automation_gap = (
        automation_eligible_test_cases
        - automated_test_cases
    )

    overall_metrics = calculate_scope_metrics(
        test_executions=test_executions,
        defects=defects,
        test_cases=test_cases,
        automation_coverage=automation_coverage,
    )

    release_metrics: list[dict[str, Any]] = []

    for release in releases.itertuples(index=False):
        release_id = str(release.release_id)
        release_name = str(release.release_name)

        release_executions = test_executions[
            test_executions["release_id"].eq(
                release_id
            )
        ]

        release_defects = defects[
            defects["release_id"].eq(release_id)
        ]

        metrics = calculate_scope_metrics(
            test_executions=release_executions,
            defects=release_defects,
            test_cases=test_cases,
            automation_coverage=automation_coverage,
        )

        release_metrics.append(
            {
                "release_name": release_name,
                **metrics,
            }
        )

    execution_status_counts = (
        test_executions["status"]
        .value_counts()
        .to_dict()
    )

    defects_by_severity = (
        defects["severity"]
        .value_counts()
        .to_dict()
    )

    defects_by_status = (
        defects["status"]
        .value_counts()
        .to_dict()
    )

    defects_by_module = (
        defects["module"]
        .value_counts()
        .to_dict()
    )

    defects_by_detection_phase = (
        defects["detected_phase"]
        .value_counts()
        .to_dict()
    )

    duration_by_module = (
        test_executions.merge(
            test_cases[
                [
                    "test_case_id",
                    "module",
                ]
            ],
            on="test_case_id",
            how="left",
            validate="many_to_one",
        )
        .groupby("module")["duration_seconds"]
        .mean()
        .to_dict()
    )

    automation_by_module: list[dict[str, Any]] = []

    for module, module_test_cases in test_cases.groupby(
        "module"
    ):
        eligible_flags = to_boolean_series(
            module_test_cases["automation_eligible"]
        )

        automated_flags = to_boolean_series(
            module_test_cases["is_automated"]
        )

        eligible_count = int(eligible_flags.sum())
        automated_count = int(automated_flags.sum())

        automation_by_module.append(
            {
                "module": str(module),
                "eligible": eligible_count,
                "automated": automated_count,
                "gap": eligible_count - automated_count,
                "coverage": safe_ratio(
                    automated_count,
                    eligible_count,
                ),
            }
        )

    return {
        "overall": overall_metrics,
        "automation": {
            "eligible_test_cases": (
                automation_eligible_test_cases
            ),
            "automated_test_cases": (
                automated_test_cases
            ),
            "coverage": automation_coverage,
            "gap": automation_gap,
        },
        "releases": release_metrics,
        "execution_status_counts": (
            execution_status_counts
        ),
        "defects_by_severity": defects_by_severity,
        "defects_by_status": defects_by_status,
        "defects_by_module": defects_by_module,
        "defects_by_detection_phase": (
            defects_by_detection_phase
        ),
        "duration_by_module": duration_by_module,
        "automation_by_module": automation_by_module,
    }


class QAMetricsExporter:
    """Own and update the Prometheus metric collectors."""

    def __init__(
        self,
        registry: CollectorRegistry,
    ) -> None:
        self.registry = registry

        self.last_refresh_success = Gauge(
            "qa_exporter_last_refresh_success",
            (
                "Whether the most recent QA dataset refresh "
                "completed successfully."
            ),
            registry=registry,
        )

        self.last_refresh_timestamp = Gauge(
            "qa_exporter_last_refresh_timestamp_seconds",
            (
                "Unix timestamp of the most recent successful "
                "QA dataset refresh."
            ),
            registry=registry,
        )

        self.test_executions_total = Gauge(
            "qa_test_executions_total",
            "Number of test executions grouped by status.",
            ["status"],
            registry=registry,
        )

        self.test_pass_rate = Gauge(
            "qa_test_pass_rate_ratio",
            (
                "Ratio of passed executions to executed "
                "non-skipped tests."
            ),
            registry=registry,
        )

        self.test_failure_rate = Gauge(
            "qa_test_failure_rate_ratio",
            (
                "Ratio of failed executions to executed "
                "non-skipped tests."
            ),
            registry=registry,
        )

        self.average_test_duration = Gauge(
            "qa_test_duration_seconds_average",
            "Average test execution duration in seconds.",
            registry=registry,
        )

        self.automation_eligible_test_cases = Gauge(
            "qa_automation_eligible_test_cases",
            "Number of test cases eligible for automation.",
            registry=registry,
        )

        self.automated_test_cases = Gauge(
            "qa_automated_test_cases",
            "Number of automated test cases.",
            registry=registry,
        )

        self.automation_coverage = Gauge(
            "qa_automation_coverage_ratio",
            (
                "Ratio of automated test cases to "
                "automation-eligible test cases."
            ),
            registry=registry,
        )

        self.automation_gap = Gauge(
            "qa_automation_gap_test_cases",
            (
                "Number of automation-eligible test cases "
                "that are not automated."
            ),
            registry=registry,
        )

        self.flaky_test_executions = Gauge(
            "qa_flaky_test_executions",
            "Number of flaky automated test executions.",
            registry=registry,
        )

        self.flaky_test_rate = Gauge(
            "qa_flaky_test_rate_ratio",
            (
                "Ratio of flaky executions to automated "
                "executions."
            ),
            registry=registry,
        )

        self.total_defects = Gauge(
            "qa_defects_total",
            "Total number of defects.",
            registry=registry,
        )

        self.open_critical_defects = Gauge(
            "qa_open_critical_defects",
            "Number of unresolved critical defects.",
            registry=registry,
        )

        self.production_defects = Gauge(
            "qa_production_defects",
            "Number of defects detected in production.",
            registry=registry,
        )

        self.defect_leakage = Gauge(
            "qa_defect_leakage_ratio",
            (
                "Ratio of production defects to confirmed "
                "defects."
            ),
            registry=registry,
        )

        self.reopened_defects = Gauge(
            "qa_reopened_defects",
            "Number of reopened defects.",
            registry=registry,
        )

        self.defect_reopen_rate = Gauge(
            "qa_defect_reopen_rate_ratio",
            (
                "Ratio of reopened defects to resolved or "
                "closed defects."
            ),
            registry=registry,
        )

        self.release_readiness_score = Gauge(
            "qa_release_readiness_score",
            (
                "Composite QA release-readiness score from "
                "zero to one hundred."
            ),
            registry=registry,
        )

        self.release_test_executions = Gauge(
            "qa_test_executions_by_release_total",
            (
                "Number of test executions grouped by "
                "release and status."
            ),
            [
                "release_name",
                "status",
            ],
            registry=registry,
        )

        self.release_pass_rate = Gauge(
            "qa_test_pass_rate_by_release_ratio",
            "Test pass-rate ratio grouped by release.",
            ["release_name"],
            registry=registry,
        )

        self.release_failure_rate = Gauge(
            "qa_test_failure_rate_by_release_ratio",
            "Test failure-rate ratio grouped by release.",
            ["release_name"],
            registry=registry,
        )

        self.release_flaky_test_rate = Gauge(
            "qa_flaky_test_rate_by_release_ratio",
            "Flaky-test rate ratio grouped by release.",
            ["release_name"],
            registry=registry,
        )

        self.release_open_critical_defects = Gauge(
            "qa_open_critical_defects_by_release",
            (
                "Number of open critical defects grouped "
                "by release."
            ),
            ["release_name"],
            registry=registry,
        )

        self.release_defect_leakage = Gauge(
            "qa_defect_leakage_by_release_ratio",
            "Defect leakage ratio grouped by release.",
            ["release_name"],
            registry=registry,
        )

        self.release_readiness = Gauge(
            "qa_release_readiness_by_release_score",
            "Release-readiness score grouped by release.",
            ["release_name"],
            registry=registry,
        )

        self.defects_by_severity = Gauge(
            "qa_defects_by_severity_total",
            "Number of defects grouped by severity.",
            ["severity"],
            registry=registry,
        )

        self.defects_by_status = Gauge(
            "qa_defects_by_status_total",
            "Number of defects grouped by status.",
            ["status"],
            registry=registry,
        )

        self.defects_by_module = Gauge(
            "qa_defects_by_module_total",
            "Number of defects grouped by module.",
            ["module"],
            registry=registry,
        )

        self.defects_by_detection_phase = Gauge(
            "qa_defects_by_detection_phase_total",
            (
                "Number of defects grouped by detection "
                "phase."
            ),
            ["detected_phase"],
            registry=registry,
        )

        self.duration_by_module = Gauge(
            "qa_test_duration_by_module_seconds_average",
            (
                "Average test execution duration grouped "
                "by module."
            ),
            ["module"],
            registry=registry,
        )

        self.automation_by_module = Gauge(
            "qa_automation_test_cases_by_module",
            (
                "Automation test-case counts grouped by "
                "module and category."
            ),
            [
                "module",
                "category",
            ],
            registry=registry,
        )

        self.automation_coverage_by_module = Gauge(
            "qa_automation_coverage_by_module_ratio",
            "Automation coverage ratio grouped by module.",
            ["module"],
            registry=registry,
        )

    def update(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """Publish one calculated snapshot to Prometheus."""

        overall = snapshot["overall"]
        automation = snapshot["automation"]

        self.test_pass_rate.set(
            overall["pass_rate"]
        )

        self.test_failure_rate.set(
            overall["failure_rate"]
        )

        self.average_test_duration.set(
            overall["average_duration_seconds"]
        )

        self.automation_eligible_test_cases.set(
            automation["eligible_test_cases"]
        )

        self.automated_test_cases.set(
            automation["automated_test_cases"]
        )

        self.automation_coverage.set(
            automation["coverage"]
        )

        self.automation_gap.set(
            automation["gap"]
        )

        self.flaky_test_executions.set(
            overall["flaky_executions"]
        )

        self.flaky_test_rate.set(
            overall["flaky_test_rate"]
        )

        self.total_defects.set(
            overall["total_defects"]
        )

        self.open_critical_defects.set(
            overall["open_critical_defects"]
        )

        self.production_defects.set(
            overall["production_defects"]
        )

        self.defect_leakage.set(
            overall["defect_leakage"]
        )

        self.reopened_defects.set(
            overall["reopened_defects"]
        )

        self.defect_reopen_rate.set(
            overall["defect_reopen_rate"]
        )

        self.release_readiness_score.set(
            overall["readiness_score"]
        )

        self.test_executions_total.clear()

        for status, count in snapshot[
            "execution_status_counts"
        ].items():
            self.test_executions_total.labels(
                status=str(status)
            ).set(count)

        self.release_test_executions.clear()
        self.release_pass_rate.clear()
        self.release_failure_rate.clear()
        self.release_flaky_test_rate.clear()
        self.release_open_critical_defects.clear()
        self.release_defect_leakage.clear()
        self.release_readiness.clear()

        for release in snapshot["releases"]:
            release_name = release["release_name"]

            release_status_counts = {
                "Passed": release["passed_executions"],
                "Failed": release["failed_executions"],
                "Executed": release["executed_executions"],
                "Total": release["total_executions"],
            }

            for status, count in release_status_counts.items():
                self.release_test_executions.labels(
                    release_name=release_name,
                    status=status,
                ).set(count)

            self.release_pass_rate.labels(
                release_name=release_name
            ).set(release["pass_rate"])

            self.release_failure_rate.labels(
                release_name=release_name
            ).set(release["failure_rate"])

            self.release_flaky_test_rate.labels(
                release_name=release_name
            ).set(release["flaky_test_rate"])

            self.release_open_critical_defects.labels(
                release_name=release_name
            ).set(release["open_critical_defects"])

            self.release_defect_leakage.labels(
                release_name=release_name
            ).set(release["defect_leakage"])

            self.release_readiness.labels(
                release_name=release_name
            ).set(release["readiness_score"])

        self.defects_by_severity.clear()

        for severity, count in snapshot[
            "defects_by_severity"
        ].items():
            self.defects_by_severity.labels(
                severity=str(severity)
            ).set(count)

        self.defects_by_status.clear()

        for status, count in snapshot[
            "defects_by_status"
        ].items():
            self.defects_by_status.labels(
                status=str(status)
            ).set(count)

        self.defects_by_module.clear()

        for module, count in snapshot[
            "defects_by_module"
        ].items():
            self.defects_by_module.labels(
                module=str(module)
            ).set(count)

        self.defects_by_detection_phase.clear()

        for phase, count in snapshot[
            "defects_by_detection_phase"
        ].items():
            self.defects_by_detection_phase.labels(
                detected_phase=str(phase)
            ).set(count)

        self.duration_by_module.clear()

        for module, duration in snapshot[
            "duration_by_module"
        ].items():
            self.duration_by_module.labels(
                module=str(module)
            ).set(duration)

        self.automation_by_module.clear()
        self.automation_coverage_by_module.clear()

        for module_metrics in snapshot[
            "automation_by_module"
        ]:
            module = module_metrics["module"]

            self.automation_by_module.labels(
                module=module,
                category="Eligible",
            ).set(module_metrics["eligible"])

            self.automation_by_module.labels(
                module=module,
                category="Automated",
            ).set(module_metrics["automated"])

            self.automation_by_module.labels(
                module=module,
                category="Gap",
            ).set(module_metrics["gap"])

            self.automation_coverage_by_module.labels(
                module=module
            ).set(module_metrics["coverage"])

        self.last_refresh_success.set(1)
        self.last_refresh_timestamp.set(time.time())


def refresh_metrics(
    exporter: QAMetricsExporter,
    data_directory: Path,
) -> None:
    """Load the datasets and publish the latest snapshot."""

    datasets = load_datasets(data_directory)
    snapshot = calculate_snapshot(datasets)

    exporter.update(snapshot)


def main() -> None:
    """Start the Prometheus metrics HTTP server."""

    arguments = parse_arguments()

    if arguments.port <= 0:
        raise ValueError(
            "The exporter port must be greater than zero."
        )

    if arguments.refresh_seconds <= 0:
        raise ValueError(
            "The refresh interval must be greater than zero."
        )

    registry = CollectorRegistry()
    exporter = QAMetricsExporter(registry)

    refresh_metrics(
        exporter=exporter,
        data_directory=arguments.data_directory,
    )

    start_http_server(
        port=arguments.port,
        addr=arguments.host,
        registry=registry,
    )

    print(
        "QA metrics exporter started successfully."
    )

    print(
        "Metrics endpoint: "
        f"http://localhost:{arguments.port}/metrics"
    )

    print(
        "Data directory: "
        f"{arguments.data_directory.resolve()}"
    )

    print(
        "Refresh interval: "
        f"{arguments.refresh_seconds} seconds"
    )

    try:
        while True:
            time.sleep(arguments.refresh_seconds)

            try:
                refresh_metrics(
                    exporter=exporter,
                    data_directory=(
                        arguments.data_directory
                    ),
                )

                print(
                    "QA metrics refreshed successfully."
                )

            except (
                FileNotFoundError,
                ValueError,
                pd.errors.ParserError,
            ) as error:
                exporter.last_refresh_success.set(0)

                print(
                    "QA metrics refresh failed: "
                    f"{error}"
                )

    except KeyboardInterrupt:
        print("QA metrics exporter stopped.")


if __name__ == "__main__":
    main()