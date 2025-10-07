from datetime import datetime, timedelta, timezone
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, CONF_NAME, CONF_LAST_DONE, CONF_NEXT_DUE, CONF_DAYS, CONF_POINTS
from .entity import parse_datetime, calculate_status

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up chore sensors."""
    data = entry.data
    entity = HouseholdChoreSensor(hass, entry.entry_id, data)
    hass.data[DOMAIN].setdefault("entities", {})[entity.entity_id] = entity
    async_add_entities([entity], True)


class HouseholdChoreSensor(Entity):
    def __init__(self, hass, entry_id, data):
        self.hass = hass
        self._entry_id = entry_id
        self._name = data.get(CONF_NAME)
        self._last_done = parse_datetime(data.get(CONF_LAST_DONE))
        self._next_due = parse_datetime(data.get(CONF_NEXT_DUE))
        self._days = data.get(CONF_DAYS, 7)
        self._points = data.get(CONF_POINTS, 1)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._name.lower().replace(' ', '_')}"

    @property
    def state(self):
        return calculate_status(self._next_due)

    @property
    def extra_state_attributes(self):
        return {
            "last_done": self._last_done.isoformat() if self._last_done else None,
            "next_due": self._next_due.isoformat() if self._next_due else None,
            "days": self._days,
            "points": self._points,
        }

    async def async_set_value(self, field, value):
        if field == "last_done":
            self._last_done = parse_datetime(value)
        elif field == "next_due":
            self._next_due = parse_datetime(value)
        elif field == "days":
            self._days = int(value)
        elif field == "points":
            self._points = int(value)
        self.async_write_ha_state()

    async def async_do_chore(self, helper_number=None):
        now = datetime.now(timezone.utc)
        self._last_done = now
        self._next_due = now + timedelta(days=self._days)

        # If helper_number provided, increment it
        if helper_number:
            await self.hass.services.async_call(
                "input_number",
                "set_value",
                {
                    "entity_id": helper_number,
                    "value": float(self.hass.states.get(helper_number).state)
                    + float(self._points),
                },
                blocking=True,
            )

        self.async_write_ha_state()
