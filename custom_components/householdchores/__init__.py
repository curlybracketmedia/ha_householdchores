from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Household Chores from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def async_do_chore(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        helper_number = call.data.get("helper_number")

        entity = hass.data[DOMAIN].get("entities", {}).get(entity_id)
        if entity:
            await entity.async_do_chore(helper_number)

    async def async_set_value(call: ServiceCall):
        entity_id = call.data.get("entity_id")
        # service name is e.g. “householdchores.set_last_done”
        # so call.service is “householdchores.set_last_done”
        # we split off “set_...” part
        _, _, field = call.service.partition("set_")
        value = call.data.get("value")

        entity = hass.data[DOMAIN].get("entities", {}).get(entity_id)
        if entity:
            await
