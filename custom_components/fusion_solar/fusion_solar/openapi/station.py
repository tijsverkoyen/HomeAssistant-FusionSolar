from ...const import DOMAIN


class FusionSolarStation:
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    def device_info(self):
        return {
            'identifiers': {
                (DOMAIN, self.code)
            },
            'name': self.name,
            'manufacturer': 'Huawei FusionSolar',
            'model': 'Station'
        }
