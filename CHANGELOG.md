# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Calendar Versioning](https://calver.org/) (YYYY.M.D).

## [2026.5.8]

### Added

- Schema-based configuration validation using jsonschema
- LICENSE file
- CHANGELOG.md

### Changed

- Switched to Calendar Versioning (CalVer)
- Updated project configuration

## [2026.5.5]

### Added

- Transmission delay simulation (`transmission_delay` config field)
- `rx` field in output records with simulated reception time
- Output records sorted by reception time

### Fixed

- Removed unused import

## [2026.5.4]

### Added

- Logging configuration and debug output
- Pin MCP integration instructions in AGENTS.md

### Changed

- Renamed and updated project documentation
- Updated project configuration for uv

### Fixed

- Speed default handling (closes #1)

## [2025.10.28]

### Added

- Initial scenario generator implementation
- Click-based CLI with Rich output
- Pydantic v2 configuration models
- Pygeodesy coordinate transformations (ENU to Geographic)
- Kinematic simulation for object movement
- Support for multiple origins and objects
- Circular route support
- Configurable coordinate errors
- JSON Lines output format (FVC)
- Configuration template generation
- Configuration validation command
- Stream output to stdout

## [2025.10.27]

### Added

- Initial commit with project structure and documentation
