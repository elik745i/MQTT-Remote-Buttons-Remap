from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util

from .const import (
    ACTION_MODE_STATE,
    BATTERY_FULL_PERCENT,
    BATTERY_FULL_RESET_PERCENT,
    BATTERY_LOW_PERCENT,
    CONF_ACTION_MAP,
    CONF_DEVICE_ID,
    CONF_HWID,
    CONF_SOURCE_MAP,
    CONF_TOPIC,
    DOMAIN,
    EVENT_BATTERY_ALERT,
    EVENT_BUTTON_ACTION,
    EVENT_CHAT_MESSAGE,
    entry_runtime_signal,
)
from .helpers import control_index_from_unique_id, list_remote_sources

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    return True


def _chat_topic_for_entry(entry: ConfigEntry) -> str:
    return f"esp32/remote/{entry.data[CONF_HWID]}/chat/ha/received"


def _state_topic_for_entry(entry: ConfigEntry) -> str:
    return f"esp32/remote/{entry.data[CONF_HWID]}/state"


def _control_command_topic(entry: ConfigEntry, control_index: int) -> str:
    return f"esp32/remote/{entry.data[CONF_HWID]}/control/{control_index}/set"


def _entry_runtime(hass: HomeAssistant, entry_id: str) -> dict[str, Any]:
    return hass.data.setdefault(DOMAIN, {}).setdefault(
        entry_id,
        {
            "unsubscribers": [],
            "state_sync_targets": {},
            "pending_target_states": {},
            "last_chat_message": "",
            "last_chat_topic": "",
            "last_chat_received_at": None,
            "last_battery_alert": "",
            "last_battery_alert_type": "",
            "last_battery_alert_received_at": None,
            "battery_percent": None,
            "battery_voltage": None,
            "battery_charging": None,
            "battery_low_active": False,
            "battery_full_active": False,
        },
    )


def _state_sync_targets_for_entry(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, list[dict[str, Any]]]:
    device_id = entry.data.get(CONF_DEVICE_ID)
    if not device_id:
        return {}

    source_map = entry.data.get(CONF_SOURCE_MAP, {})
    sync_targets: dict[str, list[dict[str, Any]]] = {}
    for source in list_remote_sources(hass, device_id):
        if source.mode != ACTION_MODE_STATE:
            continue

        target_entity_id = source_map.get(source.entity_id, "")
        if not target_entity_id:
            continue

        control_index = control_index_from_unique_id(source.unique_id)
        if control_index is None:
            continue

        sync_targets.setdefault(target_entity_id, []).append(
            {
                "control_topic": _control_command_topic(entry, control_index),
                "source_entity_id": source.entity_id,
                "source_name": source.name,
            }
        )

    return sync_targets


async def _async_publish_control_state(
    hass: HomeAssistant,
    entry: ConfigEntry,
    target_entity_id: str,
    control_topic: str,
    state: str,
) -> None:
    payload = "ON" if state == STATE_ON else "OFF"
    mqtt.async_publish(hass, control_topic, payload, qos=0, retain=False)
    _LOGGER.debug(
        "Published state sync for '%s' target '%s' to '%s' payload '%s'",
        entry.title,
        target_entity_id,
        control_topic,
        payload,
    )


async def _async_create_chat_notification(
    hass: HomeAssistant,
    entry: ConfigEntry,
    message: str,
    received_at: str,
) -> None:
    await hass.services.async_call(
        "persistent_notification",
        "create",
        {
            "notification_id": f"{DOMAIN}_{entry.entry_id}_chat",
            "title": f"{entry.title} message",
            "message": f"Received at {received_at}\n\n{message}",
        },
        blocking=False,
    )


def _battery_alert_message(alert_type: str, percent: int | None, voltage: float | None) -> str:
    details: list[str] = []
    if percent is not None:
        details.append(f"{percent}%")
    if voltage is not None:
        details.append(f"{voltage:.2f}V")
    suffix = f" ({', '.join(details)})" if details else ""
    if alert_type == "low":
        return f"Battery low{suffix}"
    return f"Battery fully charged{suffix}"


async def _async_emit_battery_alert(
    hass: HomeAssistant,
    entry: ConfigEntry,
    runtime: dict[str, Any],
    topic: str,
    alert_type: str,
    percent: int | None,
    voltage: float | None,
    charging: bool | None,
    received_at: str,
) -> None:
    message = _battery_alert_message(alert_type, percent, voltage)
    hass.bus.async_fire(
        EVENT_BATTERY_ALERT,
        {
            "entry_id": entry.entry_id,
            "name": entry.title,
            "hwid": entry.data.get(CONF_HWID),
            "topic": topic,
            "alert_type": alert_type,
            "message": message,
            "battery_percent": percent,
            "battery_voltage": voltage,
            "battery_charging": charging,
            "received_at": received_at,
        },
    )
    runtime["last_battery_alert"] = message
    runtime["last_battery_alert_type"] = alert_type
    runtime["last_battery_alert_received_at"] = received_at


async def _async_process_state_message(hass: HomeAssistant, entry: ConfigEntry, topic: str, payload: str) -> None:
    try:
        state = json.loads(payload)
    except json.JSONDecodeError:
        _LOGGER.debug("Ignoring non-JSON state payload for '%s': %s", entry.title, payload)
        return

    if not isinstance(state, dict):
        return

    runtime = _entry_runtime(hass, entry.entry_id)
    received_at = dt_util.utcnow().isoformat()

    percent_value = state.get("battery_percent")
    voltage_value = state.get("battery_voltage")
    charging_value = state.get("battery_charging")

    percent = int(percent_value) if isinstance(percent_value, (int, float)) else None
    voltage = float(voltage_value) if isinstance(voltage_value, (int, float)) else None
    charging = charging_value if isinstance(charging_value, bool) else None

    runtime["battery_percent"] = percent
    runtime["battery_voltage"] = voltage
    runtime["battery_charging"] = charging

    low_condition = percent is not None and percent <= BATTERY_LOW_PERCENT and charging is False
    full_condition = percent is not None and percent >= BATTERY_FULL_PERCENT and charging in (True, False)

    if low_condition and not runtime.get("battery_low_active", False):
        await _async_emit_battery_alert(hass, entry, runtime, topic, "low", percent, voltage, charging, received_at)
        runtime["battery_low_active"] = True
    elif not low_condition:
        runtime["battery_low_active"] = False

    if full_condition and not runtime.get("battery_full_active", False):
        await _async_emit_battery_alert(hass, entry, runtime, topic, "full", percent, voltage, charging, received_at)
        runtime["battery_full_active"] = True
    elif percent is None or percent <= BATTERY_FULL_RESET_PERCENT:
        runtime["battery_full_active"] = False

    async_dispatcher_send(hass, entry_runtime_signal(entry.entry_id))


async def _async_process_message(hass: HomeAssistant, entry: ConfigEntry, topic: str, payload: str) -> None:
    action = payload.strip()
    if not action:
        return

    event_data = {
        "entry_id": entry.entry_id,
        "name": entry.title,
        "hwid": entry.data.get(CONF_HWID),
        "topic": topic,
        "action": action,
        "payload": payload,
    }
    hass.bus.async_fire(EVENT_BUTTON_ACTION, event_data)

    action_map = entry.data.get(CONF_ACTION_MAP, {})
    mapping = action_map.get(action)
    if not mapping:
        _LOGGER.debug("No mapping for entry '%s' action '%s'", entry.title, action)
        return

    service_ref = mapping.get("service", "")
    target_entity_id = mapping.get("target_entity_id")
    if not service_ref or not target_entity_id or "." not in service_ref:
        _LOGGER.warning("Skipping invalid mapping for entry '%s' action '%s'", entry.title, action)
        return

    if mapping.get("mode") == ACTION_MODE_STATE and mapping.get("state") in {STATE_ON, STATE_OFF}:
        runtime = _entry_runtime(hass, entry.entry_id)
        runtime.setdefault("pending_target_states", {})[target_entity_id] = mapping["state"]

    service_domain, service_name = service_ref.split(".", 1)
    await hass.services.async_call(service_domain, service_name, {"entity_id": target_entity_id}, blocking=False)


async def _async_process_chat_message(hass: HomeAssistant, entry: ConfigEntry, topic: str, payload: str) -> None:
    message = payload.strip()
    if not message:
        return

    received_at = dt_util.utcnow().isoformat()
    event_data = {
        "entry_id": entry.entry_id,
        "name": entry.title,
        "hwid": entry.data.get(CONF_HWID),
        "topic": topic,
        "message": message,
        "payload": payload,
        "received_at": received_at,
    }
    hass.bus.async_fire(EVENT_CHAT_MESSAGE, event_data)
    await _async_create_chat_notification(hass, entry, message, received_at)

    runtime = _entry_runtime(hass, entry.entry_id)
    runtime["last_chat_message"] = message
    runtime["last_chat_topic"] = topic
    runtime["last_chat_received_at"] = received_at
    async_dispatcher_send(hass, entry_runtime_signal(entry.entry_id))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    topic = entry.data[CONF_TOPIC]
    chat_topic = _chat_topic_for_entry(entry)
    state_topic = _state_topic_for_entry(entry)
    runtime = _entry_runtime(hass, entry.entry_id)
    runtime["state_sync_targets"] = _state_sync_targets_for_entry(hass, entry)
    runtime["pending_target_states"] = {}

    @callback
    def _message_received(message: mqtt.ReceiveMessage) -> None:
        hass.async_create_task(_async_process_message(hass, entry, message.topic, message.payload))

    @callback
    def _chat_message_received(message: mqtt.ReceiveMessage) -> None:
        hass.async_create_task(_async_process_chat_message(hass, entry, message.topic, message.payload))

    @callback
    def _state_message_received(message: mqtt.ReceiveMessage) -> None:
        hass.async_create_task(_async_process_state_message(hass, entry, message.topic, message.payload))

    @callback
    def _target_state_changed(event) -> None:
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")

        if not entity_id or new_state is None:
            return
        if new_state.state not in {STATE_ON, STATE_OFF}:
            return
        if old_state is not None and old_state.state == new_state.state:
            return

        pending_target_states = runtime.setdefault("pending_target_states", {})
        pending_state = pending_target_states.get(entity_id)
        if pending_state == new_state.state:
            pending_target_states.pop(entity_id, None)
            return

        sync_targets = runtime.get("state_sync_targets", {}).get(entity_id, [])
        for sync_target in sync_targets:
            hass.async_create_task(
                _async_publish_control_state(
                    hass,
                    entry,
                    entity_id,
                    sync_target["control_topic"],
                    new_state.state,
                )
            )

    runtime["unsubscribers"] = [
        await mqtt.async_subscribe(hass, topic, _message_received, 0),
        await mqtt.async_subscribe(hass, chat_topic, _chat_message_received, 0),
        await mqtt.async_subscribe(hass, state_topic, _state_message_received, 0),
    ]
    if runtime["state_sync_targets"]:
        runtime["unsubscribers"].append(
            async_track_state_change_event(hass, list(runtime["state_sync_targets"].keys()), _target_state_changed)
        )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("Subscribed '%s' to topics '%s', '%s', and '%s'", entry.title, topic, chat_topic, state_topic)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    runtime = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if runtime is not None:
        for unsubscribe in runtime.get("unsubscribers", []):
            unsubscribe()
    return unload_ok

