import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_LAST_DONE, CONF_NEXT_DUE, CONF_DAYS, CONF_POINTS


class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Household Chores."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Optional(CONF_LAST_DONE): str,
                vol.Optional(CONF_NEXT_DUE): str,
                vol.Optional(CONF_DAYS, default=7): int,
                vol.Optional(CONF_POINTS, default=1): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HouseholdChoresOptionsFlowHandler(config_entry)


class HouseholdChoresOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for an existing chore."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options for the integration."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = {**self.config_entry.data, **self.config_entry.options}

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=data.get(CONF_NAME)): str,
                vol.Optional(CONF_LAST_DONE, default=data.get(CONF_LAST_DONE, "")): str,
                vol.Optional(CONF_NEXT_DUE, default=data.get(CONF_NEXT_DUE, "")): str,
                vol.Optional(CONF_DAYS, default=data.get(CONF_DAYS, 7)): int,
                vol.Optional(CONF_POINTS, default=data.get(CONF_POINTS, 1)): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
