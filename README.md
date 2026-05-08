# Flyvercity Flight Scenario Generator

A tool for generating flight scenarios for UAS (Unmanned Aircraft Systems) ground-based traffic management systems. The tool uses Flyvercity Common Format (`fvc`).

## Features

- **Configuration-driven**: Generate scenarios from YAML configuration files
- **Geodesic accuracy**: Precise coordinate transformations using pygeodesy
- **Kinematic simulation**: Realistic object movement using kinematic equations
- **Multiple objects**: Support for multiple origins and objects per scenario
- **Coordinate errors**: Configurable statistical errors for realistic simulation
- **Circular routes**: Support for closed-loop flight paths

## Installation

### From CodeArtifact (recommended)

1. Authenticate with CodeArtifact:
   ```powershell
   . .\scripts\Login-ToCodeArtifact.ps1
   ```

2. Install as a tool:
   ```bash
   uv run scripts/install_fvcgen.py
   ```

### From source

```bash
uv sync
```

## Quick Start

1. **Generate a configuration template**:
   ```bash
   uv run fvcgen template -o my_scenario.yaml
   ```

2. **Edit the configuration file** to define your scenario:
   - Set the base point (geographic reference)
   - Configure default parameters (speed, altitude, errors)
   - Define objects and their waypoints

3. **Generate the FVC scenario**:
   ```bash
   uv run fvcgen generate -c my_scenario.yaml -o scenario.fvc
   ```

4. **Validate your configuration**:
   ```bash
   uv run fvcgen validate -c my_scenario.yaml
   ```

## Configuration Format

The configuration file uses YAML format with the following structure:

```yaml
general:
  base_point:
    lat: 55.7558  # Base point latitude
    lon: 37.6176  # Base point longitude
    alt: 150.0    # Base point altitude (meters)
  defaults:
    speed: 15.0   # Default speed (m/s)
    altitude: 120.0  # Default altitude (meters)
    coordinate_errors:
      east: {mean: 0.0, std_dev: 2.0}
      north: {mean: 0.0, std_dev: 2.0}
      up: {mean: 0.0, std_dev: 3.0}
    time_step: 1.0  # Time step (seconds)
    transmission_delay:  # Optional: simulated transmission delay (ms)
      mean: 2.0
      std_dev: 0.5
  include_origin: false  # Include origin name in output records
  output_file: "scenario.fvc"  # Output file path

origins:
  - name: "origin-1"  # Required origin name
    objects:
      - id: "UAS-001"
        start_delay: 0.0
        waypoints:
          - {east: 0.0, north: 0.0, up: 120.0, speed: 15.0}
          - {east: 1000.0, north: 0.0, up: 120.0, speed: 15.0}
          - {east: 1000.0, north: 1000.0, up: 120.0, speed: 15.0}
        circular: true
```

### Hierarchical Defaults

Defaults are resolved in order: **general → origin → object**. Each level can partially override fields from the level above. For example, an object can override only `speed` while inheriting all other defaults from its origin or the general section.

### Multiple IDs per Object

The `id` field accepts a string or a list of strings. When a list is provided, a position record is emitted for each ID at every time step (useful for simulating co-located objects).

## Command Line Interface (Development Environment)

### Global options
```bash
uv run fvcgen --version          # Show version
uv run fvcgen -v <command>       # Enable verbose/debug output
```

### Generate FVC scenario
```bash
uv run fvcgen generate -c config.yaml -o output.fvc
```

### Generate configuration template
```bash
uv run fvcgen template -o template.yaml
```

### Validate configuration
```bash
uv run fvcgen validate -c config.yaml
```

### Stream output to stdout
```bash
uv run fvcgen generate -c config.yaml --stream
```

## Output Format

The output file uses JSON Lines format (`.fvc`). The first line is a metadata record, followed by position records:

```jsonl
{"origin": "config.yaml", "content": "flightlog", "source": "fvcgen"}
{"time": {"unix": 0}, "uaid": {"int": "UAS-001"}, "pos": {"loc": {"lat": 55.7558, "lon": 37.6176, "alt": 270.0}}}
{"time": {"unix": 1000, "rx": 1002}, "uaid": {"int": "UAS-001"}, "pos": {"loc": {"lat": 55.7559, "lon": 37.6180, "alt": 270.1}}}
```

Record fields:
- `time.unix` — simulation timestamp (milliseconds)
- `time.rx` — simulated reception time (milliseconds), present when `transmission_delay` is configured
- `uaid.int` — object identifier
- `pos.loc` — geographic position (`lat`, `lon`, `alt`)
- `origin` — origin name (present when `include_origin: true`)

Records are sorted by `rx` time when transmission delay is enabled.

## Development

### Code Style
- Uses `ruff` for formatting and linting
- Maximum line length: 160 characters
- Follows Python 3.13+ standards

### Running Tests
```bash
uv run pytest
```

### Building
```bash
uv run build
```

## Architecture

- **CLI**: Click-based command-line interface with rich output
- **Configuration**: Pydantic models for type-safe configuration
- **Geodesy**: pygeodesy for accurate coordinate transformations
- **Kinematics**: Custom kinematic equations for object movement
- **Generation**: FVC file format generation with error simulation
