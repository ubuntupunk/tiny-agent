# Tiny Agent

A lightweight, extensible AI agent framework for building autonomous AI systems.

## Features

- **Lightweight**: Minimal dependencies and fast startup
- **Extensible**: Plugin-based architecture for tools and capabilities
- **Async-first**: Built with asyncio for high performance
- **Type-safe**: Full type annotations and Pydantic validation
- **CLI Tools**: Command-line interface for agent management

## Quick Start

```bash
# Install the package
pip install -e .

# Run the CLI
python -m tiny_agent.cli --help
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Linting
ruff check .
```

## Architecture

The tiny-agent framework consists of:

- **Core Agent**: The main agent class that orchestrates capabilities
- **Tools**: Modular components that provide specific capabilities
- **Memory**: Simple in-memory storage for agent state
- **CLI**: Command-line interface for agent interaction

## Contribute
Fork this repo and create a PR request.

## License

Copyright Tiny Agent 2025. MIT License - see [LICENSE](LICENSE) file for details.
