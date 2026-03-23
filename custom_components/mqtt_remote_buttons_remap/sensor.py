from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DEVICE_ID, CONF_HWID, CONF_SOURCE_MAP, DOMAIN, entry_runtime_signal


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities(
        [
            MqttRemoteButtonsRemapSensor(hass, entry),
            MqttRemoteButtonsRemapLastChatSensor(hass, entry),
            MqttRemoteButtonsRemapLastBatteryAlertSensor(hass, entry),
        ]
    )


def _device_info_for_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_registry = dr.async_get(hass)
    mqtt_device = device_registry.devices.get(entry.data.get(CONF_DEVICE_ID))
    if mqtt_device is not None and mqtt_device.identifiers:
        return {
            "identifiers": mqtt_device.identifiers,
        }

    return {
        "identifiers": {(DOMAIN, entry.data[CONF_HWID])},
        "name": entry.title,
    }


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
        self._attr_device_info = _device_info_for_entry(hass, entry)


class MqttRemoteButtonsRemapLastChatSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Last Chat Message"
    _attr_icon = "mdi:message-text-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_HWID]}_last_chat_message"
        self._attr_device_info = _device_info_for_entry(hass, entry)
        self._apply_runtime_state()

    def _apply_runtime_state(self) -> None:
        runtime = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {})
        self._attr_native_value = runtime.get("last_chat_message", "")
        self._attr_extra_state_attributes = {
            "device_id": self._entry.data.get(CONF_DEVICE_ID),
            "hwid": self._entry.data.get(CONF_HWID),
            "topic": runtime.get("last_chat_topic", ""),
            "received_at": runtime.get("last_chat_received_at"),
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, entry_runtime_signal(self._entry.entry_id), self._handle_runtime_update)
        )

    def _handle_runtime_update(self) -> None:
        self._apply_runtime_state()
        self.async_write_ha_state()


class MqttRemoteButtonsRemapLastBatteryAlertSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Last Battery Alert"
    _attr_icon = "mdi:battery-alert-variant-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_HWID]}_last_battery_alert"
        self._attr_device_info = _device_info_for_entry(hass, entry)
        self._apply_runtime_state()

    def _apply_runtime_state(self) -> None:
        runtime = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {})
        self._attr_native_value = runtime.get("last_battery_alert", "")
        self._attr_extra_state_attributes = {
            "device_id": self._entry.data.get(CONF_DEVICE_ID),
            "hwid": self._entry.data.get(CONF_HWID),
            "alert_type": runtime.get("last_battery_alert_type", ""),
            "battery_percent": runtime.get("battery_percent"),
            "battery_voltage": runtime.get("battery_voltage"),
            "battery_charging": runtime.get("battery_charging"),
            "received_at": runtime.get("last_battery_alert_received_at"),
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, entry_runtime_signal(self._entry.entry_id), self._handle_runtime_update)
        )

    def _handle_runtime_update(self) -> None:
        self._apply_runtime_state()
        self.async_write_ha_state()