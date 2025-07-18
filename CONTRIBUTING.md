# Contributing to Lean Spec

This repository uses a monorepo structure with multiple packages.

## Tool Configuration

All tool configurations (ruff, mypy, pytest) are centralized in the root `pyproject.toml` to ensure consistency across all packages. Subspecs inherit these configurations automatically.

## Repository Structure

```
lean-spec/
├── _scripts/               # Scripts for development tasks
│   └── init_subspec.py     # Script to create new subspecs
│
├── packages/               # Supporting subspec packages
│   ├── poseidon2           # poseidon2 subspec implementation
│   │   ├── src/
│   │   ├── tests/          # Tests for poseidon2
│   │   └── pyproject.toml  # Package configuration
│   ├── ...
│
├── tests/                  # lean-spec tests
│   └── ...
└── pyproject.toml          # Workspace configuration
```

## Working with Packages

### Installing Everything
```bash
uv sync  # Installs all packages in development mode
```

### Creating a New Subspec
```bash
uv run python scripts/init_subspec.py new-subspec
```

### Running Tests

Test a specific subspec:
```bash
# From the workspace root
uv run pytest packages/poseidon2

# From within the subspec directory
cd packages/poseidon2
uv run pytest  # Uses workspace environment by default
uv run pytest --no-workspace  # Test in isolation
```

Test everything from root:
```bash
uv run pytest  # Runs all tests including subspecs
```

### Making Changes

1. Each subspec is an independent package with its own `pyproject.toml`.
2. The main `lean-spec` package can import from subspecs.
3. Subspecs should NOT import from the main package.
4. Cross-subspec imports should be avoided to maintain independence.

### Publishing (Future)

Each package can be published independently:
- `lean-spec` - Main package with core functionality
- `poseidon2` - Poseidon2 implementation
- etc.

Users can then:
```bash
uv pip install lean-spec  # Gets everything
uv pip install poseidon2  # Just the Poseidon2 implementation
```