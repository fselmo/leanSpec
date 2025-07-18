# Lean Ethereum Specifications

A monorepo containing the Lean Ethereum protocol specifications and cryptographic subspecifications.

## Quick Start

### Prerequisites

- Python 3.12 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone this repository
git clone https://github.com/leanEthereum/lean-spec leanSpec
cd leanSpec

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks (optional)
uvx pre-commit install

# Run tests to verify setup
uv run pytest
```

### Project Structure

```
├── _scripts/
│   └── init_subspec.py     # Script to create new subspecs
│
├── packages/
│   ├── poseidon2/      # Poseidon2 hash function (subspec example)
│   │   ├── pyproject.toml
│   │   └── tests/
│   │       └── test_poseidon2.py
│   ├── ...
│   ├── ...
│
├── src/
│   └── lean_spec/          # Main protocol specifications
│   
├── tests/                  # Integration tests
├── docs/                   # Documentation source
└── pyproject.toml          # Workspace configuration
```

## Working with the Workspace

This repository uses a uv workspace to manage multiple packages:
- **`lean-spec`** - The main specification package
- **Subspecs** (e.g., `poseidon2`) - Independent cryptographic implementations. 
  The subspecs are separate packages that exist inside the `packages/` directory. 

### Creating a New Subspec

```bash
# Create a new subspec package
uv run python scripts/init_subspec.py my-new-subspec
```

This automatically:
- Creates the package structure
- Adds it to the workspace
- Sets up the main package to depend on it

### Workspace Commands

```bash
# Install all packages (from anywhere in the repo)
uv sync

# Install all packages for all extras (e.g., dev dependencies)
uv sync --all-extras

# Work on a specific subspec in isolation
cd packages/poseidon2
uv sync --no-workspace  # Only installs poseidon2's dependencies
```

## Development Workflow

### Running Tests

```bash
# Run all tests from workspace root
uv run pytest

# Run tests for a specific subspec
cd packages/poseidon2
uv run pytest

# Run integration tests only
uv run pytest tests/

# Run tests in parallel
uv run pytest -n auto
```

### Code Quality

```bash
# Check code style and errors
uv run ruff check src tests

# Auto-fix issues
uv run ruff check --fix src tests

# Format code
uv run ruff format src tests

# Type checking
uv run mypy src tests
```

### Using Tox

```bash
# Run all environments (tests, linting, type checking, docs)
uvx --with=tox-uv tox

# Run specific environment
uvx --with=tox-uv tox -e lint
```

### Pre-commit Hooks (Optional)

The project includes pre-commit hooks that automatically check your code before commits:

```bash
# Install pre-commit hooks (one-time setup)
uvx pre-commit install

# Run hooks manually on all files
uvx pre-commit run --all-files

# Skip hooks for a single commit
git commit --no-verify
```

Hooks include:
- Trailing whitespace removal
- End-of-file fixing
- YAML/TOML validation
- Ruff linting and formatting
- MyPy type checking

### Documentation

```bash
# Serve docs locally (with auto-reload)
uv run mkdocs serve

# Build docs
uv run mkdocs build
```

## Writing Specifications

### Example: Writing Tests

```python
# tests/test_new_types.py
import pytest
from pydantic import ValidationError
from specs.new_types import NewTransaction

# Parametrized test - test multiple inputs
@pytest.mark.parametrize("version", [1, 2, 3])
def test_transaction_versions(version):
    """Test different transaction versions."""
    tx = NewTransaction(version=version, data=b"test", signature=b"0" * 65)
    assert tx.version == version


# Exception testing
def test_invalid_transaction():
    """Test that invalid data raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        NewTransaction(version=0, data=b"", signature=b"short")
    
    assert "version" in str(exc_info.value)  # Check error details
```

## Guide to Python Tools

- **Pydantic models**: Think of these as strongly-typed data structures that validate inputs automatically
- **pytest**: Testing framework - just name test files `test_*.py` and functions `test_*`
- **uv**: Fast Python package manager - like npm/yarn but for Python

## Common Commands Reference

| Task                               | Command                        |
|------------------------------------|--------------------------------|
| Install deps                       | `uv sync`                      |
| Run main spec tests                | `uv run pytest tests/`         |
| Run all tests (spec and sub-specs) | `uv run pytest`                |
| Format code                        | `uv run ruff format src tests` |
| Check types                        | `uv run mypy src tests`        |
| Serve docs                         | `uv run mkdocs serve`          |
| Run all checks                     | `uvx --with=tox-uv tox`        |

## Package Structure

This directory contains all packages in the Lean Spec workspace:

- **`lean_spec/`** - Main package containing core Ethereum specifications
- **`poseidon2/`** - Poseidon2 hash function implementation
- **`[future subspecs]/`** - Additional cryptographic primitives and subspecifications

Each subdirectory is a complete Python package with:
- Its own `pyproject.toml`
- Its own `src/` directory
- Its own `tests/` directory
- Its own version and dependencies

The main `lean-spec` package depends on the subspecs, not the other way around.

## Contributing

1. Make your changes
2. Run `uv run ruff format src tests` to format code
3. Run `uvx --with=tox-uv tox` to ensure all checks pass
4. Submit a pull request

## License

MIT License - see LICENSE file for details.