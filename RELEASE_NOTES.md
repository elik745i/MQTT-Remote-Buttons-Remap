## Highlights

- Fixed Home Assistant flow initialization for the options and reconfigure dialogs.
- Preserved pasted Home Assistant entity IDs in the mapping UI, with validation applied on submit.
- Replaced the broken hotfix with a clean patch release that HACS can detect normally.

## Added

- No new features in this patch.

## Changed

- Integration version bumped to `0.1.7`.
- Flow handlers now call the Home Assistant base initializers before step handling.

## Fixed

- The gear-icon configuration flow and reconfigure dialog no longer fail before the first step is shown.