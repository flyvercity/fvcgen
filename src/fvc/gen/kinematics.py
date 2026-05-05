"""Kinematic equations for object movement simulation."""

import logging
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from .config import Waypoint, ObjectConfig, Defaults

logger = logging.getLogger(__name__)


class MovementType(Enum):
    """Type of movement between waypoints."""

    LINEAR = 'linear'
    SMOOTH = 'smooth'  # Smooth transitions with acceleration/deceleration


@dataclass
class Position:
    """Object position at a specific time."""

    time: float
    east: float
    north: float
    up: float
    speed: float
    heading: float  # Bearing in degrees from North


@dataclass
class MovementSegment:
    """Movement segment between two waypoints."""

    start_waypoint: Waypoint
    end_waypoint: Waypoint
    start_time: float
    end_time: float
    distance: float
    speed: float
    heading: float


class KinematicCalculator:
    """Calculates object positions using kinematic equations."""

    def __init__(self, movement_type: MovementType = MovementType.LINEAR):
        """Initialize kinematic calculator."""
        self.movement_type = movement_type

    def calculate_segments(
        self, waypoints: List[Waypoint], start_delay: float, time_step: float, default_speed: float, circular: bool = False
    ) -> List[MovementSegment]:
        """Calculate movement segments from waypoints."""
        if len(waypoints) < 2:
            raise ValueError('At least 2 waypoints required')

        segments = []
        current_time = start_delay

        # Create waypoint list (add first waypoint at end if circular)
        wp_list = waypoints.copy()
        if circular and len(wp_list) > 2:
            wp_list.append(wp_list[0])

        for i in range(len(wp_list) - 1):
            start_wp = wp_list[i]
            end_wp = wp_list[i + 1]

            # Calculate distance and heading
            distance = self._calculate_distance(start_wp, end_wp)
            heading = self._calculate_heading(start_wp, end_wp)

            # Use waypoint speed (prefer end waypoint, then start waypoint) or default speed
            speed = end_wp.speed if end_wp.speed is not None else (start_wp.speed if start_wp.speed is not None else default_speed)
            speed_source = 'end_waypoint' if end_wp.speed is not None else ('start_waypoint' if start_wp.speed is not None else 'default')

            if speed is None or speed <= 0:
                raise ValueError(f'Invalid speed for segment {i}: {speed}')

            # Calculate segment duration
            duration = distance / speed
            end_time = current_time + duration

            segment = MovementSegment(
                start_waypoint=start_wp, end_waypoint=end_wp, start_time=current_time, end_time=end_time, distance=distance, speed=speed, heading=heading
            )

            logger.info(
                f'Segment {i}: start=({start_wp.east:.2f}, {start_wp.north:.2f}, {start_wp.up:.2f}), '
                f'end=({end_wp.east:.2f}, {end_wp.north:.2f}, {end_wp.up:.2f}), '
                f'distance={distance:.2f}m, speed={speed:.2f}m/s ({speed_source}), '
                f'heading={heading:.2f}°, duration={duration:.2f}s, '
                f'time_range=[{current_time:.2f}s, {end_time:.2f}s]'
            )

            segments.append(segment)
            current_time = end_time

        return segments

    def generate_trajectory(self, segments: List[MovementSegment], time_step: float) -> List[Position]:
        """Generate trajectory positions for all segments."""
        if not segments:
            return []

        # Calculate total time range
        start_time = segments[0].start_time
        end_time = segments[-1].end_time

        # Generate time points
        time_points = np.arange(start_time, end_time + time_step, time_step)

        positions = []
        for time in time_points:
            position = self._calculate_position_at_time(segments, time)
            if position:
                positions.append(position)

        return positions

    def _calculate_position_at_time(self, segments: List[MovementSegment], time: float) -> Optional[Position]:
        """Calculate object position at specific time."""
        # Find the segment containing this time
        for segment in segments:
            if segment.start_time <= time <= segment.end_time:
                return self._interpolate_position(segment, time)

        # Time is outside all segments
        return None

    def _interpolate_position(self, segment: MovementSegment, time: float) -> Position:
        """Interpolate position within a segment."""
        if self.movement_type == MovementType.LINEAR:
            return self._linear_interpolation(segment, time)
        elif self.movement_type == MovementType.SMOOTH:
            return self._smooth_interpolation(segment, time)
        else:
            raise ValueError(f'Unknown movement type: {self.movement_type}')

    def _linear_interpolation(self, segment: MovementSegment, time: float) -> Position:
        """Linear interpolation between waypoints."""
        # Calculate progress within segment (0 to 1)
        segment_duration = segment.end_time - segment.start_time
        if segment_duration <= 0:
            progress = 1.0
        else:
            progress = (time - segment.start_time) / segment_duration

        # Clamp progress to [0, 1]
        progress = max(0.0, min(1.0, progress))

        # Linear interpolation
        start = segment.start_waypoint
        end = segment.end_waypoint

        east = start.east + progress * (end.east - start.east)
        north = start.north + progress * (end.north - start.north)
        up = start.up + progress * (end.up - start.up)

        return Position(time=time, east=east, north=north, up=up, speed=segment.speed, heading=segment.heading)

    def _smooth_interpolation(self, segment: MovementSegment, time: float) -> Position:
        """Smooth interpolation with acceleration/deceleration."""
        # For now, use linear interpolation
        # TODO: Implement smooth transitions with acceleration/deceleration
        return self._linear_interpolation(segment, time)

    def _calculate_distance(self, wp1: Waypoint, wp2: Waypoint) -> float:
        """Calculate distance between two waypoints."""
        dx = wp2.east - wp1.east
        dy = wp2.north - wp1.north
        dz = wp2.up - wp1.up

        return np.sqrt(dx * dx + dy * dy + dz * dz)

    def _calculate_heading(self, wp1: Waypoint, wp2: Waypoint) -> float:
        """Calculate heading from wp1 to wp2 (degrees from North)."""
        dx = wp2.east - wp1.east
        dy = wp2.north - wp1.north

        # Calculate bearing in radians, then convert to degrees
        heading_rad = np.arctan2(dx, dy)
        heading_deg = np.degrees(heading_rad)

        # Normalize to 0-360 degrees
        if heading_deg < 0:
            heading_deg += 360

        return heading_deg


class TrajectoryGenerator:
    """Generates complete trajectories for objects."""

    def __init__(self, movement_type: MovementType = MovementType.LINEAR):
        """Initialize trajectory generator."""
        self.calculator = KinematicCalculator(movement_type)

    def generate_object_trajectory(self, object_config: ObjectConfig, defaults: Defaults) -> List[Position]:
        """Generate complete trajectory for an object."""
        logger.info(
            f'Generating trajectory for object(s) {object_config.id}: '
            f'{len(object_config.waypoints)} waypoints, start_delay={object_config.start_delay:.2f}s, '
            f'circular={object_config.circular}, default_speed={defaults.speed:.2f}m/s, '
            f'time_step={defaults.time_step:.2f}s'
        )

        # Calculate movement segments
        segments = self.calculator.calculate_segments(
            waypoints=object_config.waypoints,
            start_delay=object_config.start_delay,
            time_step=defaults.time_step,
            default_speed=defaults.speed,
            circular=object_config.circular,
        )

        logger.info(f'Calculated {len(segments)} segment(s) for object(s) {object_config.id}')

        # Generate trajectory positions
        trajectory = self.calculator.generate_trajectory(segments, defaults.time_step)

        logger.info(f'Generated {len(trajectory)} trajectory point(s) for object(s) {object_config.id}')

        return trajectory

    def generate_all_trajectories(self, origins: List, general_defaults: Defaults) -> List[List[Position]]:
        """Generate trajectories for all objects in all origins."""
        all_trajectories = []

        for origin in origins:
            for obj_config in origin.objects:
                # Get effective defaults for this object
                # This would need access to the full config to determine defaults hierarchy
                # For now, use general defaults
                trajectory = self.generate_object_trajectory(obj_config, general_defaults)
                all_trajectories.append(trajectory)

        return all_trajectories


def create_trajectory_generator(movement_type: MovementType = MovementType.LINEAR) -> TrajectoryGenerator:
    """Create a trajectory generator."""
    return TrajectoryGenerator(movement_type)
