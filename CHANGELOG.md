# Changelog

## 1.0.0 — first numbered stable HACS release (2026-11-26)

- Establish a new **stable** version sequence starting at v1.0.0, with permanent tag/release and `archive/v1.0` branch for rollback.
- Preserve the same working main branch Bluetooth/GATT behavior, device and entity IDs, and 12 Lightshow mode commands; Carnival 1–10 remain disabled.
- Add release automation for subsequent explicitly approved stable updates (for example v1.1.0), without modifying `test`.
- Historical development versions (`1.2.2` manifest and `v1.2.2bN` beta releases) remain in GitHub; they are not part of the new stable sequence.

## 1.2.2 — stable main branch (2026-11-22)

- Promote the tested Bluetooth GATT recovery fixes from `test`: avoid unsupported H1167 notifications and periodic readback, reset stale GATT handles, and retry once after characteristic/discovery errors.
- Temporarily disable **Carnival 1–10** on `main` pending further investigation. Original captured packets remain commented out in `h1167_modes.py`.
- Expose only the **12 Lightshow modes** on `main`. The `test` branch still contains all 22 modes and their captured frames for further work.
- Preserve power on/off control, entity unique IDs, config entries, and Bluetooth device selection.

## 1.2.2 beta — BLE GATT recovery testing (2026-11-22)

- Skip unreliable notification subscriptions on H1167 while retaining notification support for other Govee devices; H1167 power state remains optimistic.
- Avoid periodic H1167 readback polls when notifications are not supported.
- Reset cached characteristics on connection failures and retry once for known stale-GATT errors.
- Preserve all 22 mode frames and existing entity IDs, and add offline regression tests.

## 1.2.1 — test release (2026-11-22)

- Initial setup now lists **all BLE devices seen by Home Assistant**, including unnamed and passive-only advertisements, not only names containing `H1167`.
- Show device addresses and connection capability; show signal strength when available. Put likely Govee/H1167 names near the top.
- Prevent selection of scan-only devices, since H1167 requires connectable Bluetooth.
- Require explicit user confirmation before configuring a device whose advertised name does not identify an H1167.
- Keep existing H1167 automatic discovery filter, MAC-entry fallback, BLE packet commands and integration domain unchanged.
- Add `strings.json`, update translations, documentation, tests and manifest version.

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