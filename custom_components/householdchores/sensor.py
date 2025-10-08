from datetime import datetime, timedelta, timezone
import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .entity import calculate_status

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Household Chores sensors from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("entities", {})

    chore = HouseholdChoreSensor(hass, entry.data)
    async_add_entities([chore])

    # Store using HA entity_id key so service lookups work
    hass.data[DOMAIN]["entities"][chore.entity_id] = chore


class HouseholdChoreSensor(Entity):
    """Representation of a single household chore as a sensor."""

    def __init__(self, hass, data):
        self.hass = hass
        self._data = dict(data)  # make mutable copy
        self._attr_name = data.get("name", "Unnamed Chore")
        self._attr_unique_id = self._attr_name.lower().replace(" ", "_")
        self.entity_id = f"sensor.{self._attr_unique_id}"

        days = self._data.get("days", 7)
        self._data.setdefault("days", days)
        self._data.setdefault("points", self._data.get("points", 1))
        self._data.setdefault("last_done", None)
        self._data.setdefault("last_done_by", None)

        if self._data.get("next_due") is None:
            next_due = datetime.now(timezone.utc) + timedelta(days=days)
            self._data["next_due"] = next_due.isoformat()

        self._data["status"] = self.calculate_status(self._data["next_due"])

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        return self._data.get("status", "Not Due")

    @property
    def extra_state_attributes(self):
        return {
            "last_done_by": self._data.get("last_done_by"),
            "last_done": self._data.get("last_done"),
            "next_due": self._data.get("next_due"),
            "days": self._data.get("days"),
            "points": self._data.get("points"),
        }

    async def async_do_chore(self, helper_number=None, last_done_by=None):
        now = datetime.now(timezone.utc)
        days = self._data.get("days", 7)
        points = self._data.get("points", 1)

        self._data["last_done"] = now.isoformat()
        self._data["next_due"] = (now + timedelta(days=days)).isoformat()
        self._data["status"] = self.calculate_status(self._data["next_due"])

        if last_done_by:
            self._data["last_done_by"] = last_done_by

        if helper_number:
            current_state = self.hass.states.get(helper_number)
            current_value = float(current_state.state) if current_state else 0
            new_value = current_value + points
            await self.hass.services.async_call(
                "input_number",
                "set_value",
                {"entity_id": helper_number, "value": new_value},
                blocking=True,
            )

        self.async_write_ha_state()

    async def async_set_value(self, field, value):
        """Update a single field on the chore."""
        if field in ["last_done", "next_due"] and isinstance(value, str):
            try:
                datetime.fromisoformat(value)
                self._data[field] = value
            except Exception:
                _LOGGER.warning("Invalid date format for %s: %s", field, value)
        else:
            self._data[field] = value

        if field in ["last_done", "next_due"]:
            self._data["status"] = self.calculate_status(self._data.get("next_due"))

        self.async_write_ha_state()

