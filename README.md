# Home Assistant FusionSolar Integration
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Integrate FusionSolar into you Home Assistant.

The integration is able to work with Kiosk mode, or with an OpenAPI account, see below for more details.

## Installation
At this point the integration is not part of the default HACS repositories, so
you will need to add this repository as a custom repository in HACS.

When this is done, just install the repository.

The configuration happens in the configuration flow when you add the integration.

## Kiosk
FusionSolar has a kiosk mode. The kiosk is a dashboard that is accessible for everyone that has the url.
The integration uses a JSON REST api that is also consumed by the kiosk.

The integration updates the data every 10 minutes.

**In kiosk mode the "realtime" data is not really realtime, it is cached at FusionSolars end for 30 minutes.**

If you need more accurate information you should use the OpenAPI mode.

## OpenAPI
You will need an OpenAPI account from Huawei for this to work. [More information](https://forum.huawei.com/enterprise/en/communicate-with-fusionsolar-through-an-openapi-account/thread/591478-100027)

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
request from Huawei. But the names are pretty self explanatory.

The realtime data is updated every minute.

### Total yields
The integration updates the total yields (current day, current month, current year, lifetime) every 10 minutes. 
