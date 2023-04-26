from collections.abc import Mapping

import voluptuous as vol
from homeassistant import config_entries

from . import get_movies
from .const import CONF_CITY_ID, CONF_CITY_NAME, CONF_PARTNERSHIP, DOMAIN

DATA_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(CONF_CITY_ID): int,
        vol.Required(CONF_CITY_NAME): str,
        vol.Required(CONF_PARTNERSHIP): str,
    }
)


class IngressoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ingresso config flow."""

    def __init__(self) -> None:
        """Initialize Ingresso config flow."""
        self.city_id: str
        self.city_name: str
        self.partnership: str

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if await get_movies(
                hass=self.hass,
                city_id=user_input.get(CONF_CITY_ID),
                partnership=user_input.get(CONF_PARTNERSHIP),
            ):
                self.city_id = user_input.get(CONF_CITY_ID)
                self.city_name = user_input.get(CONF_CITY_NAME)
                self.partnership = user_input.get(CONF_PARTNERSHIP)

                return self.async_create_entry(
                    title=f"{self.partnership.capitalize()} {self.city_name.capitalize()}",
                    data={
                        CONF_CITY_ID: self.city_id,
                        CONF_CITY_NAME: self.city_name,
                        CONF_PARTNERSHIP: self.partnership,
                    },
                )

            errors[CONF_CITY_ID] = "city_id_error"
            errors[CONF_PARTNERSHIP] = "partnership_error"

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                DATA_SCHEMA,
                user_input,
            ),
            errors=errors,
        )
