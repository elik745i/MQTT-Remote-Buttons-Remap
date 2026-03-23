## Highlights

- Added bidirectional state sync for mapped toggle controls.
- Added a visible Home Assistant persistent notification for the latest incoming remote chat message.
- Preserved the earlier options-flow and mapping fixes.

## Added

- MQTT state mirroring from Home Assistant back to mapped remote toggle controls.
- Persistent notification creation for incoming remote-to-HA chat messages.

## Changed

- Integration version bumped to `0.1.8`.
- The integration now listens for state changes on mapped stateful target entities.

## Fixed

- Mapped toggle controls now stay synchronized when they are switched from the Home Assistant side.