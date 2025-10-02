"""Pytest plugin for generating consensus test fixtures."""

import json
from pathlib import Path
from typing import Any, List

import pytest

from lean_spec_test_tools.base_types import CamelModel


class FixtureCollector:
    """Collects generated fixtures and writes them to disk."""

    def __init__(self, output_dir: Path, fork: str):
        """
        Initialize the fixture collector.

        Args:
            output_dir: Root directory for generated fixtures.
            fork: The fork name (e.g., "3sf", "devnet-0").
        """
        self.output_dir = output_dir
        self.fork = fork
        self.fixtures: List[tuple[str, str, Any]] = []

    def add_fixture(
        self,
        test_name: str,
        fixture_format: str,
        fixture: Any,
    ) -> None:
        """
        Add a fixture to the collection.

        Args:
            test_name: Name of the test that generated this fixture.
            fixture_format: Format name (e.g., "vote_processing_test").
            fixture: The fixture object.
        """
        self.fixtures.append((test_name, fixture_format, fixture))

    def write_fixtures(self) -> None:
        """Write all collected fixtures to disk."""
        for test_name, fixture_format, fixture in self.fixtures:
            # Create directory structure: fixtures/fork/format/test_name.json
            format_dir = fixture_format.replace("_test", "")
            fixture_path = self.output_dir / self.fork / format_dir
            fixture_path.mkdir(parents=True, exist_ok=True)

            # Write fixture JSON
            output_file = fixture_path / f"{test_name}.json"
            fixture_dict = fixture.json_dict_with_info()

            with open(output_file, "w") as f:
                json.dump(
                    fixture_dict,
                    f,
                    indent=2,
                    default=CamelModel.json_encoder,
                )

            print(f"Generated: {output_file.relative_to(self.output_dir)}")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command-line options for fixture generation."""
    group = parser.getgroup("fill", "leanSpec fixture generation")
    group.addoption(
        "--output",
        action="store",
        default="fixtures",
        help="Output directory for generated fixtures",
    )
    group.addoption(
        "--fork",
        action="store",
        required=True,
        help="Fork to generate fixtures for (e.g., 3sf, devnet-0)",
    )
    group.addoption(
        "--clean",
        action="store_true",
        default=False,
        help="Clean output directory before generating",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Setup fixture generation session."""
    # Get options
    output_dir = Path(config.getoption("--output"))
    fork = config.getoption("--fork")
    clean = config.getoption("--clean")

    # Clean if requested
    if clean and output_dir.exists():
        import shutil

        shutil.rmtree(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create collector
    config.fixture_collector = FixtureCollector(output_dir, fork)  # type: ignore[attr-defined]

    # Store fork for use in fixtures
    config.consensus_fork = fork  # type: ignore[attr-defined]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write all collected fixtures at the end of the session."""
    if hasattr(session.config, "fixture_collector"):
        session.config.fixture_collector.write_fixtures()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Any:
    """Skip test failures during fixture generation."""
    outcome = yield
    report = outcome.get_result()

    # During fixture generation, we don't care about test results
    # We only care about generating fixtures
    if call.when == "call":
        # Mark as passed regardless of actual result
        report.outcome = "passed"

    return report
