from ...const import DOMAIN


class FusionSolarDevice:
    def __init__(self, id: str, name: str, station_code: str, esn_code: str, type_id: str, inverter_type,
                 software_version: str):
        self.device_id = id
        self.name = name
        self.station_code = station_code
        self.esn_code = esn_code
        self.type_id = type_id
        self.inverter_type = inverter_type
        self.software_version = software_version

    @property
    def model(self) -> str:
        if self.type_id == 1:
            return 'String inverter'
        if self.type_id == 10:
            return 'EMI'
        if self.type_id == 17:
            return 'Grid meter'
        if self.type_id == 38:
            return f'Residential inverter {self.inverter_type}'
        if self.type_id == 39:
            return 'Battery'
        if self.type_id == 47:
            return 'Power Sensor'

        return 'Unknown'

    def device_info(self):
        return {
            'identifiers': {
                (DOMAIN, self.device_id)
            },
            'name': self.name,
            'manufacturer': 'Huawei FusionSolar',
            'model': self.model,
            'sw_version': self.software_version,
            'via_device': (DOMAIN, self.station_code)
        }
