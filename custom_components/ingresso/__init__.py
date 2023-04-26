import logging
from typing import Optional, Union

import requests
from homeassistant import config_entries, core
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryAuthFailed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .const import BASE_URL, CONF_CITY_ID, CONF_CITY_NAME, CONF_PARTNERSHIP, DOMAIN

PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
):
    if await get_movies(
        hass=hass,
        city_id=entry.data.get(CONF_CITY_ID),
        partnership=entry.data.get(CONF_PARTNERSHIP),
    ):
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = entry.data

        for platform in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )
    else:
        raise ConfigEntryAuthFailed("Invalid credentials")
    return True


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_migrate_entry(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            CONF_CITY_ID: config_entry.data.get(CONF_CITY_ID),
            CONF_CITY_NAME: config_entry.data.get(CONF_CITY_NAME),
            CONF_PARTNERSHIP: config_entry.data.get(CONF_PARTNERSHIP),
        },
    )

    return True


async def get_movies(
    hass, city_id: int, partnership: str
) -> Union[dict, Optional[None]]:
    def get():
        url = BASE_URL.format(city_id, partnership)
        retry_strategy = Retry(
            total=3,
            status_forcelist=[400, 401, 404, 500, 502, 503, 504],
            method_whitelist=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)

        return http.get(url, headers={"User-Agent": "Mozilla/5.0"})

    response = await hass.async_add_executor_job(get)
    _LOGGER.debug("API Response movies: %s", response.json())

    if response.ok:
        return response.json()
    return None
