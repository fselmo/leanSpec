#!/usr/bin/env python3
"""Initialize a new subspec package with a standard setup."""

import sys
import subprocess
from pathlib import Path
import tomllib
import tomli_w


def init_subspec(name: str) -> None:
    """Initialize a new subspec package."""
    # get the root directory (parent of scripts/)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    subspec_dir = root_dir / "packages" / name

    subprocess.run(
        [
            "uv",
            "init",
            str(subspec_dir),
            "--lib",
            "--build-backend",
            "hatch",
            "--author-from",
            "git",
            "--no-workspace",  # don't create a new workspace
        ],
        check=True,
        cwd=root_dir,
    )

    # Read root pyproject.toml for shared configuration
    root_pyproject = root_dir / "pyproject.toml"
    with open(root_pyproject, "rb") as f:
        root_config = tomllib.load(f)

    # Build subspec pyproject.toml with inherited values
    subspec_config = {
        "build-system": {
            "requires": ["hatchling>=1.25.0,<2"],
            "build-backend": "hatchling.build",
        },
        "project": {
            "name": name,
            "version": "0.1.0",
            "description": f"{name.title()} implementation for Lean Ethereum",
            "readme": "README.md",
            "requires-python": root_config["project"]["requires-python"],
            "dependencies": [
                # list common dependencies for sub-specs here, or we can leave blank
                "pydantic>=2.9.2,<3",
            ],
            "authors": [
                {"name": "Ethereum Foundation"},
            ],
        },
        "tool": {
            "hatch": {
                "metadata": {"allow-direct-references": True},
                "build": {
                    "exclude": [".*", "tests/"],
                    "targets": {
                        "wheel": {"packages": [f"src/{name.replace('-', '_')}"]}
                    },
                },
            },
        },
    }

    subspec_pyproject = subspec_dir / "pyproject.toml"
    with open(subspec_pyproject, "wb") as f:
        tomli_w.dump(subspec_config, f)

    package_name = name.replace("-", "_")
    package_dir = subspec_dir / "src" / package_name
    package_dir.mkdir(parents=True, exist_ok=True)

    main_py = subspec_dir / "main.py"
    init_py = package_dir / "__init__.py"
    if main_py.exists():
        main_py.rename(init_py)
    else:
        init_py.touch()

    (package_dir / "py.typed").touch()

    tests_dir = subspec_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").touch()

    test_file = tests_dir / f"test_{package_name}.py"
    test_file.write_text(f'''import pytest


def test_package_import():
    import {package_name}  # noqa: F401
''')

    # Update workspace and add as dependency to main package
    with open(root_pyproject, "rb") as f:
        root_config = tomllib.load(f)

    # Add to main package dependencies
    dependencies = root_config.get("project", {}).get("dependencies", [])
    if name not in dependencies:
        dependencies.append(name)
        root_config["project"]["dependencies"] = dependencies

        # Add to uv sources
        if "tool" not in root_config:
            root_config["tool"] = {}
        if "uv" not in root_config["tool"]:
            root_config["tool"]["uv"] = {}
        if "sources" not in root_config["tool"]["uv"]:
            root_config["tool"]["uv"]["sources"] = {}

        root_config["tool"]["uv"]["sources"][name] = {"workspace": True}

        # Add to ruff's known-first-party
        if "ruff" not in root_config["tool"]:
            root_config["tool"]["ruff"] = {}
        if "lint" not in root_config["tool"]["ruff"]:
            root_config["tool"]["ruff"]["lint"] = {}
        if "isort" not in root_config["tool"]["ruff"]["lint"]:
            root_config["tool"]["ruff"]["lint"]["isort"] = {}
        if "known-first-party" not in root_config["tool"]["ruff"]["lint"]["isort"]:
            root_config["tool"]["ruff"]["lint"]["isort"]["known-first-party"] = []

        known_first_party = root_config["tool"]["ruff"]["lint"]["isort"][
            "known-first-party"
        ]
        package_name = name.replace("-", "_")
        if package_name not in known_first_party:
            known_first_party.append(package_name)

        # Write back the updated config
        with open(root_pyproject, "wb") as f:
            tomli_w.dump(root_config, f)
        print(f"\nAdded '{name}' as dependency to main package.")

    print(f"\nSubspec '{name}' created at {subspec_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/init_subspec.py <subspec-name>")
        sys.exit(1)

    init_subspec(sys.argv[1])
