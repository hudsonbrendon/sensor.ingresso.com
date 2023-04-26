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
from homeassistant import config_entries, const, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util.dt import utc_from_timestamp
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .const import (
    BASE_URL,
    CONF_CITY_ID,
    CONF_CITY_NAME,
    CONF_PARTNERSHIP,
    DEFAULT_POSTER,
    DOMAIN,
    ICON,
    SCAN_INTERVAL,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CITY_ID): cv.string,
        vol.Required(CONF_CITY_NAME): cv.string,
        vol.Required(CONF_PARTNERSHIP): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    """Setup sensor platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)
    sensors = [
        IngressoSensor(
            city_id=config[CONF_CITY_ID],
            city_name=config[CONF_CITY_NAME],
            partnership=config[CONF_PARTNERSHIP],
            name=config[CONF_CITY_NAME],
            session=session,
        )
    ]
    async_add_entities(sensors, update_before_add=True)


class IngressoSensor(Entity):
    """Ingresso.com Sensor class"""

    def __init__(
        self,
        city_id: int,
        city_name: str,
        partnership: str,
        name: str,
        session: ClientSession,
    ) -> None:
        self._state = city_name
        self._city_id = city_id
        self._partnership = partnership
        self.session = session
        self._name = name
        self._movies = [
            {
                "title_default": "$title",
                "line1_default": "$rating",
                "line2_default": "$release",
                "line3_default": "$runtime",
                "line4_default": "$studio",
                "icon": "mdi:arrow-down-bold",
            }
        ]
        self._last_updated = const.STATE_UNKNOWN

    @property
    def city_id(self) -> int:
        return self._city_id

    @property
    def partnership(self) -> str:
        return self._partnership

    @property
    def name(self) -> str:
        """Name."""
        return f"{self._partnership.capitalize()} {self._name.capitalize()}"

    @property
    def state(self) -> str:
        """State."""
        return len(self.movies)

    @property
    def last_updated(self):
        """Returns date when it was last updated."""
        if self._last_updated != "unknown":
            stamp = float(self._last_updated)
            return utc_from_timestamp(int(stamp))

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

        retry_strategy = Retry(
            total=3,
            status_forcelist=[400, 401, 500, 502, 503, 504],
            method_whitelist=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)

        movies = http.get(url, headers={"User-Agent": "Mozilla/5.0"})

        if movies.ok:
            self._movies.extend(
                [
                    dict(
                        title=movie.get("title", "Não informado"),
                        poster=movie["images"][0]["url"]
                        if movie["images"]
                        else DEFAULT_POSTER,
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
            _LOGGER.debug("Payload received: %s", movies.json())
        else:
            _LOGGER.debug("Error received: %s", movies.content)
