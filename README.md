# MQTT Remote Buttons Remap

Custom Home Assistant integration for this firmware family.

Revision: `0.1.8`

Main remote device repository with hardware details and build instructions:

- https://github.com/elik745i/ESP32-2432S024C-Remote

![ESP32-2432S024C Remote](https://github.com/elik745i/ESP32-2432S024C-Remote/raw/main/3D_Models/render1.jpeg)

This integration adds a Home Assistant setup interface for ESP32 remotes that already advertise MQTT buttons and switches through Home Assistant MQTT discovery.

The interface works like this:

1. Choose the MQTT remote device from a dropdown.
2. The integration entry is added immediately.
3. Open that integration entry and configure mappings from its options screen.
4. The integration reads that device's advertised MQTT buttons and toggle controls already registered in Home Assistant.
5. Under each remote button, paste or enter the Home Assistant target entity.
6. Leave any control as `Unmapped` if you do not want to use it.
7. Press-type MQTT buttons trigger press-style Home Assistant entities.
8. Toggle-type MQTT buttons mirror on and off state to a compatible Home Assistant entity.

## What It Listens To

The firmware publishes button actions to:

- `esp32/remote/<HWID>/action`

Examples of payloads:

- `up`
- `down`
- `left`
- `right`
- `button_5`
- `light_on`
- `light_off`

The last two forms are produced by toggle-type MQTT buttons configured in the device UI, and they are what the integration uses to keep mapped stateful targets in sync.

## Installation

### HACS

This package now includes the manifest fields and `hacs.json` metadata HACS expects for a custom integration.

This standalone repository layout is HACS-compatible.

Add this repository in HACS as a custom repository of type `Integration`.

### Manual

1. Copy the folder `custom_components/mqtt_remote_buttons_remap` into your Home Assistant config directory under `custom_components/`.
2. Restart Home Assistant.
3. Make sure the built-in MQTT integration is already configured and connected to the same broker as the ESP32 remote.
4. In Home Assistant, open `Settings -> Devices & services -> Add Integration`.
5. Search for `MQTT Remote Buttons Remap`.
6. Select the ESP32 remote device from the dropdown.
7. The integration entry is created right away.
8. Open the added integration entry and open its options.
9. The options screen shows the mapping dropdowns together with built-in instructions.
10. Assign only the buttons you want.
11. Leave the rest as `Unmapped`.

Final target path in Home Assistant:

```text
config/
  custom_components/
    mqtt_remote_buttons_remap/
      __init__.py
      brand/
        icon.png
      config_flow.py
      const.py
      helpers.py
      manifest.json
      strings.json
```

## UI Behavior

After the integration entry is created, its options screen shows built-in instructions together with one dropdown per advertised MQTT control.

- Source `button` entities from the ESP32 remote are treated as press actions.
- Source `switch` entities from the ESP32 remote are treated as on/off state actions.

Target dropdown behavior:

- Press actions offer Home Assistant entities from `button`, `input_button`, `scene`, and `script` domains.
- Toggle actions offer Home Assistant entities from `switch`, `input_boolean`, `light`, and `fan` domains.
- Every dropdown also includes `Unmapped`, so you can map only the controls you actually want.

This split is intentional. A Home Assistant `button` entity is stateless, so it cannot mirror an MQTT `ON/OFF` state. For actual on/off synchronization, the target must be a stateful entity such as a `switch`, `light`, or `input_boolean`.

## Chat Integration

The firmware already exposes Home Assistant chat over MQTT discovery, and the custom integration now also listens for incoming remote-to-HA chat messages.

Firmware MQTT topics:

- HA -> remote: `esp32/remote/<HWID>/chat/ha/set`
- Remote -> HA: `esp32/remote/<HWID>/chat/ha/received`

What appears in Home Assistant:

- MQTT discovery `text` entity `Send Chat Message`
- MQTT discovery `text` entity `Received Chat Messages`
- Integration-created persistent notification for the latest received chat message
- Custom integration diagnostic sensor `Last Chat Message`
- Custom integration event `mqtt_remote_buttons_remap_chat_message`

This means Home Assistant can display incoming messages in the built-in MQTT text entity, surface the latest one as a visible persistent notification, and still expose a dedicated event/sensor path for automations.

## TTS Automations

Recent Home Assistant versions do not have a built-in `auto speak every incoming MQTT text message` toggle, but this is straightforward with an automation.

Recommended trigger options:

- Trigger on event `mqtt_remote_buttons_remap_chat_message`
- Or trigger on state change of the integration sensor `Last Chat Message`

Typical action:

- Call `tts.speak` with your chosen TTS provider and target `media_player`

High-level example:

```yaml
alias: Remote chat TTS
triggers:
  - trigger: event
    event_type: mqtt_remote_buttons_remap_chat_message
actions:
  - action: tts.speak
    target:
      entity_id: tts.google_translate_en_com
    data:
      media_player_entity_id: media_player.kitchen_speaker
      message: "{{ trigger.event.data.message }}"
```

That gives you future-proof TTS handling without changing the device firmware again.

## Battery Monitoring

The firmware already exposes battery telemetry to Home Assistant over MQTT discovery through the shared state topic:

- MQTT sensor `Battery`
- MQTT sensor `Battery Voltage`
- MQTT binary sensor `Charging`

The custom integration now adds alert semantics on top of that state stream.

What the integration adds:

- Diagnostic sensor `Last Battery Alert`
- Event `mqtt_remote_buttons_remap_battery_alert`

Alert types emitted:

- `low` when battery falls to 15% or below while not charging
- `full` when battery reaches 99% or above

Event data includes:

- `alert_type`
- `message`
- `battery_percent`
- `battery_voltage`
- `battery_charging`
- `received_at`

This is meant for notifications and automations. The actual battery percent / voltage entities still come directly from the firmware MQTT discovery path.

## Synchronization Rules

- MQTT press payloads like `up` or `button_5` call the mapped target's press-style service.
- MQTT toggle payloads like `lamp_on` and `lamp_off` call `turn_on` and `turn_off` on the mapped target.
- When a mapped Home Assistant `switch`, `light`, `fan`, or `input_boolean` changes inside Home Assistant, the integration publishes `ON` or `OFF` back to the matching remote MQTT control topic.
- Toggle actions originating from the remote are not echoed back to the device, which avoids MQTT feedback loops.
- The integration also fires a Home Assistant event named `mqtt_remote_buttons_remap_button_action` for every received payload.

## Example Flow

Example mapping result:

- Remote source `Up` -> `button.tv_volume_up`
- Remote source `Down` -> `button.tv_volume_down`
- Remote source `Lamp` -> `light.corner_lamp`

Behavior:

- Receiving `up` triggers `button.press` on `button.tv_volume_up`.
- Receiving `down` triggers `button.press` on `button.tv_volume_down`.
- Receiving `lamp_on` triggers `light.turn_on` on `light.corner_lamp`.
- Receiving `lamp_off` triggers `light.turn_off` on `light.corner_lamp`.

## Event Emitted

The integration fires these Home Assistant events:

- `mqtt_remote_buttons_remap_button_action`
- `mqtt_remote_buttons_remap_chat_message`
- `mqtt_remote_buttons_remap_battery_alert`

Event data:

- `entry_id`
- `name`
- `hwid`
- `topic`
- `action`
- `payload`

You can use that event in automations if you want to build logic outside the direct mappings saved through the UI.

## Notes

- The remote firmware publishes to a shared action topic per device, not one topic per button.
- The integration derives the list of available source buttons from the MQTT entities already discovered in Home Assistant for that selected device.
- If a button or switch is renamed on the ESP32 and rediscovered by Home Assistant, reopen the integration options and review the mappings.
- HACS metadata for this integration is stored in `hacs.json` in the repository root.
