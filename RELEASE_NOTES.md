## Highlights

- Fixed the Home Assistant to remote state bridge for mapped toggle controls.
- Switched to direct state tracking callbacks for mapped target entities.
- Hardened MQTT publishing so the bridge works whether Home Assistant exposes the helper as sync or awaitable.

## Added

- No new features in this patch.

## Changed

- Integration version bumped to `0.1.9`.
- Bidirectional state sync now uses direct state tracking instead of event-object callbacks.

## Fixed

- MQTT control topics now receive HA-side toggle updates reliably.