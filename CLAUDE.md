# Working with leanSpec

## Repository Overview

This is a Python repository for the Lean Ethereum Python specifications. It is set up as 
a `uv` workspace containing the main specifications and various cryptographic 
subspecifications that the Lean Ethereum protocol relies on.

## Key Directories

- `src/lean-spec/` - Specifications for the Lean Ethereum protocol
- `packages/*/` - Supporting ub-specification libraries (e.g., poseidon2, lean-sig, whir, ...)
- `tests/` - Main specification tests
- `docs/` - MkDocs documentation source

## Development Workflow

### Running Tests
```bash
# Sync all dependencies and install packages
uv sync --all-extras

# Run all tests in the workspace
uv run pytest

# Run tests for a specific subspec
uv run pytest src/poseidon2/tests  # from the workspace root
uv run pytest  # from within the subspec directory

# Run tests with coverage
uv run pytest --cov=src/lean_spec --cov=src/poseidon2 --cov-report=html
```

### Code Quality Checks
```bash
# Format code
uv run ruff format src tests

# Check linting
uv run ruff check src tests

# Fix fixable linting errors
uv run ruff check --fix src tests

# Type checking
uv run mypy src tests

# Run all checks via tox
uvx --with=tox-uv tox
```

### Common Tasks

1. **Adding to specs**: Located in `src/lean-spec`
2. **Adding to subspecs**: Located in `packages/*`
   - Each subspec should have its own `pyproject.toml` for dependencies
   - Use `uv sync --no-workspace` to install only that subspec's dependencies
   - Tests for subspecs should be in `packages/{subspec}/tests`, mirroring the source structure

## Important Patterns

### Test Patterns
- Tests should be placed in `tests/` and follow the same structure as the source code.
- Use `pytest.fixture`, in `conftest.py` or test files, for reusable test setup.
- Use `pytest.mark.parametrize` to parametrize tests with multiple inputs
- Use `pytest.raises(...)` with specific exceptions to test error cases
- Use `@pytest.mark.slow` for long-running tests

## Code Style

- Line length: 88 characters (default for `ruff`)
- Use type hints everywhere
- Follow Google docstring style
- No docstrings needed for `__init__` methods
- Imports are automatically sorted by `isort` and `ruff`

## Testing Philosophy

- Tests should be simple and clear
- Test file names must start with `test_`
- Test function names must start with `test_`
- Use descriptive test names that explain what's being tested

## Common Commands Reference

| Task                 | Command |
|----------------------|---------|
| Install dependencies | `uv sync --all-extras` |
| Run tests            | `uv run pytest` |
| Format code          | `uv run ruff format src tests` |
| Lint code            | `uv run ruff check src tests` |
| Fix lint errors      | `uv run ruff check --fix src tests` |
| Type check           | `uv run mypy src tests` |
| Run all checks       | `uvx --with=tox-uv tox` |
| Build docs           | `uv run mkdocs build` |
| Serve docs           | `uv run mkdocs serve` |

## Important Notes

1. This repository uses Python 3.12+ features
2. All models should use Pydantic for automatic validation  # TODO: talk about this structure
3. Keep things simple, readable, and clear. These are meant to be clear specifications.
