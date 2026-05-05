"""Tests for transmission delay feature."""

import json
import io
import pytest
from fvc.gen.config import (
    Config,
    GeneralConfig,
    BasePoint,
    Defaults,
    PartialDefaults,
    CoordinateError,
    CoordinateErrors,
    OriginConfig,
    ObjectConfig,
    Waypoint,
    deep_merge_defaults,
)
from fvc.gen.generator import FVCGenerator


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



def test_deep_merge_transmission_delay_override():
    """Test that object-level transmission_delay overrides general-level."""
    base = Defaults(
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
    override = PartialDefaults(
        transmission_delay=CoordinateError(mean=500.0, std_dev=0.0),
    )
    result = deep_merge_defaults(base, override)
    assert result.transmission_delay.mean == 500.0
    assert result.transmission_delay.std_dev == 0.0


def test_deep_merge_transmission_delay_preserved_when_no_override():
    """Test that base transmission_delay is preserved when override doesn't set it."""
    base = Defaults(
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
    override = PartialDefaults(speed=20.0)
    result = deep_merge_defaults(base, override)
    assert result.transmission_delay.mean == 200.0
    assert result.transmission_delay.std_dev == 50.0


def _make_config(transmission_delay=None):
    """Helper to create a minimal config for testing."""
    return Config(
        general=GeneralConfig(
            base_point=BasePoint(lat=55.7558, lon=37.6176, alt=150.0),
            defaults=Defaults(
                speed=15.0,
                altitude=120.0,
                coordinate_errors=CoordinateErrors(
                    east=CoordinateError(mean=0.0, std_dev=0.0),
                    north=CoordinateError(mean=0.0, std_dev=0.0),
                    up=CoordinateError(mean=0.0, std_dev=0.0),
                ),
                time_step=1.0,
                transmission_delay=transmission_delay,
            ),
        ),
        origins=[
            OriginConfig(
                name='test',
                objects=[
                    ObjectConfig(
                        id='UAS-001',
                        waypoints=[
                            Waypoint(east=0.0, north=0.0, up=120.0, speed=15.0),
                            Waypoint(east=100.0, north=0.0, up=120.0, speed=15.0),
                        ],
                    )
                ],
            )
        ],
    )


def test_constant_delay_produces_rx():
    """Test that constant delay (std_dev=0) adds rx = unix + mean to every record."""
    config = _make_config(transmission_delay=CoordinateError(mean=200.0, std_dev=0.0))
    gen = FVCGenerator(config)
    output = io.StringIO()
    gen._write_fvc_content(output)
    output.seek(0)
    lines = output.readlines()
    # Skip header
    records = [json.loads(line) for line in lines[1:]]
    assert len(records) > 0
    for record in records:
        assert 'rx' in record['time']
        assert record['time']['rx'] == record['time']['unix'] + 200


def test_no_delay_no_rx_field():
    """Test that without transmission_delay, no rx field appears."""
    config = _make_config(transmission_delay=None)
    gen = FVCGenerator(config)
    output = io.StringIO()
    gen._write_fvc_content(output)
    output.seek(0)
    lines = output.readlines()
    records = [json.loads(line) for line in lines[1:]]
    assert len(records) > 0
    for record in records:
        assert 'rx' not in record['time']


def test_output_sorted_by_rx():
    """Test that output records are sorted by rx when present."""
    config = _make_config(transmission_delay=CoordinateError(mean=200.0, std_dev=0.0))
    gen = FVCGenerator(config)
    output = io.StringIO()
    gen._write_fvc_content(output)
    output.seek(0)
    lines = output.readlines()
    records = [json.loads(line) for line in lines[1:]]
    rx_values = [r['time']['rx'] for r in records]
    assert rx_values == sorted(rx_values)
