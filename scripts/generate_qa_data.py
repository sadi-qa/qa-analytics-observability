from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


RANDOM_SEED = 42
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "raw"

MODULES = [
    "Authentication",
    "Product Catalog",
    "Cart",
    "Checkout",
    "Payment",
    "User Account",
]

TEST_TYPES = [
    "Functional",
    "Regression",
    "Smoke",
    "Integration",
    "API",
    "End-to-End",
    "Security",
    "Usability",
]

PRIORITIES = ["Critical", "High", "Medium", "Low"]
BROWSERS = ["Chromium", "Firefox", "WebKit"]
ENVIRONMENTS = ["QA", "Staging", "UAT"]

DEFECT_SEVERITIES = ["Critical", "High", "Medium", "Low"]
DEFECT_STATUSES = ["Open", "In Progress", "Resolved", "Closed", "Deferred"]
DETECTION_PHASES = ["QA", "UAT", "Production"]

ROOT_CAUSES = [
    "Code",
    "Requirement",
    "Configuration",
    "Test Data",
    "Environment",
    "Third-Party Integration",
]


def generate_releases() -> pd.DataFrame:
    """Create six software releases for historical analysis."""

    releases: list[dict[str, Any]] = []

    release_start_dates = [
        datetime(2026, 1, 5),
        datetime(2026, 2, 2),
        datetime(2026, 3, 2),
        datetime(2026, 4, 6),
        datetime(2026, 5, 4),
        datetime(2026, 6, 1),
    ]

    for index, start_date in enumerate(release_start_dates, start=1):
        releases.append(
            {
                "release_id": f"REL-{index:03d}",
                "release_name": f"Release 1.{index - 1}",
                "start_date": start_date.date().isoformat(),
                "release_date": (
                    start_date + timedelta(days=24)
                ).date().isoformat(),
                "environment": "Staging",
                "release_status": "Released" if index < 6 else "Ready",
            }
        )

    return pd.DataFrame(releases)


def generate_test_cases(
    random_generator: random.Random,
) -> pd.DataFrame:
    """Create the reusable test-case inventory."""

    test_cases: list[dict[str, Any]] = []

    for index in range(1, 73):
        module = MODULES[(index - 1) % len(MODULES)]
        test_type = TEST_TYPES[(index - 1) % len(TEST_TYPES)]

        priority = random_generator.choices(
            PRIORITIES,
            weights=[0.10, 0.35, 0.40, 0.15],
            k=1,
        )[0]

        automation_eligible = (
            test_type != "Usability"
            and random_generator.random() < 0.90
        )

        is_automated = (
            automation_eligible
            and random_generator.random() < 0.78
        )

        owner_team = (
            "QA Automation"
            if is_automated
            else random_generator.choice(
                ["QA Functional", "Quality Engineering"]
            )
        )

        created_date = datetime(2025, 7, 1) + timedelta(
            days=random_generator.randint(0, 183)
        )

        test_cases.append(
            {
                "test_case_id": f"TC-{index:03d}",
                "test_name": (
                    f"{module} {test_type} scenario {index:02d}"
                ),
                "module": module,
                "test_type": test_type,
                "priority": priority,
                "automation_eligible": automation_eligible,
                "is_automated": is_automated,
                "owner_team": owner_team,
                "created_date": created_date.date().isoformat(),
            }
        )

    return pd.DataFrame(test_cases)


def choose_execution_status(
    random_generator: random.Random,
    release_number: int,
) -> str:
    """Return execution results that improve across releases."""

    pass_rates = {
        1: 0.82,
        2: 0.85,
        3: 0.88,
        4: 0.90,
        5: 0.93,
        6: 0.95,
    }

    pass_rate = pass_rates[release_number]
    remaining_probability = 1.0 - pass_rate

    return random_generator.choices(
        ["Passed", "Failed", "Blocked", "Skipped"],
        weights=[
            pass_rate,
            remaining_probability * 0.60,
            remaining_probability * 0.25,
            remaining_probability * 0.15,
        ],
        k=1,
    )[0]


def generate_test_executions(
    random_generator: random.Random,
    releases: pd.DataFrame,
    test_cases: pd.DataFrame,
) -> pd.DataFrame:
    """Create execution records for every test and release."""

    executions: list[dict[str, Any]] = []
    execution_number = 1

    module_duration_baselines = {
        "Authentication": 8.0,
        "Product Catalog": 14.0,
        "Cart": 12.0,
        "Checkout": 18.0,
        "Payment": 22.0,
        "User Account": 10.0,
    }

    for release in releases.itertuples(index=False):
        release_number = int(
            str(release.release_id).split("-")[1]
        )

        release_start = datetime.fromisoformat(
            str(release.start_date)
        )

        for test_case in test_cases.itertuples(index=False):
            status = choose_execution_status(
                random_generator,
                release_number,
            )

            if test_case.test_type == "API":
                browser = "API"
            elif test_case.test_type == "Usability":
                browser = "Not Applicable"
            else:
                browser = random_generator.choice(BROWSERS)

            is_flaky = (
                bool(test_case.is_automated)
                and random_generator.random() < 0.035
            )

            if is_flaky:
                retry_count = random_generator.randint(1, 2)
            elif (
                status == "Failed"
                and random_generator.random() < 0.20
            ):
                retry_count = 1
            else:
                retry_count = 0

            baseline = module_duration_baselines[
                str(test_case.module)
            ]

            automation_multiplier = (
                0.75 if bool(test_case.is_automated) else 1.25
            )

            browser_multiplier = (
                1.10 if browser == "WebKit" else 1.0
            )

            duration_seconds = max(
                1.0,
                random_generator.gauss(
                    baseline
                    * automation_multiplier
                    * browser_multiplier,
                    baseline * 0.20,
                ),
            )

            execution_date = release_start + timedelta(
                days=random_generator.randint(1, 21),
                hours=random_generator.randint(8, 18),
                minutes=random_generator.randint(0, 59),
            )

            executions.append(
                {
                    "execution_id": (
                        f"EXE-{execution_number:05d}"
                    ),
                    "test_case_id": test_case.test_case_id,
                    "release_id": release.release_id,
                    "build_number": (
                        f"BUILD-{release_number}"
                        f"{random_generator.randint(1, 5):02d}"
                    ),
                    "execution_date": execution_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "status": status,
                    "browser": browser,
                    "environment": random_generator.choices(
                        ENVIRONMENTS,
                        weights=[0.25, 0.60, 0.15],
                        k=1,
                    )[0],
                    "duration_seconds": round(
                        duration_seconds,
                        2,
                    ),
                    "is_flaky": is_flaky,
                    "retry_count": retry_count,
                }
            )

            execution_number += 1

    return pd.DataFrame(executions)


def generate_defects(
    random_generator: random.Random,
    test_cases: pd.DataFrame,
    test_executions: pd.DataFrame,
) -> pd.DataFrame:
    """Create defects from failed and blocked executions."""

    defects: list[dict[str, Any]] = []

    test_case_lookup = (
        test_cases
        .set_index("test_case_id")
        .to_dict("index")
    )

    failed_executions = test_executions[
        test_executions["status"].isin(
            ["Failed", "Blocked"]
        )
    ]

    defect_number = 1

    for execution in failed_executions.itertuples(index=False):
        if random_generator.random() > 0.72:
            continue

        test_case = test_case_lookup[
            str(execution.test_case_id)
        ]

        severity = random_generator.choices(
            DEFECT_SEVERITIES,
            weights=[0.08, 0.27, 0.45, 0.20],
            k=1,
        )[0]

        detected_phase = random_generator.choices(
            DETECTION_PHASES,
            weights=[0.78, 0.15, 0.07],
            k=1,
        )[0]

        status = random_generator.choices(
            DEFECT_STATUSES,
            weights=[0.12, 0.10, 0.30, 0.40, 0.08],
            k=1,
        )[0]

        created_date = datetime.strptime(
            str(execution.execution_date),
            "%Y-%m-%d %H:%M:%S",
        ).date()

        resolved_date: str | None = None

        if status in {"Resolved", "Closed"}:
            resolved_date = (
                created_date
                + timedelta(
                    days=random_generator.randint(1, 14)
                )
            ).isoformat()

        linked_test_case_id: str | None = str(
            execution.test_case_id
        )

        if (
            detected_phase == "Production"
            and random_generator.random() < 0.40
        ):
            linked_test_case_id = None

        defects.append(
            {
                "defect_id": f"BUG-{defect_number:03d}",
                "release_id": execution.release_id,
                "linked_test_case_id": linked_test_case_id,
                "title": (
                    f"{test_case['module']} issue found during "
                    f"{str(test_case['test_type']).lower()} testing"
                ),
                "module": test_case["module"],
                "severity": severity,
                "status": status,
                "detected_phase": detected_phase,
                "created_date": created_date.isoformat(),
                "resolved_date": resolved_date,
                "is_reopened": (
                    status in {"Resolved", "Closed"}
                    and random_generator.random() < 0.12
                ),
                "root_cause": random_generator.choice(
                    ROOT_CAUSES
                ),
            }
        )

        defect_number += 1

    return pd.DataFrame(defects)


def write_dataset(
    dataframe: pd.DataFrame,
    file_name: str,
) -> Path:
    """Write one dataset to the raw data directory."""

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIRECTORY / file_name

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    return output_path


def main() -> None:
    """Generate and save all synthetic QA datasets."""

    random_generator = random.Random(RANDOM_SEED)

    releases = generate_releases()

    test_cases = generate_test_cases(
        random_generator
    )

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

    datasets = {
        "releases.csv": releases,
        "test_cases.csv": test_cases,
        "test_executions.csv": test_executions,
        "defects.csv": defects,
    }

    print("Generating synthetic QA datasets:")

    for file_name, dataframe in datasets.items():
        output_path = write_dataset(
            dataframe,
            file_name,
        )

        print(
            f"- {file_name}: "
            f"{len(dataframe)} rows -> {output_path}"
        )

    print(
        "Synthetic QA dataset generation "
        "completed successfully."
    )


if __name__ == "__main__":
    main()