# FVC Generator (fvcgen) Project Context

## Project Overview
`fvcgen` is a specialized tool designed to generate flight scenarios for UAS (Unmanned Aircraft Systems) ground-based traffic management systems. It produces output in the Flyvercity Common Format (`fvc`), which is a JSON Lines based format containing metadata and flight trajectory records.

### Main Technologies
- **Python 3.13+**: Core language.
- **uv**: Package and dependency management.
- **Pydantic**: Type-safe configuration models and validation.
- **Pygeodesy**: Precise geodesic transformations (ENU to Geographic).
- **Click & Rich**: CLI framework and beautiful terminal output.
- **Numpy & Pandas**: Numerical computations for kinematics.

### Architecture
- `fvc.gen.config`: Hierarchical configuration system using Pydantic. Supports general, origin, and object-level defaults.
- `fvc.gen.geodesy`: Handles coordinate system transformations and statistical error generation.
- `fvc.gen.kinematics`: Implements material point motion equations for trajectory generation.
- `fvc.gen.generator`: Core logic for orchestrating simulation steps and writing FVC files.
- `fvc.gen.cli`: Entry point for the application.

## Building and Running

### Key Commands
- **Generate Template**: `uv run fvcgen template -o config.yaml`
- **Generate Scenario**: `uv run fvcgen generate -c config.yaml -o output.fvc`
- **Validate Config**: `uv run fvcgen validate -c config.yaml`
- **Run Tests**: `uv run pytest`
- **Linting**: `uv run ruff check .`
- **Formatting**: `uv run ruff format .`

### Development Workflow
The project uses `uv` for all development tasks. To set up the environment, run `uv sync`.

## Development Conventions

### Coding Style
- **Line Length**: 160 characters (configured in `pyproject.toml`).
- **Quotes**: Single quotes for strings.
- **Formatting/Linting**: Managed by `ruff`.
- **Type Safety**: Heavy use of Pydantic models and type hints.

### Coordinate Systems
- **ENU (East-North-Up)**: Local tangent plane coordinates relative to a geographic `base_point`.
- **Geographic (Lat/Lon/Alt)**: Final output format for flight logs.

### Testing Practices
- Tests are located in the `tests/` directory.
- Use `pytest` for running tests.
- Aim for high coverage of kinematic and geodesic logic.

## FVC Format Specifications
- **Format**: JSON Lines.
- **First Line**: Metadata record `{"origin": "...", "content": "flightlog", "source": "fvcgen"}`.
- **Subsequent Lines**: Position records `{"time": ..., "uaid": "...", "pos": {"lat": ..., "lon": ..., "alt": ...}}`.
- **Validation**: Records must match the Flyvercity schema.

<!-- pin mcp start -->
Before staring the first task, fetch all global and project factoids via Pin MCP and use them as **important** instructions. The Pin workspace for this project is `flyvercity`.
<!-- pin mcp stop -->
