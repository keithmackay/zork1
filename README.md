# ZIL Interpreter

A Python interpreter for ZIL (Zork Implementation Language) that can play Zork I from source files.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
zil path/to/zork1.zil
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=zil_interpreter --cov-report=html

# Format code
black zil_interpreter tests
```

## Architecture

See `docs/plans/2025-11-23-zil-interpreter-design.md` for detailed architecture.
