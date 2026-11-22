# Changelog

## 1.2.0 — release candidate (2026-11-22)

- Remove the hard-coded Bluetooth address and developer device name from the setup form.
- Add a discovered-device dropdown in the first-run UI using Home Assistant's connectable BLE scanner cache.
- Request a managed five-second active Bluetooth scan on setup/refresh; add scan refresh and manual-address fallback when no H1167 advertisement is visible.
- Restrict unsolicited Bluetooth discovery to names containing the H1167 model and specify model explicitly for new entries.
- Preserve old version-2 entries and existing light/select entity unique IDs.
- Add HACS/Marketplace layout, branding, release documentation, CI validation, translations, and offline tests.
- Use the BLE dependencies provided by Home Assistant Bluetooth rather than specifying an unpinned duplicate Python requirement.
- Keep original H1167 BLE power/mode implementation and all 22 captured scene frames byte-for-byte.

## 1.1.0 — original working local build

- H1167 on/off and mode-selection support (12 Lightshow modes, 10 Carnival modes).