# Transmission Delay Simulation

## Summary

Add optional simulation of transmission delays to fvcgen. When configured, each generated record receives an `rx` (reception time) field in addition to the existing `unix` (validity time) field. Output is sorted by reception time to simulate how a ground system actually receives data.

## Motivation

Currently, each record has a single `unix` timestamp that conflates information validity time with reception time. In real systems these differ — data arrives after a transmission delay that varies by aircraft, link quality, and conditions. Simulating this allows testing ground systems against realistic reception ordering, including edge cases like "data from the future" (negative delay).

## Configuration Model

### New field: `transmission_delay`

Added as an optional field in `Defaults` and `PartialDefaults`, reusing the existing `CoordinateError` model shape:

```yaml
general:
  defaults:
    transmission_delay:
      mean: 200.0    # mean delay in milliseconds
      std_dev: 50.0  # std_dev in milliseconds (0 = constant delay)
```

- **Type:** `Optional[CoordinateError]` — reuses the existing model (mean + std_dev)
- **Default:** `None` — feature disabled, no `rx` field emitted, sort by `unix`
- **Units:** milliseconds (matches `time.unix`)
- **Hierarchy:** general → origin → object (same override pattern as all other defaults)
- **No clamping:** negative sampled values are valid (simulates "data from the future" errors)

### Constant delay mode

Set `std_dev: 0` — every record gets exactly `mean` ms of delay.

### Statistical delay mode

Set `std_dev > 0` — delay is sampled from `N(mean, std_dev)` independently per record.

## Output Format

When `transmission_delay` is configured, each record's `time` object gains an `rx` field:

```json
{"time": {"unix": 1756033206882, "rx": 1756033207094}, "uaid": {"int": "UAS-001"}, "pos": {...}}
```

- `unix` — validity time (when position was true), unchanged
- `rx` — reception time (`unix + sampled_delay_ms`, rounded to integer)

When `transmission_delay` is not configured, output is identical to current behavior (no `rx` field).

## Sorting

- When any record has an `rx` field: sort all records by `rx` (records without `rx` fall back to `unix` as sort key)
- When no records have `rx`: sort by `unix` (current behavior)

This simulates the order a ground system receives data, which may differ from validity order.

## Generator Logic

Changes are confined to `FVCGenerator._generate_object_records` and `_write_fvc_content`:

1. In `_generate_object_records`, after building each record dict:
   - If effective defaults have `transmission_delay`:
     - Sample delay: `numpy.random.normal(mean, std_dev)` (or just `mean` if `std_dev == 0`)
     - Compute `rx = int(position.time * 1000) + int(round(delay))`
     - Add `'rx': rx` to the record's `'time'` dict

2. In `_write_fvc_content`, change sort key:
   - Use `record['time'].get('rx', record['time']['unix'])` as sort key

No changes to kinematics, geodesy, or the `Position` dataclass.

## Configuration Merge

In `deep_merge_defaults`:
- Add `transmission_delay` as one more field
- In `PartialDefaults`, the type is `Optional[CoordinateError]` (a complete value, not a partial) — this means an override either provides both mean and std_dev, or is absent
- Override semantics: if the override provides `transmission_delay`, it replaces the base value entirely
- If override is `None`, base value is preserved

## Template

Update `config-template.yaml` to include a commented-out example:

```yaml
general:
  defaults:
    # transmission_delay:
    #   mean: 200.0
    #   std_dev: 50.0
```

## Testing

Four unit tests:

1. **Constant delay:** configure `transmission_delay` with `std_dev: 0`, verify every record has `rx = unix + mean`
2. **Absence:** no `transmission_delay` configured, verify no `rx` field appears, records sorted by `unix`
3. **Hierarchical override:** object-level delay overrides origin-level which overrides general-level
4. **Sort order:** with delays present, verify output is sorted by `rx`, including cases where `rx` reorders records relative to `unix` order

No new test dependencies — existing pytest setup is sufficient.

## Files Modified

- `src/fvc/gen/config.py` — add `transmission_delay` to `Defaults` and `PartialDefaults`, update `deep_merge_defaults`
- `src/fvc/gen/generator.py` — apply delay in `_generate_object_records`, update sort key in `_write_fvc_content`
- `config-template.yaml` — add commented-out example
- `tests/test_config.py` or new test file — add 4 unit tests
