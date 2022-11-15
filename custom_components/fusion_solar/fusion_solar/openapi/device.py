from ...const import DOMAIN


class FusionSolarDevice:
    def __init__(
            self,
            device_id: str,
            name: str,
            station_code: str,
            esn_code: str,
            type_id: str,
            inverter_type,
            software_version: str,
            longitude: float,
            latitude: float
    ):
        self.device_id = device_id
        self.name = name
        self.station_code = station_code
        self.esn_code = esn_code
        self.type_id = type_id
        self.inverter_type = inverter_type
        self.software_version = software_version
        self.longitude = longitude
        self.latitude = latitude

    @property
    def model(self) -> str:
        if self.type_id == 38:
            return f'{self.device_type} {self.inverter_type}'

        return self.device_type

    @property
    def device_type(self) -> str:
        if self.type_id == 1:
            return 'String inverter'
        if self.type_id == 2:
            return 'SmartLogger'
        if self.type_id == 8:
            return 'Transformer'
        if self.type_id == 10:
            return 'EMI'
        if self.type_id == 13:
            return 'Protocol converter'
        if self.type_id == 16:
            return 'General device'
        if self.type_id == 17:
            return 'Grid meter'
        if self.type_id == 22:
            return 'PID'
        if self.type_id == 37:
            return 'Pinnet data logger'
        if self.type_id == 38:
            return 'Residential inverter'
        if self.type_id == 39:
            return 'Battery'
        if self.type_id == 40:
            return 'Backup box'
        if self.type_id == 45:
            return 'PLC'
        if self.type_id == 46:
            return 'Optimizer'
        if self.type_id == 47:
            return 'Power Sensor'
        if self.type_id == 62:
            return 'Dongle'
        if self.type_id == 63:
            return 'Distributed SmartLogger'
        if self.type_id == 70:
            return 'Safety box'

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

    @property
    def readable_name(self):
        if self.name == self.esn_code:
            return self.name

        if self.esn_code is not None and self.esn_code != '':
            return f'{self.name} ({self.esn_code})'

        return self.name
