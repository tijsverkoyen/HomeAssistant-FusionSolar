import re
import logging

from urllib.parse import urlparse

_LOGGER = logging.getLogger(__name__)


class FusionSolarKiosk:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self._parseId()

    def _parseId(self):
        id = re.search("\?kk=(.*)", self.url).group(1)
        _LOGGER.debug('calculated KioskId: ' + id)
        self.id = id

    def apiUrl(self):
        url = urlparse(self.url)
        apiUrl = (url.scheme + "://" + url.netloc)
        _LOGGER.debug('calculated API base url for ' + self.id + ': ' + apiUrl)
        return apiUrl
