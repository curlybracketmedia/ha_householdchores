from datetime import datetime, timedelta, timezone
import logging

from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Household Chores sensors from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("entities", {})

    chore = HouseholdChoreSensor(hass, entry)
    # Use unique_id for lookup
    hass.data[DOMAIN]["entities"][chore.unique_id] = chore

    async_add_entities([chore])


class HouseholdChoreSensor(Entity):
    """Representation of a single chore as a sensor."""

    def __init__(self, hass, entry):
        """Initialize the chore."""
        self.hass = hass
        self.entry = entry  # keep reference for persistence
        self._data = dict(entry.data)
        self._attr_name = self._data.get("name", "Unnamed Chore")
        self._attr_unique_id = self._attr_name.lower().replace(" ", "_")

        # Set defaults if missing
        days = self._data.get("days", 7)
        self._data.setdefault("days", days)
        self._data.setdefault("points", self._data.get("points", 1))
        self._data.setdefault("last_done", None)

        if self._data.get("next_due") is None:
            next_due = datetime.now(timezone.utc) + timedelta(days=days)
            self._data["next_due"] = next_due.isoformat()

        # Set initial status
        self._data["status"] = self.calculate_status(self._data["next_due"])

    #
    # ────────────────────────────── PROPERTIES ──────────────────────────────
    #

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

    #
    # ────────────────────────────── CORE ACTIONS ──────────────────────────────
    #

    async def async_do_chore(self, helper_number=None):
        """Mark the chore as done, update due dates, and award points."""
        now = datetime.now(timezone.utc)
        days = self._data.get("days", 7)
        points = self._data.get("points", 1)

        self._data["last_done"] = now.isoformat()
        self._data["next_due"] = (now + timedelta(days=days)).isoformat()
        self._data["status"] = self.calculate_status(self._data["next_due"])

        self.async_write_ha_state()
        await self._save_to_entry()

        # Increment helper number if provided
        if helper_number:
            try:
                current_state = self.hass.states.get(helper_number)
                current_value = float(current_state.state) if current_state else 0
                new_value = current_value + points
                self.hass.async_create_task(
                    self.hass.services.async_call(
                        "input_number",
                        "set_value",
                        {"entity_id": helper_number, "value": new_value},
                        blocking=True,
                    )
                )
            except Exception as e:
                _LOGGER.error("Failed to update helper number %s: %s", helper_number, e)

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
        await self._save_to_entry()

    #
    # ────────────────────────────── HELPERS ──────────────────────────────
    #

    async def _save_to_entry(self):
        """Persist updated data to the config entry for restart survival."""
        try:
            self.hass.config_entries.async_update_entry(self.entry, data=self._data)
            _LOGGER.debug("Persisted chore '%s' data to config entry", self._attr_name)
        except Exception as e:
            _LOGGER.error("Failed to persist chore '%s': %s", self._attr_name, e)

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
