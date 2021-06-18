"""
A platform that provides information about movies in city.

For more details on this component, refer to the documentation at
https://github.com/hudsonbrendon/sensor.ingresso.com
"""
import logging
from datetime import timedelta

import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import Entity

CONF_CITY_ID = "city_id"
CONF_CITY_NAME = "city_name"
CONF_PARTNERSHIP = "partnership"
CONF_SCAN_INTERVAL = "scan_interval" or timedelta(minutes=2)
SCAN_INTERVAL = timedelta(minutes=120)


ICON = "mdi:ticket"

BASE_URL = "https://api-content.ingresso.com/v0/templates/nowplaying/{}?partnership={}"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CITY_ID): cv.string,
        vol.Required(CONF_CITY_NAME): cv.string,
        vol.Required(CONF_PARTNERSHIP): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor platform."""
    city_id = config["city_id"]
    city_name = config["city_name"]
    partnership = config["partnership"]
    session = async_create_clientsession(hass)
    name = partnership.capitalize()
    async_add_entities(
        [IngressoSensor(city_id, city_name, partnership, name, session)], True
    )


class IngressoSensor(Entity):
    """Ingresso.com Sensor class"""

    def __init__(self, city_id, city_name, partnership, name, session):
        self._state = city_name
        self._city_id = city_id
        self._partnership = partnership
        self.session = session
        self._name = name
        self._movies = []

    async def async_update(self):
        """Update sensor."""
        _LOGGER.debug("%s - Running update", self._name)
        try:
            url = BASE_URL.format(self._city_id, self._partnership)
            async with async_timeout.timeout(10, loop=self.hass.loop):
                response = await self.session.get(url)
                movies = await response.json()

                self._movies.append(
                    {
                        "title_default": "$title",
                        "line1_default": "$rating",
                        "line2_default": "$release",
                        "line3_default": "$runtime",
                        "line4_default": "$studio",
                        "icon": "mdi:arrow-down-bold",
                    }
                )

                for movie in movies:
                    self._movies.append(
                        dict(
                            title=movie["title"],
                            poster=movie["images"][0]["url"],
                            synopsis=movie["synopsis"],
                            director=movie["director"],
                            cast=movie["cast"],
                            studio=movie["distributor"],
                            genres=movie["genres"],
                            runtime=movie["duration"],
                            rating=movie["contentRating"],
                            release="$date",
                            airdate=movie["premiereDate"]["localDate"].split("T")[0],
                            city=movie["city"],
                            ticket=movie["siteURL"],
                        )
                    )

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
        return [i for n, i in enumerate(self._movies) if i not in self._movies[n + 1 :]]

    @property
    def icon(self):
        """Icon."""
        return ICON

    @property
    def device_state_attributes(self):
        """Attributes."""
        return {
            "data": self.movies,
        }
