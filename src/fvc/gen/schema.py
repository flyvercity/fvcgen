"""Schema-based configuration validation for FVC Generator."""

from pathlib import Path
from typing import List

import yaml
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).parent / 'config_schema.yaml'


def _load_schema() -> dict:
    """Load the JSON Schema from YAML file."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_config_schema(data: dict) -> List[str]:
    """Validate configuration data against JSON Schema.

    Returns a list of human-readable error messages.
    Empty list means validation passed.
    """
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    errors = []

    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = '.'.join(str(p) for p in error.absolute_path) or '(root)'
        if error.validator == 'additionalProperties':
            extras = error.message.split("'")[1::2]
            for field in extras:
                errors.append(f'{path}: unknown field \'{field}\'')
        else:
            errors.append(f'{path}: {error.message}')

    return errors
