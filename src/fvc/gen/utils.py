"""Utility functions for FVC Generator."""

from pathlib import Path
from typing import Union

from .config import Config, GeneralConfig, BasePoint, Defaults, CoordinateErrors, CoordinateError, OriginConfig, ObjectConfig, Waypoint


def generate_config_template(output_path: Union[str, Path]) -> None:
    """Generate a configuration file template."""
    # Create a sample configuration
    config = Config(
        general=GeneralConfig(
            base_point=BasePoint(
                lat=55.7558,  # Moscow latitude
                lon=37.6176,  # Moscow longitude
                alt=150.0,
            ),
            defaults=Defaults(
                speed=15.0,  # 15 m/s
                altitude=120.0,  # 120 meters
                coordinate_errors=CoordinateErrors(
                    east=CoordinateError(mean=0.0, std_dev=2.0), north=CoordinateError(mean=0.0, std_dev=2.0), up=CoordinateError(mean=0.0, std_dev=3.0)
                ),
                time_step=1.0,  # 1 second
            ),
            output_file='scenario.fvc',
        ),
        origins=[
            OriginConfig(
                name='origin-1',
                objects=[
                    ObjectConfig(
                        id='UAS-001',
                        start_delay=0.0,
                        waypoints=[
                            Waypoint(east=0.0, north=0.0, up=120.0, speed=15.0),
                            Waypoint(east=1000.0, north=0.0, up=120.0, speed=15.0),
                            Waypoint(east=1000.0, north=1000.0, up=120.0, speed=15.0),
                            Waypoint(east=0.0, north=1000.0, up=120.0, speed=15.0),
                            Waypoint(east=0.0, north=0.0, up=120.0, speed=15.0),
                        ],
                        circular=True,
                    ),
                    ObjectConfig(
                        id='UAS-002',
                        start_delay=30.0,  # Start 30 seconds later
                        waypoints=[
                            Waypoint(east=500.0, north=500.0, up=100.0, speed=12.0),
                            Waypoint(east=1500.0, north=500.0, up=100.0, speed=12.0),
                            Waypoint(east=1500.0, north=1500.0, up=100.0, speed=12.0),
                            Waypoint(east=500.0, north=1500.0, up=100.0, speed=12.0),
                        ],
                    ),
                ],
            )
        ],
    )

    # Save to file
    config.to_file(output_path)
