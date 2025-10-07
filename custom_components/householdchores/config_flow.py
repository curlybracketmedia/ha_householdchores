import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_LAST_DONE,
    CONF_NEXT_DUE,
    CONF_DAYS,
    CONF_POINTS,
)


class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Household Chores integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Initial step when user adds a chore via the UI."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Form schema
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Optional(CONF_LAST_DONE, default=""): str,
                vol.Optional(CONF_NEXT_DUE, default=""): str,
                vol.Optional(CONF_DAYS, default=7): int,
                vol.Optional(CONF_POINTS, default=1): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow handler for this chore."""
        return HouseholdChoresOptionsFlow(config_entry)


class HouseholdChoresOptionsFlow(config_entries.OptionsFlow):
    """Handle editing options for an existing chore."""

    def __init__(self, config_entry):
        """Store entry ID for lookup."""
        self._entry_id = config_entry.entry_id

    async def async_step_init(self, user_input=None):
        """Show or handle the options form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Lookup entry in HA
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        data = {}
        if entry:
            data.update(entry.data)
            data.update(entry.options)

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=data.get(CONF_NAME, "")): str,
                vol.Optional(CONF_LAST_DONE, default=data.get(CONF_LAST_DONE, "")): str,
                vol.Optional(CONF_NEXT_DUE, default=data.get(CONF_NEXT_DUE, "")): str,
                vol.Optional(CONF_DAYS, default=data.get(CONF_DAYS, 7)): int,
                vol.Optional(CONF_POINTS, default=data.get(CONF_POINTS, 1)): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
