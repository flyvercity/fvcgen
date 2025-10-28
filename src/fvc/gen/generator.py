"""FVC file generation logic."""

import sys
import json
from pathlib import Path
from typing import List, TextIO
import numpy as np

from rich.console import Console

from .config import Config, ObjectConfig
from .geodesy import CoordinateTransformer, CoordinateErrorGenerator
from .kinematics import TrajectoryGenerator, Position, MovementType

console = Console()


class FVCGenerator:
    """Generates FVC files from configuration."""

    def __init__(self, config: Config, movement_type: MovementType = MovementType.LINEAR):
        """Initialize FVC generator."""
        self.config = config
        self.transformer = CoordinateTransformer(config.general.base_point)
        self.error_generator = CoordinateErrorGenerator()
        self.trajectory_generator = TrajectoryGenerator(movement_type)

    def generate(self) -> None:
        """Generate FVC file and save to output path."""
        output_path = self.config.general.output_file

        if output_path:
            self._generate_to_file(output_path)
        else:
            self._generate_to_stdout()

    def generate_stream(self) -> None:
        """Generate FVC data and stream to stdout."""
        self._generate_to_stdout()

    def _generate_to_file(self, output_path: str) -> None:
        """Generate FVC file to specified path."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            self._write_fvc_content(f)

        console.print(f'[green]FVC file generated: {path}[/green]')

    def _generate_to_stdout(self) -> None:
        """Generate FVC content to stdout."""
        self._write_fvc_content(sys.stdout)

    def _write_fvc_content(self, output: TextIO) -> None:
        """Write FVC content to output stream."""
        # Write FVC header
        self._write_header(output)

        # Generate records for all objects first, then emit in chronological order
        all_records = []
        for origin_idx, origin in enumerate(self.config.origins):
            for obj_idx, obj_config in enumerate(origin.objects):
                all_records.extend(self._generate_object_records(origin_idx, obj_idx, obj_config))

        # Sort by time to simulate natural flow of time
        all_records.sort(key=lambda r: r['time']['unix'])

        for record in all_records:
            output.write(json.dumps(record) + '\n')

    def _write_header(self, output: TextIO) -> None:
        """Write FVC file metadata record."""
        origin_name = None
        if getattr(self.config, 'source_path', None):
            try:
                origin_name = Path(self.config.source_path).name
            except Exception:
                origin_name = str(self.config.source_path)
        metadata = {
            'origin': origin_name or 'fvcgen_scenario.fvc',
            'content': 'flightlog',
            'source': 'fvcgen'
        }
        output.write(json.dumps(metadata) + '\n')

    def _generate_object_records(self, origin_idx: int, obj_idx: int, obj_config: ObjectConfig) -> list[dict]:
        """Generate trajectory records for a single object."""
        # Get effective defaults for this object
        defaults = self.config.get_object_defaults(origin_idx, obj_idx)

        # Generate trajectory
        trajectory = self.trajectory_generator.generate_object_trajectory(obj_config, defaults)

        if not trajectory:
            console.print(f'[yellow]Warning: No trajectory generated for object {obj_config.id}[/yellow]')
            return []

        records: list[dict] = []
        for position in trajectory:
            # Convert ENU to geographic coordinates
            lat, lon, alt = self.transformer.enu_to_geographic(position.east, position.north, position.up)

            # Add coordinate errors
            lat, lon, alt = self._add_coordinate_errors(lat, lon, alt, defaults.coordinate_errors)

            # Create data line for each object ID
            for obj_id in obj_config.id:
                record = {
                    'time': {'unix': int(position.time * 1000)},
                    'uaid': {'int': obj_id},
                    'pos': {
                        'loc': {
                            'lat': lat,
                            'lon': lon,
                            'alt': alt
                        }
                    }
                }
                records.append(record)

        return records

    def _add_coordinate_errors(self, lat: float, lon: float, alt: float, coordinate_errors) -> tuple[float, float, float]:
        """Add coordinate errors to geographic coordinates."""
        # Convert errors from ENU to geographic
        # This is a simplified approach - in practice, you'd need proper error propagation

        # For now, add errors directly to lat/lon/alt
        # TODO: Implement proper error propagation from ENU to geographic coordinates

        lat_error = (
            self.error_generator.generate_errors(coordinate_errors.north.mean, coordinate_errors.north.std_dev)[0] / 111000.0
        )  # Rough conversion from meters to degrees

        lon_error = self.error_generator.generate_errors(coordinate_errors.east.mean, coordinate_errors.east.std_dev)[0] / (
            111000.0 * np.cos(np.radians(lat))
        )  # Account for latitude

        alt_error = self.error_generator.generate_errors(coordinate_errors.up.mean, coordinate_errors.up.std_dev)[0]

        return lat + lat_error, lon + lon_error, alt + alt_error


class FVCValidator:
    """Validates FVC files and configurations."""

    @staticmethod
    def validate_config(config: Config) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        # Check general configuration
        if not config.general.base_point:
            issues.append('Base point is required')

        if config.general.defaults.time_step <= 0:
            issues.append('Time step must be positive')

        if config.general.defaults.speed < 0:
            issues.append('Default speed cannot be negative')

        # Check origins and objects
        if not config.origins:
            issues.append('At least one origin is required')

        for origin_idx, origin in enumerate(config.origins):
            if not origin.objects:
                issues.append(f'Origin {origin_idx} has no objects')

            for obj_idx, obj in enumerate(origin.objects):
                if not obj.id:
                    issues.append(f'Object {obj_idx} in origin {origin_idx} has no ID')

                if len(obj.waypoints) < 2:
                    issues.append(f'Object {obj.id} has less than 2 waypoints')

                # Check for valid speeds
                for wp_idx, wp in enumerate(obj.waypoints):
                    if wp.speed is not None and wp.speed < 0:
                        issues.append(f'Object {obj.id} waypoint {wp_idx} has negative speed')

        return issues

    @staticmethod
    def validate_trajectory(trajectory: List[Position]) -> List[str]:
        """Validate trajectory and return list of issues."""
        issues = []

        if not trajectory:
            issues.append('Empty trajectory')
            return issues

        # Check for time consistency
        times = [pos.time for pos in trajectory]
        if times != sorted(times):
            issues.append('Trajectory times are not monotonically increasing')

        # Check for reasonable positions
        for i, pos in enumerate(trajectory):
            if not (-90 <= pos.east <= 90):  # Rough check for lat-like values
                issues.append(f'Position {i} has invalid east coordinate: {pos.east}')

            if not (-180 <= pos.north <= 180):  # Rough check for lon-like values
                issues.append(f'Position {i} has invalid north coordinate: {pos.north}')

        return issues


def create_fvc_generator(config: Config, movement_type: MovementType = MovementType.LINEAR) -> FVCGenerator:
    """Create an FVC generator."""
    return FVCGenerator(config, movement_type)


def validate_fvc_config(config: Config) -> bool:
    """Validate FVC configuration and return True if valid."""
    issues = FVCValidator.validate_config(config)
    if issues:
        console.print('[red]Configuration validation failed:[/red]')
        for issue in issues:
            console.print(f'  - {issue}')
        return False
    return True
