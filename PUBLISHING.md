# Publishing Checklist

This repository is prepared as a standalone HACS custom integration repository.

Current repository:

1. `https://github.com/elik745i/MQTT-Remote-Buttons-Remap`

Repository checklist:

1. Keep `hacs.json` in the repository root.
2. Keep only one integration under `custom_components/`.
3. Keep `documentation` and `issue_tracker` in `custom_components/mqtt_remote_buttons_remap/manifest.json` pointing at this repository.
4. Optionally publish GitHub releases so HACS can offer version selection.

Minimum expected root layout:

```text
README.md
PUBLISHING.md
hacs.json
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