# Home Assistant FusionSolar Integration
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Integrate FusionSolar into you Home Assistant.

The integration is able to work with Kiosk mode, or with an OpenAPI account, see below for more details.

## Installation
At this point the integration is not part of the default HACS repositories, so
you will need to add this repository as a custom repository in HACS.

When this is done, just install the repository.

The configuration happens in the configuration flow when you add the integration.

## Configuration
### Kiosk
FusionSolar has a kiosk mode. The kiosk is a dashboard that is accessible for everyone that has the url.
The integration uses a JSON REST api that is also consumed by the kiosk.

**In kiosk mode the "realtime" data is not really realtime, it is cached at FusionSolars end for 30 minutes.**

If you need more accurate information you should use the OpenAPI mode.

### OpenAPI
You will need an OpenAPI account from Huawei for this to work. [More information](https://forum.huawei.com/enterprise/en/communicate-with-fusionsolar-through-an-openapi-account/thread/591478-100027)
