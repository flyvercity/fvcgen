# General Generator Instructions

* Make all uncertain fragments with `[REFINE]` tags
* Be extra careful with the geodesy and timing aspects of the code as they are critical for the accuracy of the generated scenarios.

# Python Code Generation

* Use `ruff` for formatting
* Use `flake8` for linting

# Architecture Choices

* CLI application
* `click` for CLI
* `rich` for output, progress bars, log formatting, etc.
* Compatibility with `fvctools`
* `pygeodesy` for coordinate transformations
* `numpy` for numerical calculations
* `pandas` for data manipulation
* `pyyaml` for YAML file handling and configuration/scenarios

# Users

This tool is intended for use by aviation professionals who need to generate FVC scenarios for simulation and validation of UAS ground-based traffic management systems.
