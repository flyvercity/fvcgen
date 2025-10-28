# FVC Generator

A tool for generating FVC (Flight Vehicle Coordinates) scenarios for UAS (Unmanned Aircraft Systems) ground-based traffic management systems.

## Features

- **Configuration-driven**: Generate scenarios from YAML configuration files
- **Geodesic accuracy**: Precise coordinate transformations using pygeodesy
- **Kinematic simulation**: Realistic object movement using kinematic equations
- **Multiple objects**: Support for multiple origins and objects per scenario
- **Coordinate errors**: Configurable statistical errors for realistic simulation
- **Circular routes**: Support for closed-loop flight paths
- **Rich CLI**: Beautiful command-line interface with progress bars and colored output

## Installation

```bash
# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

1. **Generate a configuration template**:
   ```bash
   fvcgen template -o my_scenario.yaml
   ```

2. **Edit the configuration file** to define your scenario:
   - Set the base point (geographic reference)
   - Configure default parameters (speed, altitude, errors)
   - Define objects and their waypoints

3. **Generate the FVC scenario**:
   ```bash
   fvcgen generate -c my_scenario.yaml -o scenario.fvc
   ```

4. **Validate your configuration**:
   ```bash
   fvcgen validate -c my_scenario.yaml
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

## Command Line Interface

### Generate FVC scenario
```bash
fvcgen generate -c config.yaml -o output.fvc
```

### Generate configuration template
```bash
fvcgen template -o template.yaml
```

### Validate configuration
```bash
fvcgen validate -c config.yaml
```

### Stream output to stdout
```bash
fvcgen generate -c config.yaml --stream
```

## Development

### Code Style
- Uses `ruff` for formatting
- Uses `flake8` for linting
- Maximum line length: 160 characters
- Follows Python 3.13+ standards

### Running Tests
```bash
pytest
```

### Building
```bash
python -m build
```

## Architecture

- **CLI**: Click-based command-line interface with rich output
- **Configuration**: Pydantic models for type-safe configuration
- **Geodesy**: pygeodesy for accurate coordinate transformations
- **Kinematics**: Custom kinematic equations for object movement
- **Generation**: FVC file format generation with error simulation

## License

This project is part of the FlyverCity ecosystem.
