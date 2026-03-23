# Publishing Checklist

This repository is prepared as a standalone HACS custom integration repository.

Current repository:

1. `https://github.com/elik745i/MQTT-Remote-Buttons-Remap`

Repository checklist:

1. Keep `hacs.json` in the repository root.
2. Keep only one integration under `custom_components/`.
3. Keep `documentation` and `issue_tracker` in `custom_components/mqtt_remote_buttons_remap/manifest.json` pointing at this repository.
4. Required validation workflows are included in `.github/workflows/validate.yml` and `.github/workflows/hassfest.yml`.
5. GitHub Actions auto-publishes releases for future tags matching `v*`.
6. For an already-pushed tag like `v0.1.0`, run the `Publish Release` workflow manually and pass the tag name.

Suggested current release:

- Title: `v0.1.6`
- Notes summary:
  - Fix the Home Assistant gear-icon options dialog after the text-entry mapping change
  - Keep pasted entity ID support with validation shown on submit instead of breaking form rendering
  - Preserve the v0.1.5 chat and battery alert additions

Minimum expected root layout:

```text
README.md
PUBLISHING.md
hacs.json
.github/
  workflows/
    hassfest.yml
    validate.yml
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