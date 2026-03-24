# HACS Default Store PR

This repository is intended to be added to the HACS default integration list in:

- `hacs/default`
- file: `integration`

Repository entry to add:

```json
"elik745i/MQTT-Remote-Buttons-Remap"
```

Alphabetical insertion point:

- after `Elijaht-dev/ovh_ipv6`
- before `elsbrock/cowboy-ha`

Resulting snippet in `hacs/default/integration`:

```json
  "ElectroceanTech/HomeAssistant",
  "Elijaht-dev/ovh_ipv6",
  "elik745i/MQTT-Remote-Buttons-Remap",
  "elsbrock/cowboy-ha",
  "Elwinmage/ha-reefbeat-component",
```

Suggested PR title:

```text
Add elik745i/MQTT-Remote-Buttons-Remap to integration
```

Suggested PR body:

```text
## Checklist

- [x] I am the owner or a major contributor of the repository.
- [x] The repository is public and hosted on GitHub.
- [x] The repository can be added to HACS as a custom repository.
- [x] The repository includes the HACS validation workflow.
- [x] The repository includes Hassfest.
- [x] The repository has at least one GitHub release.
- [x] I added the repository to the correct category file in alphabetical order.
- [x] This PR is editable by HACS maintainers.

## Repository

- Repository: https://github.com/elik745i/MQTT-Remote-Buttons-Remap
- Category: integration

## Notes

- This integration provides config-flow based remapping of MQTT-discovered ESP32 remote button actions to Home Assistant entities.
```

Current blocker before submitting:

- Confirm the `Validate` workflow is green on the latest commit before opening the PR.
- This environment does not have the GitHub authentication needed to fork `hacs/default`, push a branch, and open the PR on your behalf, so the final PR submission must be done from your GitHub account.