"""Geodesic coordinate transformations using pygeodesy."""

import numpy as np
from typing import Tuple
from pygeodesy import LocalCartesian
from pygeodesy.ellipsoidalVincenty import LatLon as LatLonVincenty

from .config import BasePoint, Waypoint


class CoordinateTransformer:
    """Handles coordinate transformations between geographic and ENU systems."""

    def __init__(self, base_point: BasePoint):
        """Initialize with base point for ENU coordinate system."""
        self.base_point = base_point
        self.base_latlon = base_point.to_latlon()
        self.local_cartesian = LocalCartesian(self.base_latlon)

    def enu_to_geographic(self, east: float, north: float, up: float) -> Tuple[float, float, float]:
        """Convert ENU coordinates to geographic (lat, lon, alt)."""
        # Convert ENU to local cartesian (x, y, z)
        # ENU: East=X, North=Y, Up=Z
        # LocalCartesian: X=East, Y=North, Z=Up
        x, y, z = east, north, up

        # Convert to geographic coordinates
        latlon = self.local_cartesian.toLatLon(x, y, z)

        return latlon.lat, latlon.lon, latlon.height

    def geographic_to_enu(self, lat: float, lon: float, alt: float) -> Tuple[float, float, float]:
        """Convert geographic coordinates to ENU."""
        latlon = LatLonVincenty(lat, lon, height=alt)
        x, y, z = self.local_cartesian.toLocal(latlon)

        # Convert from local cartesian to ENU
        east, north, up = x, y, z

        return east, north, up

    def waypoint_to_geographic(self, waypoint: Waypoint) -> Tuple[float, float, float]:
        """Convert waypoint ENU coordinates to geographic."""
        return self.enu_to_geographic(waypoint.east, waypoint.north, waypoint.up)

    def calculate_distance_bearing(self, from_waypoint: Waypoint, to_waypoint: Waypoint) -> Tuple[float, float]:
        """Calculate distance and bearing between two waypoints."""
        # Convert to geographic coordinates
        lat1, lon1, alt1 = self.waypoint_to_geographic(from_waypoint)
        lat2, lon2, alt2 = self.waypoint_to_geographic(to_waypoint)

        # Create LatLon objects
        point1 = LatLonVincenty(lat1, lon1, height=alt1)
        point2 = LatLonVincenty(lat2, lon2, height=alt2)

        # Calculate distance and bearing
        distance = point1.distanceTo(point2)
        bearing = point1.bearingTo(point2)

        return distance, bearing

    def calculate_enu_distance(self, from_waypoint: Waypoint, to_waypoint: Waypoint) -> float:
        """Calculate straight-line distance between two waypoints in ENU."""
        dx = to_waypoint.east - from_waypoint.east
        dy = to_waypoint.north - from_waypoint.north
        dz = to_waypoint.up - from_waypoint.up

        return np.sqrt(dx * dx + dy * dy + dz * dz)

    def calculate_enu_bearing(self, from_waypoint: Waypoint, to_waypoint: Waypoint) -> float:
        """Calculate bearing between two waypoints in ENU (degrees from North)."""
        dx = to_waypoint.east - from_waypoint.east
        dy = to_waypoint.north - from_waypoint.north

        # Calculate bearing in radians, then convert to degrees
        bearing_rad = np.arctan2(dx, dy)
        bearing_deg = np.degrees(bearing_rad)

        # Normalize to 0-360 degrees
        if bearing_deg < 0:
            bearing_deg += 360

        return bearing_deg


class CoordinateErrorGenerator:
    """Generates coordinate errors based on statistical parameters."""

    def __init__(self, seed: int = None):
        """Initialize random number generator."""
        self.rng = np.random.RandomState(seed)

    def generate_errors(self, mean: float, std_dev: float, size: int = 1) -> np.ndarray:
        """Generate normally distributed errors."""
        return self.rng.normal(mean, std_dev, size)

    def add_coordinate_errors(
        self, east: float, north: float, up: float, east_error: Tuple[float, float], north_error: Tuple[float, float], up_error: Tuple[float, float]
    ) -> Tuple[float, float, float]:
        """Add coordinate errors to ENU coordinates."""
        # Generate errors
        east_err = self.generate_errors(east_error[0], east_error[1])[0]
        north_err = self.generate_errors(north_error[0], north_error[1])[0]
        up_err = self.generate_errors(up_error[0], up_error[1])[0]

        # Apply errors
        east_with_error = east + east_err
        north_with_error = north + north_err
        up_with_error = up + up_err

        return east_with_error, north_with_error, up_with_error


def create_coordinate_transformer(base_point: BasePoint) -> CoordinateTransformer:
    """Create a coordinate transformer for the given base point."""
    return CoordinateTransformer(base_point)


def create_error_generator(seed: int = None) -> CoordinateErrorGenerator:
    """Create a coordinate error generator."""
    return CoordinateErrorGenerator(seed)
