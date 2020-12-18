# Home Assisant FusionSolar Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Integrate FusionSolar into you Home Assistant.

## Known issues

### Detected I/O inside the event loop

    2020-12-15 19:30:34 WARNING (MainThread) [homeassistant.util.async_] Detected I/O inside the event loop. This is causing stability issues. Please report issue to the custom component author for fusion_solar_kiosk doing I/O at custom_components/fusion_solar_kiosk/sensor.py, line 116: response = post(url, headers=headers, data=json.dumps(data))

Something like above will be shown in the logs. I am aware of this. I will look 
into this when my python-game is up to a decent level 
