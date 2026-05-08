# Flight Scenario Generator Specification

## Overview
The Scenario Generator (hereinafter Generator) should create FVC files for objects according to a configuration file.

## Configuration File Structure
The configuration file should contain a general section and an objects settings section.

### General Section
The general section should contain:
- Geographic coordinates of the scenario base point (for converting coordinates from ENU)
- Default values (applied to all objects for which not explicitly specified):
  - Object speed
  - Object altitude
  - Mean and standard deviation of coordinate determination errors (along three axes of the trajectory coordinate system, oriented along the tangent to the trajectory, then recalculate them to ENU)
  - Time step for coordinate updates (seconds)
- Path and name of the output file (optional)

### Objects Settings Section
The objects settings section should contain:
- List of origins, each including:
  - Default values similar to those mentioned above, but applicable within this origin
  - List of objects, each including:
    - Object identifier(s)
    - Default values similar to those mentioned above, applicable to the object (optional)
    - Object start delay in the scenario (seconds) (optional, if not specified then 0)
    - List of waypoints of the object in ENU coordinate system, containing:
      - ENU coordinates relative to the base point, meters
      - Object speed on the section from this to the next waypoint (optional)

## Core Requirements

### 1. Kinematic Calculations
Object coordinates should be calculated in accordance with the kinematic equations of motion of a material point.

### 2. Smooth Transitions (Optional)
Make smooth changes in trajectory and speed when passing through waypoints.

### 3. Coordinate Uncertainty
Object coordinates should be determined as a normally distributed unbiased random variable with given distribution parameters (mathematical expectation and standard deviation - specified in settings).

### 4. Circular Routes (Optional)
Add the ability to fly along a circular route, where the last waypoint from the list is connected to the first (need to add a setting).

### 5. Output Configuration
Provide the ability to specify the name and path of the output file in command line parameters and in the configuration file.

### 6. Template Generation
Provide the ability to generate a configuration file template in command line parameters.

### 7. Streaming Output (Optional)
Make streaming data output for transmission to fusion.

## Output Format

* The output file should be in Flyvercity Common Format (`fvc`), based on jsonlines format.
* The first string should be the metadata record: `{"origin": "example.yaml", "content": "flightlog", "source": "fvcgen"}`
* For each simulation step, and for each object, a new record should be added to the file.
* The record should contain the following nested fields:
  * `time.unix` — simulation timestamp in milliseconds
  * `time.rx` — simulated reception timestamp in milliseconds (present when `transmission_delay` is configured)
  * `uaid.int` — object identifier string
  * `pos.loc.lat` — latitude (degrees)
  * `pos.loc.lon` — longitude (degrees)
  * `pos.loc.alt` — altitude (meters)
  * `origin` — origin name (present when `include_origin` is enabled)
* When `transmission_delay` is configured, records should be sorted by `rx` time.
* Each record shall match the schema specified here: https://github.com/flyvercity/fvctools/blob/main/src/fvc/tools/df/schema.yaml

## Technical Implementation Notes

- Use ENU (East-North-Up) coordinate system
- Implement proper geodesic transformations between coordinate systems
- Handle timing and synchronization carefully for accuracy
- Support both deterministic and stochastic coordinate generation
- Ensure compatibility with existing FVC tools and formats
