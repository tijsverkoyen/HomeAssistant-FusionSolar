# Home Assisant FusionSolar Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Integrate FusionSolar into you Home Assistant.

FusionSolar has a kiosk mode. When this kiosk mode is enabled we can access 
data about our plants through a JSON REST api.


## Installation
At this point the integration is not part of the default HACS repositories, so
you will need to add this repository as a custom repository in HACS.

When this is done, just install the repository.


## Configuration

The configuration of this integration happens in a few steps:

### Enable kiosk mode
1. Sign in on the Huawei FusionSolar portal: [https://eu5.fusionsolar.huawei.com/](https://eu5.fusionsolar.huawei.com/).
2. Select your plant if needed.
2. At the top there is a button: "Kiosk", click it.
3. An overlay will open, and you need to enable the kiosk view by enabling the toggle.
4. Note down the url that is shown.

### Add into configuration
Open your `configuration.yaml`, add the code below:

    sensor:
      - platform: fusion_solar_kiosk
        kiosks:
          - url: "REPLACE THIS WITH THE KIOSK URL"
            name: "A readable name for the plant"

### Use secrets
I strongly advise to store the unique urls as a secret. The kiosk url is public, 
so anybody with the link can access your data. Be careful when sharing this.

More information on secrets: [Storing secrets](https://www.home-assistant.io/docs/configuration/secrets/).

### Multiple plants
You can configure multiple plants:

    sensor:
      - platform: fusion_solar_kiosk
        kiosks:
            - url: "KIOSK URL XXXXX"
              name: "A readable name for plant XXXXX"
            - url: "KIOSK URL YYYYY"
              name: "A readable name for plant YYYYY"
