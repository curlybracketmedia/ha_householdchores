from datetime import datetime, timedelta
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_platform

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Household Chores from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    platform = entity_platform.async_get_current_platform()

    async def async_do_chore(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        helper_number = call.data.get("helper_number")

        entity = hass.data[DOMAIN]["entities"].get(entity_id)
        if entity:
            await entity.async_do_chore(helper_number)

    async def async_set_value(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        field = call.service.split("_", 1)[1]  # e.g. "set_last_done" → "last_done"
        value = call.data.get("value")

        entity = hass.data[DOMAIN]["entities"].get(entity_id)
        if entity:
            await entity.async_set_value(field, value)

    # Register services
    hass.services.async_register(DOMAIN, "do_chore", async_do_chore)
    for field in ["last_done", "next_due", "days", "points"]:
        hass.services.async_register(DOMAIN, f"set_{field}", async_set_value)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Household Chores config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
