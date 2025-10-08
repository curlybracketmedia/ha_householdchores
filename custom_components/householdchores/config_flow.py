from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN


class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Household Chores."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Dates are intentionally omitted — will be set automatically in sensor
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

        schema = vol.Schema(
            {
                vol.Required("name", description={"suggested_value": "New Chore"}): str,
                vol.Required("days", description={"suggested_value": 7}): int,
                vol.Required("points", description={"suggested_value": 1}): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "name": "Chore name or title",
                "days": "Number of days until next due",
                "points": "Points awarded when completed",
            },
        )
