"""Tests for configuration models."""

import pytest
from fvc.gen.config import (
    Config,
    BasePoint,
    CoordinateErrors,
    CoordinateError,
)


def test_base_point_validation():
    """Test base point validation."""
    # Valid coordinates
    bp = BasePoint(lat=55.7558, lon=37.6176, alt=150.0)
    assert bp.lat == 55.7558
    assert bp.lon == 37.6176
    assert bp.alt == 150.0

    # Invalid latitude
    with pytest.raises(ValueError):
        BasePoint(lat=95.0, lon=37.6176)

    # Invalid longitude
    with pytest.raises(ValueError):
        BasePoint(lat=55.7558, lon=185.0)


def test_coordinate_errors():
    """Test coordinate errors model."""
    errors = CoordinateErrors(
        east=CoordinateError(mean=0.0, std_dev=2.0), north=CoordinateError(mean=0.0, std_dev=2.0), up=CoordinateError(mean=0.0, std_dev=3.0)
    )

    assert errors.east.mean == 0.0
    assert errors.east.std_dev == 2.0
    assert errors.north.std_dev == 2.0
    assert errors.up.std_dev == 3.0


def test_config_creation():
    """Test configuration creation."""
    config = Config(
        general={
            'base_point': {'lat': 55.7558, 'lon': 37.6176, 'alt': 150.0},
            'defaults': {
                'speed': 15.0,
                'altitude': 120.0,
                'coordinate_errors': {'east': {'mean': 0.0, 'std_dev': 2.0}, 'north': {'mean': 0.0, 'std_dev': 2.0}, 'up': {'mean': 0.0, 'std_dev': 3.0}},
                'time_step': 1.0,
            },
        },
        origins=[
            {
                'name': 'test_origin',
                'objects': [{'id': 'UAS-001', 'waypoints': [{'east': 0.0, 'north': 0.0, 'up': 120.0}, {'east': 1000.0, 'north': 0.0, 'up': 120.0}]}],
            }
        ],
    )

    assert config.general.base_point.lat == 55.7558
    assert len(config.origins) == 1
    assert config.origins[0].name == 'test_origin'
    assert len(config.origins[0].objects) == 1
    assert config.origins[0].objects[0].id == ['UAS-001']
