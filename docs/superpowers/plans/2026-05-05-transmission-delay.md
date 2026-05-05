# Transmission Delay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional transmission delay simulation that produces an `rx` timestamp in output records and sorts by reception time.

**Architecture:** Add `transmission_delay` (Optional[CoordinateError]) to Defaults/PartialDefaults, sample delay per record in the generator, emit `rx` field in time object, sort by `rx` when present.

**Tech Stack:** Python 3.13, Pydantic v2, numpy, pytest

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `src/fvc/gen/config.py` | Modify | Add `transmission_delay` field to `Defaults` and `PartialDefaults`, update `deep_merge_defaults` |
| `src/fvc/gen/generator.py` | Modify | Sample delay, add `rx` to records, update sort key |
| `src/fvc/gen/utils.py` | Modify | Add commented-out `transmission_delay` to template config |
| `tests/test_transmission_delay.py` | Create | All transmission delay tests |

---

### Task 1: Add `transmission_delay` to config models

**Files:**
- Modify: `src/fvc/gen/config.py:55-60` (Defaults class)
- Modify: `src/fvc/gen/config.py:64-69` (PartialDefaults class)
- Modify: `src/fvc/gen/config.py:140-170` (deep_merge_defaults function)
- Test: `tests/test_transmission_delay.py`

- [ ] **Step 1: Write the failing test for config with transmission_delay**

Create `tests/test_transmission_delay.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_transmission_delay.py -v`
Expected: FAIL — `transmission_delay` field not recognized by Defaults model

- [ ] **Step 3: Add `transmission_delay` to `Defaults` and `PartialDefaults`**

In `src/fvc/gen/config.py`, add to the `Defaults` class:

```python
class Defaults(BaseModel):
    """Default values for objects."""

    speed: float = Field(..., ge=0, description='Default speed (m/s)')
    altitude: float = Field(..., description='Default altitude (meters)')
    coordinate_errors: CoordinateErrors = Field(..., description='Coordinate determination errors')
    time_step: float = Field(..., gt=0, description='Time step (seconds)')
    transmission_delay: Optional[CoordinateError] = Field(None, description='Transmission delay (ms): mean and std_dev')
```

In `src/fvc/gen/config.py`, add to the `PartialDefaults` class:

```python
class PartialDefaults(BaseModel):
    """Partial override for Defaults, all fields optional."""

    speed: Optional[float] = Field(None, ge=0, description='Default speed (m/s)')
    altitude: Optional[float] = Field(None, description='Default altitude (meters)')
    coordinate_errors: Optional[PartialCoordinateErrors] = Field(None, description='Coordinate determination errors')
    time_step: Optional[float] = Field(None, gt=0, description='Time step (seconds)')
    transmission_delay: Optional[CoordinateError] = Field(None, description='Transmission delay (ms): mean and std_dev')
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_transmission_delay.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/fvc/gen/config.py tests/test_transmission_delay.py
git commit -m "feat(config): add transmission_delay field to Defaults and PartialDefaults"
```

---

### Task 2: Update `deep_merge_defaults` to handle `transmission_delay`

**Files:**
- Modify: `src/fvc/gen/config.py:140-170` (deep_merge_defaults function)
- Test: `tests/test_transmission_delay.py`

- [ ] **Step 1: Write the failing test for hierarchical override**

Append to `tests/test_transmission_delay.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_transmission_delay.py::test_deep_merge_transmission_delay_override -v`
Expected: FAIL — `deep_merge_defaults` doesn't handle `transmission_delay` yet

- [ ] **Step 3: Update `deep_merge_defaults`**

In `src/fvc/gen/config.py`, update the `deep_merge_defaults` function. Add after the `time_step` line:

```python
def deep_merge_defaults(base: Defaults, override: PartialDefaults) -> Defaults:
    """Deep-merge a PartialDefaults into Defaults, returning a new Defaults."""
    speed = override.speed if override.speed is not None else base.speed
    altitude = override.altitude if override.altitude is not None else base.altitude
    time_step = override.time_step if override.time_step is not None else base.time_step
    transmission_delay = override.transmission_delay if override.transmission_delay is not None else base.transmission_delay

    # Merge coordinate errors
    ce = base.coordinate_errors
    o_ce = override.coordinate_errors

    def merge_axis(base_axis: CoordinateError, override_axis: Optional[PartialCoordinateError]) -> CoordinateError:
        if override_axis is None:
            return base_axis
        mean = override_axis.mean if override_axis.mean is not None else base_axis.mean
        std_dev = override_axis.std_dev if override_axis.std_dev is not None else base_axis.std_dev
        return CoordinateError(mean=mean, std_dev=std_dev)

    east = merge_axis(ce.east, o_ce.east if o_ce else None)
    north = merge_axis(ce.north, o_ce.north if o_ce else None)
    up = merge_axis(ce.up, o_ce.up if o_ce else None)

    merged_ce = CoordinateErrors(east=east, north=north, up=up)

    return Defaults(speed=speed, altitude=altitude, coordinate_errors=merged_ce, time_step=time_step, transmission_delay=transmission_delay)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_transmission_delay.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/fvc/gen/config.py tests/test_transmission_delay.py
git commit -m "feat(config): handle transmission_delay in deep_merge_defaults"
```

---

### Task 3: Add `rx` field and sort by reception time in generator

**Files:**
- Modify: `src/fvc/gen/generator.py:85-105` (_generate_object_records method)
- Modify: `src/fvc/gen/generator.py:60-70` (_write_fvc_content method)
- Test: `tests/test_transmission_delay.py`

- [ ] **Step 1: Write the failing test for constant delay producing `rx`**

Append to `tests/test_transmission_delay.py`:

```python
import json
import io
from unittest.mock import patch
from fvc.gen.config import Config, GeneralConfig, BasePoint, Defaults, CoordinateErrors, CoordinateError, OriginConfig, ObjectConfig, Waypoint
from fvc.gen.generator import FVCGenerator


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_transmission_delay.py::test_constant_delay_produces_rx tests/test_transmission_delay.py::test_no_delay_no_rx_field -v`
Expected: FAIL — no `rx` field produced

- [ ] **Step 3: Implement delay sampling in `_generate_object_records`**

In `src/fvc/gen/generator.py`, modify `_generate_object_records`. After the line that builds the `record` dict and before `records.append(record)`, add:

```python
                # Add transmission delay if configured
                if defaults.transmission_delay:
                    if defaults.transmission_delay.std_dev == 0:
                        delay = defaults.transmission_delay.mean
                    else:
                        delay = np.random.normal(defaults.transmission_delay.mean, defaults.transmission_delay.std_dev)
                    record['time']['rx'] = int(position.time * 1000) + int(round(delay))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_transmission_delay.py::test_constant_delay_produces_rx tests/test_transmission_delay.py::test_no_delay_no_rx_field -v`
Expected: PASS

- [ ] **Step 5: Write the failing test for sort order by `rx`**

Append to `tests/test_transmission_delay.py`:

```python
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
```

- [ ] **Step 6: Update sort key in `_write_fvc_content`**

In `src/fvc/gen/generator.py`, change the sort line in `_write_fvc_content` from:

```python
        all_records.sort(key=lambda r: r['time']['unix'])
```

to:

```python
        all_records.sort(key=lambda r: r['time'].get('rx', r['time']['unix']))
```

- [ ] **Step 7: Run all transmission delay tests**

Run: `uv run pytest tests/test_transmission_delay.py -v`
Expected: All PASS

- [ ] **Step 8: Run full test suite to verify no regressions**

Run: `uv run pytest -v`
Expected: All PASS

- [ ] **Step 9: Commit**

```bash
git add src/fvc/gen/generator.py tests/test_transmission_delay.py
git commit -m "feat(generator): add rx field with transmission delay and sort by reception time"
```

---

### Task 4: Update config template

**Files:**
- Modify: `src/fvc/gen/utils.py`

- [ ] **Step 1: Update `generate_config_template` to show commented-out transmission_delay**

The template is generated programmatically via `Config.to_file()`, which serializes the Pydantic model. Since `transmission_delay` defaults to `None`, it will serialize as `transmission_delay: null` automatically. However, to show a useful commented example, we add a post-write comment.

Actually, since the template uses `Config.to_file()` which calls `yaml.dump(self.model_dump())`, and `transmission_delay` is `None` by default, it will appear as `transmission_delay: null` in the output. This is acceptable — it shows the field exists and is disabled.

No code change needed — the field will appear in the template automatically once added to `Defaults`. Verify:

Run: `uv run fvcgen template -o /tmp/test-template.yaml && cat /tmp/test-template.yaml`
Expected: `transmission_delay: null` appears under `defaults`

- [ ] **Step 2: Commit (if any change was needed)**

If the output looks good with `transmission_delay: null`, no commit needed for this task.

---

### Task 5: Final verification

**Files:** None (verification only)

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -v`
Expected: All PASS

- [ ] **Step 2: Run linter**

Run: `uv run ruff check .`
Expected: No errors

- [ ] **Step 3: Run formatter**

Run: `uv run ruff format --check .`
Expected: No reformatting needed (or run `uv run ruff format .` to fix)

- [ ] **Step 4: Generate a scenario with transmission delay to verify end-to-end**

Create a test config or modify existing one to include `transmission_delay`, then generate:

Run: `uv run fvcgen generate -c config-template.yaml -o test-output.fvc`

Manually inspect a few lines of `test-output.fvc` to confirm no `rx` field (since template has `null`). Then test with an actual delay value by temporarily editing the config.

- [ ] **Step 5: Clean up test artifacts**

```bash
rm -f test-output.fvc
```
