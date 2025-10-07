from datetime import datetime, timedelta, timezone
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Household Chores sensors from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("entities", {})

    chore = HouseholdChoreSensor(hass, entry.data)
    hass.data[DOMAIN]["entities"][chore.unique_id] = chore

    async_add_entities([chore])


class HouseholdChoreSensor(Entity):
    """Representation of a single chore as a sensor."""

    def __init__(self, hass, data):
        """Initialize the chore."""
        self.hass = hass
        self._data = data
        self._attr_name = data.get("name", "Unnamed Chore")
        self._attr_unique_id = self._attr_name.lower().replace(" ", "_")
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        """Return status as the main state."""
        return self._data.get("status", "Not Due")

    @property
    def extra_state_attributes(self):
        """Return chore attributes."""
        return {
            "last_done": self._data.get("last_done"),
            "next_due": self._data.get("next_due"),
            "days": self._data.get("days"),
            "points": self._data.get("points"),
        }

    async def async_do_chore(self, helper_number=None):
        """Mark the chore as done and update dates."""
        now = datetime.now(timezone.utc)
        self._data["last_done"] = now.isoformat()

        days = self._data.get("days", 7)
        next_due = now + timedelta(days=days)
        self._data["next_due"] = next_due.isoformat()

        self._data["status"] = self.calculate_status(self._data["next_due"])

        # Increment helper number if provided
        if helper_number:
            current_value = float(
                self.hass.states.get(helper_number).state or 0
            )
            new_value = current_value + self._data.get("points", 0)
            await self.hass.services.async_call(
                "input_number",
                "set_value",
                {"entity_id": helper_number, "value": new_value},
            )

        self.async_write_ha_state()

    async def async_set_value(self, field, value):
        """Update a single field on the chore."""
        self._data[field] = value
        if field in ["last_done", "next_due"]:
            self._data["status"] = self.calculate_status(self._data.get("next_due"))
        self.async_write_ha_state()

    def calculate_status(self, next_due_str):
        """Determine the chore status based on next due datetime."""
        if not next_due_str:
            return "Do Not Do"
        now = datetime.now(timezone.utc)
        try:
            next_due = datetime.fromisoformat(next_due_str)
        except Exception:
            return "Do Not Do"

        delta = (next_due - now).total_seconds()

        if delta < -172800:
            return "Overdue"
        elif delta < 0:
            return "Due"
        elif delta < 86400:
            return "Due Soon"
        else:
            return "Not Due"
