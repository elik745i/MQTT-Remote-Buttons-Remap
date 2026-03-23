# Publishing Checklist

This repository is prepared as a standalone HACS custom integration repository.

Current repository:

1. `https://github.com/elik745i/MQTT-Remote-Buttons-Remap`

Repository checklist:

1. Keep `hacs.json` in the repository root.
2. Keep only one integration under `custom_components/`.
3. Keep `documentation` and `issue_tracker` in `custom_components/mqtt_remote_buttons_remap/manifest.json` pointing at this repository.
4. GitHub Actions now auto-publishes releases for future tags matching `v*`.
5. For an already-pushed tag like `v0.1.0`, run the `Publish Release` workflow manually and pass the tag name.

Suggested current release:

- Title: `v0.1.1`
- Notes summary:
  - Initial HACS-ready release of `MQTT Remote Buttons Remap`
  - Config-flow based setup for selecting an ESP32 MQTT remote
  - Per-button mapping from discovered MQTT controls to Home Assistant entities
  - Toggle action synchronization for compatible Home Assistant stateful entities
  - Included HACS metadata and brand icon assets

Minimum expected root layout:

```text
README.md
PUBLISHING.md
hacs.json
.github/
  workflows/
    release.yml
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