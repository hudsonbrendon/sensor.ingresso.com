"""
A platform that provides information about movies in city.

For more details on this component, refer to the documentation at
https://github.com/hudsonbrendon/sensor.ingresso.com
"""
import logging
from typing import List

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from aiohttp import ClientSession
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import Entity
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .const import (
    BASE_URL,
    CONF_CITY_ID,
    CONF_CITY_NAME,
    CONF_PARTNERSHIP,
    DEFAULT_POSTER,
    ICON,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CITY_ID): cv.string,
        vol.Required(CONF_CITY_NAME): cv.string,
        vol.Required(CONF_PARTNERSHIP): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None) -> None:
    """Setup sensor platform."""
    city_id = config["city_id"]
    city_name = config["city_name"]
    partnership = config["partnership"]
    session = async_create_clientsession(hass)
    name = partnership.capitalize()
    async_add_entities([IngressoSensor(city_id, city_name, partnership, name, session)], True)


class IngressoSensor(Entity):
    """Ingresso.com Sensor class"""

    def __init__(self, city_id: int, city_name: str, partnership: str, name: str, session: ClientSession) -> None:
        self._state = city_name
        self._city_id = city_id
        self._partnership = partnership
        self.session = session
        self._name = name
        self._movies = []

    @property
    def city_id(self) -> int:
        return self._city_id

    @property
    def partnership(self) -> str:
        return self._partnership

    @property
    def name(self) -> str:
        """Name."""
        return self._name

    @property
    def state(self) -> str:
        """State."""
        return len(self.movies)

    @property
    def movies(self) -> List[dict]:
        """Movies."""
        return self._movies

    @property
    def icon(self) -> str:
        """Icon."""
        return ICON

    @property
    def extra_state_attributes(self) -> dict:
        """Attributes."""
        return {
            "data": self.movies,
        }

    def update(self) -> None:
        """Update sensor."""
        _LOGGER.debug("%s - Running update", self.name)
        url = BASE_URL.format(self.city_id, self.partnership)

        retry_strategy = Retry(total=3, status_forcelist=[400, 401, 404, 500, 502, 503, 504], method_whitelist=["GET"])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)

        movies = http.get(url)

        if movies.ok:
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
            self._movies.extend(
                [
                    dict(
                        title=movie.get("title", "Não informado"),
                        poster=movie["images"][0]["url"] if movie["images"] else DEFAULT_POSTER,
                        synopsis=movie.get("synopsis", "Não informado"),
                        director=movie.get("director", "Não informado"),
                        cast=movie.get("cast", "Não informado"),
                        studio=movie.get("distributor", "Não informado"),
                        genres=movie.get("genres", "Não informado"),
                        runtime=movie.get("duration", "Não informado"),
                        rating=movie.get("contentRating", "Não informado"),
                        release="$date",
                        airdate=movie["premiereDate"]["localDate"].split("T")[0],
                        city=movie.get("city", "Não informado"),
                        ticket=movie.get("siteURL", "Não informado"),
                    )
                    for movie in movies.json()
                ]
            )
            _LOGGER.debug("%s - Success", movies.json())
        else:
            _LOGGER.debug("%s - Error", movies.json())
