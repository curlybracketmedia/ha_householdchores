from datetime import datetime, timedelta, timezone

class HouseholdChoreSensor:
    """Represents a chore entity."""

    def __init__(self, hass, data):
        self.hass = hass
        self._data = data  # dict containing last_done, next_due, days, points
        self._attr_name = data.get("name", "Unnamed Chore")
        self._attr_unique_id = data.get("name", "chore").lower().replace(" ", "_")
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "last_done": self._data.get("last_done"),
            "next_due": self._data.get("next_due"),
            "days": self._data.get("days"),
            "points": self._data.get("points"),
            "status": self._data.get("status"),
        }

    async def async_do_chore(self, helper_number=None):
        """Mark chore as done."""
        now = datetime.now(timezone.utc)
        self._data["last_done"] = now.isoformat()

        days = self._data.get("days", 7)
        self._data["next_due"] = (now + timedelta(days=days)).isoformat()

        # Recalculate status
        self._data["status"] = self.calculate_status(self._data["next_due"])

        # Increment helper number if provided
        if helper_number:
            current = await self.hass.helpers.entity_registry.async_get(helper_number)
            # Or just assume it's an input_number
            self.hass.services.call("input_number", "set_value", {
                "entity_id": helper_number,
                "value": current.state + self._data.get("points", 0)
            })

        # This tells Home Assistant to refresh the entity in the UI
        self.async_write_ha_state()

    async def async_set_value(self, field, value):
        """Update a single field."""
        self._data[field] = value
        if field in ["last_done", "next_due"]:
            self._data["status"] = self.calculate_status(self._data.get("next_due"))
        self.async_write_ha_state()

    def calculate_status(self, next_due_str):
        """Recalculate status based on next due date."""
        if not next_due_str:
            return "Do Not Do"
        now = datetime.now(timezone.utc)
        next_due = datetime.fromisoformat(next_due_str)
        delta = (next_due - now).total_seconds()
        if delta < -172800:
            return "Overdue"
        elif delta < 0:
            return "Due"
        elif delta < 43200:
            return "Due Soon"
        else:
            return "Not Due"

    @callback
    def async_write_ha_state(self):
        """Notify HA that the entity state changed."""
        # This needs to hook into the actual HA Entity object in sensor.py
        # If using EntityComponent, call self.entity.async_write_ha_state()
        pass
