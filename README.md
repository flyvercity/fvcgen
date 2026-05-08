# Flyvercity Flight Scenario Generator

A tool for generating flight scenarios for UAS (Unmanned Aircraft Systems) ground-based traffic management systems. The tool uses Flyvercity Common Format (`fvc`).

## Features

- **Configuration-driven**: Generate scenarios from YAML configuration files
- **Geodesic accuracy**: Precise coordinate transformations using pygeodesy
- **Kinematic simulation**: Realistic object movement using kinematic equations
- **Multiple objects**: Support for multiple origins and objects per scenario
- **Coordinate errors**: Configurable statistical errors for realistic simulation
- **Circular routes**: Support for closed-loop flight paths

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
  output_file: "scenario.fvc"  # Output file path

origins:
  - objects:
      - id: "UAS-001"
        start_delay: 0.0
        waypoints:
          - {east: 0.0, north: 0.0, up: 120.0, speed: 15.0}
          - {east: 1000.0, north: 0.0, up: 120.0, speed: 15.0}
          - {east: 1000.0, north: 1000.0, up: 120.0, speed: 15.0}
        circular: true
```

## Command Line Interface (Development Environment)

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

## Development

### Code Style
- Uses `ruff` for formatting
- Uses `flake8` for linting
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
