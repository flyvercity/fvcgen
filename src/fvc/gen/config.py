"""Configuration models for FVC Generator."""

from pathlib import Path
from typing import List, Optional, Union
import yaml
from pydantic import BaseModel, Field, field_validator, field_serializer
from pygeodesy.ellipsoidalKarney import LatLon


class CoordinateError(BaseModel):
    """Coordinate determination error parameters."""

    mean: float = Field(..., description='Mean error (meters)')
    std_dev: float = Field(..., ge=0, description='Standard deviation (meters)')

    @field_serializer('mean', 'std_dev')
    def serialize_float_6(self, value: float) -> float:
        """Serialize float values with 6 decimal places."""
        return round(value, 6)


class CoordinateErrors(BaseModel):
    """Coordinate errors for all three axes."""

    east: CoordinateError = Field(..., description='East axis error')
    north: CoordinateError = Field(..., description='North axis error')
    up: CoordinateError = Field(..., description='Up axis error')


class Defaults(BaseModel):
    """Default values for objects."""

    speed: float = Field(..., ge=0, description='Default speed (m/s)')
    altitude: float = Field(..., description='Default altitude (meters)')
    coordinate_errors: CoordinateErrors = Field(..., description='Coordinate determination errors')
    time_step: float = Field(..., gt=0, description='Time step (seconds)')


class BasePoint(BaseModel):
    """Geographic base point for coordinate conversion."""

    lat: float = Field(..., ge=-90, le=90, description='Latitude (degrees)')
    lon: float = Field(..., ge=-180, le=180, description='Longitude (degrees)')
    alt: float = Field(default=0.0, description='Altitude (meters)')

    @field_validator('lat', 'lon')
    @classmethod
    def validate_coordinates(cls, v):
        """Validate coordinate values."""
        if not isinstance(v, (int, float)):
            raise ValueError('Coordinates must be numeric')
        return float(v)

    def to_latlon(self) -> LatLon:
        """Convert to pygeodesy LatLon object."""
        return LatLon(self.lat, self.lon, height=self.alt)


class GeneralConfig(BaseModel):
    """General configuration section."""

    base_point: BasePoint = Field(..., description='Geographic base point')
    defaults: Defaults = Field(..., description='Default values')
    output_file: Optional[str] = Field(None, description='Output file path')


class Waypoint(BaseModel):
    """Waypoint in ENU coordinate system."""

    east: float = Field(..., description='East coordinate (meters)')
    north: float = Field(..., description='North coordinate (meters)')
    up: float = Field(..., description='Up coordinate (meters)')
    speed: Optional[float] = Field(None, ge=0, description='Speed (m/s)')

    @field_serializer('east', 'north', 'up', 'speed')
    def serialize_float_3(self, value: Optional[float]) -> Optional[float]:
        """Serialize float values with 3 decimal places."""
        return round(value, 3) if value is not None else None


class ObjectConfig(BaseModel):
    """Object configuration."""

    id: Union[str, List[str]] = Field(..., description='Object identifier(s)')
    defaults: Optional[Defaults] = Field(None, description='Object defaults')
    start_delay: float = Field(default=0.0, ge=0, description='Start delay (s)')
    waypoints: List[Waypoint] = Field(..., min_length=1, description='Waypoints in ENU')
    circular: bool = Field(default=False, description='Enable circular route')

    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Ensure id is always a list."""
        if isinstance(v, str):
            return [v]
        return v


class OriginConfig(BaseModel):
    """Origin configuration section."""

    defaults: Optional[Defaults] = Field(None, description='Origin defaults')
    objects: List[ObjectConfig] = Field(..., min_length=1, description='Objects in origin')


class Config(BaseModel):
    """Main configuration model."""

    general: GeneralConfig = Field(..., description='General configuration')
    origins: List[OriginConfig] = Field(..., min_length=1, description='Origins configuration')
    source_path: Optional[str] = Field(default=None, exclude=True, description='Path to the configuration file (internal)')

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Config':
        """Load configuration from YAML file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f'Configuration file not found: {path}')

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        config = cls.model_validate(data)
        # Store source path for later use (e.g., metadata origin field)
        config.source_path = str(path)
        return config

    def to_file(self, file_path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, indent=2, sort_keys=False)

    def get_object_defaults(self, origin_idx: int, object_idx: int) -> Defaults:
        """Get effective defaults for an object."""
        obj = self.origins[origin_idx].objects[object_idx]
        origin = self.origins[origin_idx]

        # Start with general defaults
        defaults = self.general.defaults

        # Override with origin defaults if available
        if origin.defaults:
            defaults = defaults.model_copy(update=origin.defaults.model_dump(exclude_unset=True))

        # Override with object defaults if available
        if obj.defaults:
            defaults = defaults.model_copy(update=obj.defaults.model_dump(exclude_unset=True))

        return defaults
