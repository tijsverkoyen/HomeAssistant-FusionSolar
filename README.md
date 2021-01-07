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
1. Sign in on the Huawei FusionSolar portal: [https://eu5.fusionsolar.huawei.com](https://eu5.fusionsolar.huawei.com).
2. At the top there is a link: Kiosk View, click it.
3. An overlay will open, and you need to enable the kioks view by enabling the toggle.
4. Note down the url that is shown.

We only need the unique id, which is located just after the `kk=`. So if your
url is `https://eu5.fusionsolar.huawei.com/singleKiosk.html?kk=XXXXX` the id is:
`XXXXX`.

### Add into configuration
Open your `configuration.yaml`, add the code below:

    sensor:
        - platform: fusion_solar_kiosk
        kiosks:
            - id: "XXXXX"
            name: "A readable name for the plant"

Make sure you replace the `XXXXX`, with the unique id.

### Use secrets
I would advice to store the unique id as a secret. With this uniaue token
anybody can access your kiosk url, so be carefull to share this.

More information on secrets: [Storing secrets](https://www.home-assistant.io/docs/configuration/secrets/).

### Multiple plants
You can configure multiple plants:

    sensor:
        - platform: fusion_solar_kiosk
        kiosks:
            - id: "XXXXX"
            name: "A readable name for plant XXXXX"
            - id: "YYYYY"
            name: "A readable name for plant YYYYY"


## Future plans

No of the items below are promises, so don't expect anything to happen soon:

### Build a view
Make a custom view that shows everything in a single card.

Possible inspiration:
* https://home-assistant-cards.bessarabov.com/
* https://github.com/denysdovhan/vacuum-card
* https://community.home-assistant.io/t/lovelace-power-wheel-card/82374
* https://community.home-assistant.io/t/solar-pv-system-card/80218
* https://github.com/gurbyz/power-wheel-card
* https://github.com/reptilex/tesla-style-solar-power-card

### Add power chart
Add the power chart

### Add social contributions
Add the social contributions


## Known issues
### Detected I/O inside the event loop

    2020-12-15 19:30:34 WARNING (MainThread) [homeassistant.util.async_] Detected I/O inside the event loop. This is causing stability issues. Please report issue to the custom component author for fusion_solar_kiosk doing I/O at custom_components/fusion_solar_kiosk/sensor.py, line 116: response = post(url, headers=headers, data=json.dumps(data))

Something like above will be shown in the logs. I am aware of this. I will look 
into this when my python-game is up to a decent level 
