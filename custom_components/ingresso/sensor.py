"""
A platform that provides information about movies in city.

For more details on this component, refer to the documentation at
https://github.com/hudsonbrendon/sensor.ingresso.com
"""
import logging

import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import Entity

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

ICON = "mdi:video"

BASE_URL = "https://www.udemy.com/api-2.0/{}/?"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor platform."""
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    session = async_create_clientsession(hass)
    name = partnership.capitalize()
    async_add_entities(
        [UdemySensor(client_id, client_secret, name, session)], True
    )


class UdemySensor(Entity):
    """Udemy.com Sensor class"""

    def __init__(self, client_id, client_secret, name, session):
        self._state = name
        self._client_id = client_id 
        self._client_secret = client_secret
        self.session = session
        self._name = name
        self._last_free_course = None
        self._courses = []

    async def async_update(self):
        """Update sensor."""
        _LOGGER.debug("%s - Running update", self._name)
        try:
            async with async_timeout.timeout(10, loop=self.hass.loop):
                response = await self.session.get(BASE_URL)
                info = await response.json()

                self._course

        except Exception as error:
            _LOGGER.debug("%s - Could not update - %s", self._name, error)

    @property
    def name(self):
        """Name."""
        return self._name

    @property
    def state(self):
        """State."""
        return self._state

    @property
    def movies(self):
        """Movies."""
        return self._movies

    @property
    def icon(self):
        """Icon."""
        return ICON

    @property
    def device_state_attributes(self):
        """Attributes."""
        return {
            "name": self.name,
            "movies": self.movies,
        }
