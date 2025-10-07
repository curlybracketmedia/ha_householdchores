from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Household Chores from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    hass.data[DOMAIN]["entities"][f"sensor.{chore.unique_id}"] = chore


    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def async_do_chore(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        helper_number = call.data.get("helper_number")

        entity = hass.data[DOMAIN]["entities"].get(entity_id)
        if entity:
            await entity.async_do_chore(helper_number)

    async def async_set_value(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        _, _, field = call.service.partition("set_")
        value = call.data.get("value")

        entity = hass.data[DOMAIN]["entities"].get(entity_id)
        if entity:
            await entity.async_set_value(field, value)

    # Register services at the integration (domain) level
    hass.services.async_register(DOMAIN, "do_chore", async_do_chore)
    for field in ["last_done", "next_due", "days", "points"]:
        hass.services.async_register(DOMAIN, f"set_{field}", async_set_value)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
