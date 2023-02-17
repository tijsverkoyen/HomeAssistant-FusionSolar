# Home Assistant FusionSolar Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Integrate FusionSolar into you Home Assistant.

The integration is able to work with Kiosk mode, or with an OpenAPI account, see below for more details.

## Installation

This integration is part of the default HACS repositories, so can add it directly from HACS or add this repository as a
custom repository in HACS.

When the integration is installed in HACS, you need to add it in Home Assistant: Settings → Devices & Services → Add
Integration → Search for FusionSolar.

The configuration happens in the configuration flow when you add the integration.

## Kiosk

FusionSolar has a kiosk mode. The kiosk is a dashboard that is accessible for everyone that has the url.
The integration uses a JSON REST api that is also consumed by the kiosk.

The integration updates the data every 10 minutes.

**In kiosk mode the "realtime" data is not really realtime, it is cached at FusionSolars end for 30 minutes.**

If you need more accurate information you should use the OpenAPI mode.

## OpenAPI

You will need an OpenAPI account from Huawei for this to
work. [More information](https://forum.huawei.com/enterprise/en/communicate-with-fusionsolar-through-an-openapi-account/thread/591478-100027)

The integration will expose the different devices (Residential inverter, String inverter, Battery, Dongle, ...) in
your plant/station.

### Realtime data

The devices that support realtime information (getDevRealKpi api call):

* String inverter
* EMI
* Grid meter
* Residential inverter
* Battery
* Power Sensor

The exposed entities can be different per device. These are documented in the "Interface reference" that you can
request from Huawei. But the names are pretty self-explanatory.

The realtime data is updated every minute per device group. As the API only allows 1 call per minute to each
endpoint and the same endpoint is needed for each device group. So the more different devices you have the slower
the update will be. See [Disabling devices](#disabling-devices)

### Total yields

The integration updates the total yields (current day, current month, current year, lifetime) every 10 minutes.

## FAQ

### Where can I find the kiosk url?

1. Login to the [FusionSolar portal](https://eu5.fusionsolar.huawei.com/)
2. Select your plant in the overview (Home → List view → Click on your plant name)
3. You will be redirect to the "Monitoring" page
4. Click on the "Kiosk" button in the top right corner
5. Enable the "Kiosk mode" in the popup if needed
6. Copy the url from the browser

If you don't see the kiosk button, you are probably logged in with an installer account.

### Energy Dashboard: Active Power not showing in the list of available entities

Active Power is the current power production in Watt (W) or kilo Watt (kW). The Energy dashboard expects a value in *
*kWh**.
Your plant, inverter(s), batteries, ... expose a lot of entities, you can see them all: Settings → Devices &
Integrations → Click on the "x devices" on the Fusion Solar Integration. Click on the device you want to see the
entities for.

### What do all entities mean?

As I don't own an installation with all possible devices this integration is mostly based on
the [Northbound Interface Reference](/docs/smartpvms-v500r007c00-northbound-interface-reference.pdf).

The entity names are based on the names in the interface reference.

### Disabling devices

If you have a lot of devices wherefor you don't want to use the data. You can disable them through the interface:
Settings → Devices & Integrations → Click on the "x devices" on the Fusion Solar Integration. Click on the device you
want to disable. Click on the pencil icon in the upper right corner. Switch off "Enable device".

This can speed up the updating of the other devices. Keep in mind that a call is made per device type. So if you have
multiple devices from the same time you need to disable them all to have effect.
