# leanSpec

Welcome to the Ethereum Specifications documentation for leanSpec. 

## Quick Start

```bash
# Clone the repository
git clone https://github.com/leanEthereum/lean-spec leanSpec
cd leanSpec

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Start documentation server
uv run mkdocs serve
```

## Features

### Type-Safe Specifications

Using Pydantic for automatic validation:

```python
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    nonce: int = Field(..., ge=0)
    gas_price: int = Field(..., ge=0)
    gas_limit: int = Field(..., ge=0)
    value: int = Field(..., ge=0)
```

### Structured Testing

Tests mirror the source structure for easy navigation:

```
src/specs/types.py → tests/specs/test_types.py
src/subspecs/eip.py → tests/subspecs/test_eip.py
```

### Development Tools

Pre-configured environment with:

- **Ruff**: Fast Python linter and formatter
- **Mypy**: Static type checking with Pydantic plugin
- **Pytest**: Testing with coverage and parallel execution
- **Tox**: Test automation across environments
- **Pre-commit**: Automated code quality checks

## Project Structure

```
├── src/
│   ├── specs/              # Main specification modules
│   │   ├── types.py        # Core data types
│   │   └── validation.py   # Validation logic
│   └── subspecs/           # Sub-specifications (EIPs)
│       └── example_eip.py  # Example implementation
├── tests/                  # Test suite
│   ├── specs/              # Tests for main specs
│   └── subspecs/           # Tests for subspecs
├── docs/                   # Documentation
└── pyproject.toml         # Project configuration
```

## Next Steps

- Read the [README](https://github.com/leanEthereum/lean-spec#readme) for development workflow