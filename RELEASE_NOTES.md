## Highlights

- Fixed the Home Assistant options dialog opened from the gear icon after the mapping UI moved to pasted entity IDs.
- Kept pasted Home Assistant entity IDs in the mapping UI, with validation now applied on submit instead of during form schema rendering.
- Preserved the remote-to-HA chat and battery alert support added in the prior release.

## Added

- Per-field validation errors for invalid pasted entity IDs in the mapping form.

## Changed

- Integration version bumped to `0.1.6`.
- Mapping form validation now runs after submit so Home Assistant can render the options dialog reliably.

## Fixed

- The gear-icon configuration flow no longer crashes with a 500 error when Home Assistant loads the options form.