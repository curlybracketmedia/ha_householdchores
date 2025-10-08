from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN


class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Household Chores."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Dates are not required — sensor will create them automatically
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "name": user_input["name"],
                    "days": user_input["days"],
                    "points": user_input["points"],
                    "last_done": None,
                    "next_due": None,
                },
            )

        # Voluptuous schema with readable labels
        schema = vol.Schema(
            {
                vol.Required("name", description={"name": "Name"}): str,
                vol.Required("days", description={"name": "Days"}): int,
                vol.Required("points", description={"name": "Points"}): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
