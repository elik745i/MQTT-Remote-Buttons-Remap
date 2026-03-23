## Highlights

- Added pasteable Home Assistant entity IDs in the mapping UI, with domain validation for press and toggle sources.
- Added remote-to-HA chat handling through `mqtt_remote_buttons_remap_chat_message` and the `Last Chat Message` diagnostic sensor.
- Added battery alert handling through `mqtt_remote_buttons_remap_battery_alert` and the `Last Battery Alert` diagnostic sensor.

## Added

- Battery alert events for low battery and fully charged transitions.
- Diagnostic sensor that stores the latest emitted battery alert together with percent, voltage, and charging attributes.
- Release workflow support for including a human-written summary in GitHub releases.

## Changed

- Integration version bumped to `0.1.5`.
- README updated to document MQTT battery entities, chat support, alert events, and automation usage.

## Fixed

- Mapping options no longer depend on dropdown-only selection for valid Home Assistant entity IDs.