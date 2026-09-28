# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Home Assistant custom integration for Huawei FusionSolar solar systems. It supports two connection modes:

- **Kiosk mode**: Public dashboard URL, cached data, updated every 10 minutes
- **OpenAPI mode**: Direct API access with real-time device data, updated every 63 seconds (rate-limited per device type)

## Development Setup

Run Home Assistant locally via Docker:

```bash
docker compose up
```

Access at `http://localhost:8123`. The entire repo mounts to `/config`.

## Validation (CI)

Two GitHub Actions workflows run on push/PR and daily:

- `hassfest`: Validates the integration manifest and structure
- `hacs`: Validates HACS compatibility

There are no unit tests. Validation is done by running the integration in a real Home Assistant instance.

## Architecture

### Directory Layout

```
custom_components/fusion_solar/       # HA integration entry points
    __init__.py                       # Setup and config entry handling
    config_flow.py                    # 3-step configuration wizard
    sensor.py                         # Sensor platform, all entity class definitions (~900 lines)
    device_real_kpi_coordinator.py    # OpenAPI data coordinator with rate limiting
    fusion_solar/                     # Reusable API library
        kiosk/                        # Kiosk REST API client
        openapi/                      # OpenAPI/Northbound API client
        *.py                          # Base entity classes and data models
```

### Two API Modes

**Kiosk** (`fusion_solar/kiosk/`): Extracts a kiosk ID from the URL via regex, calls a single public endpoint, decodes HTML-escaped JSON. Exposes realtime power and energy totals.

**OpenAPI** (`fusion_solar/openapi/`): Authenticates with username/password, stores token in `xsrf-token` header. Fetches station list, then device list per station, then real-time KPI per device group. Supports inverters, batteries, grid meters, power sensors, and EMI devices.

### Rate Limiting (OpenAPI)

`DeviceRealKpiDataCoordinator` cycles through device type groups one at a time per update tick (every 63 seconds). It calls one device type per cycle to stay within the API's 1-call/minute-per-endpoint limit. On `AccessFrequencyTooHighError`, it skips the update and backs off.

### Entity Hierarchy

All entities live in `sensor.py` and inherit from base classes in `fusion_solar/`:

- `FusionSolarPowerEntity` — kW sensors
- `FusionSolarPowerEntityRealtimeInWatt` — W sensors
- `FusionSolarEnergySensor` — kWh sensors (prevents midnight glitch: returns previous value if no production)
- `FusionSolarRealtimeDeviceDataSensor` — base for dynamic device metrics

Static attributes (device ESN, coordinates, station address) use `DIAGNOSTIC` entity category. Real-time metrics use `SENSOR`.

### Device Types

Supported `type_id` values: String inverter (1), EMI (10), Grid meter (17), Residential inverter (38), Battery (39), C&I ESS (41), Power sensor (47). The `Device.device_type` property maps these to human-readable strings.

### Unique IDs and Device Registry

Devices use `(DOMAIN, device_id)` as registry identifier. Entity unique IDs follow `fusion_solar-{entity}-{attribute}`. Stations and devices can be disabled via the HA UI; the coordinator skips disabled entries.

Device lookups use `device_registry.async_get_device_by_identifier((DOMAIN, id), config_entry_id)` (not the deprecated `async_get_device`) — it requires `config_entry_id`, threaded down from `async_setup_entry` through every function that resolves a device or its `via_device_id`. Parent-device linking uses `via_device_id` (the registry ID), not the deprecated `via_device` (identifier tuple); `FusionSolarDevice.via_device_id` is set once in `add_entities_for_stations` after the station device is registered, before device entities are created.

### Key Constants

- `custom_components/fusion_solar/const.py` — domain, config keys, entity IDs
- `custom_components/fusion_solar/fusion_solar/const.py` — API response field names, attribute mappings
