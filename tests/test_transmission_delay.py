"""Tests for transmission delay feature."""

import pytest
from fvc.gen.config import (
    Config,
    Defaults,
    PartialDefaults,
    CoordinateError,
    CoordinateErrors,
    deep_merge_defaults,
)


def test_defaults_with_transmission_delay():
    """Test that Defaults accepts optional transmission_delay."""
    defaults = Defaults(
        speed=15.0,
        altitude=120.0,
        coordinate_errors=CoordinateErrors(
            east=CoordinateError(mean=0.0, std_dev=2.0),
            north=CoordinateError(mean=0.0, std_dev=2.0),
            up=CoordinateError(mean=0.0, std_dev=3.0),
        ),
        time_step=1.0,
        transmission_delay=CoordinateError(mean=200.0, std_dev=50.0),
    )
    assert defaults.transmission_delay.mean == 200.0
    assert defaults.transmission_delay.std_dev == 50.0


def test_defaults_without_transmission_delay():
    """Test that Defaults works without transmission_delay (None by default)."""
    defaults = Defaults(
        speed=15.0,
        altitude=120.0,
        coordinate_errors=CoordinateErrors(
            east=CoordinateError(mean=0.0, std_dev=2.0),
            north=CoordinateError(mean=0.0, std_dev=2.0),
            up=CoordinateError(mean=0.0, std_dev=3.0),
        ),
        time_step=1.0,
    )
    assert defaults.transmission_delay is None
