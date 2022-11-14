from ...const import DOMAIN


class FusionSolarStation:
    def __init__(
            self,
            code: str,
            name: str,
            address: str = None,
            capacity: float = None,
            build_state: str = None,
            combine_type: str = None,
            aid_type: int = None,
            contact_person: str = None,
            contact_phone: str = None
    ):
        self.code = code
        self.name = name
        self.address = address
        self.capacity = capacity
        self.build_state = build_state
        self.combine_type = combine_type
        self.aid_type = aid_type
        self.contact_person = contact_person
        self.contact_phone = contact_phone

    def device_info(self):
        return {
            'identifiers': {
                (DOMAIN, self.code)
            },
            'name': self.name,
            'manufacturer': 'Huawei FusionSolar',
            'model': 'Station'
        }

    @property
    def readable_name(self):
        if self.name is not None and self.name != '':
            return self.name

        return self.code