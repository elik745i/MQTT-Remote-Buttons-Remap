from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DEVICE_ID, CONF_HWID, CONF_SOURCE_MAP, DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([MqttRemoteButtonsRemapSensor(hass, entry)])


class MqttRemoteButtonsRemapSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Mappings"
    _attr_icon = "mdi:swap-horizontal"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_HWID]}_mappings"

        mapping_values = entry.data.get(CONF_SOURCE_MAP, {}).values()
        self._attr_native_value = sum(1 for value in mapping_values if value)
        self._attr_extra_state_attributes = {
            "device_id": entry.data.get(CONF_DEVICE_ID),
            "hwid": entry.data.get(CONF_HWID),
        }

        device_registry = dr.async_get(hass)
        mqtt_device = device_registry.devices.get(entry.data.get(CONF_DEVICE_ID))
        if mqtt_device is not None and mqtt_device.identifiers:
            self._attr_device_info = {
                "identifiers": mqtt_device.identifiers,
            }
        else:
            self._attr_device_info = {
                "identifiers": {(DOMAIN, entry.data[CONF_HWID])},
                "name": entry.title,
            }