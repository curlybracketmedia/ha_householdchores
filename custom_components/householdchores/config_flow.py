import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN


class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Household Chores."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        schema = vol.Schema({
            vol.Required("name", description={"name": "Name"}): str,
            vol.Required("days", default=7, description={"name": "Days"}): int,
            vol.Required("points", default=1, description={"name": "Points"}): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
