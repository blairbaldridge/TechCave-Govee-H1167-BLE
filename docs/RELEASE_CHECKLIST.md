# Release checklist for repository owner

- [ ] Confirm the GitHub owner/repository name; run `python scripts/set_repository.py YOUR_GITHUB_USERNAME` (use `--repo REPOSITORY` if different).
- [ ] Verify `manifest.json`: `documentation`, `issue_tracker` and `codeowners` point to real GitHub resources.
- [ ] Review `LICENSE` and `ATTRIBUTION.md`; determine origin and redistribution rights of all pre-existing code. Fix anything missing before making it public.
- [ ] Upload the **contents** of this repository ZIP to your repository root (do not upload the ZIP as the sole repository file).
- [ ] Enable GitHub Issues and set a clear description and topics (home-assistant, hacs, bluetooth, govee, h1167).
- [ ] Check the Actions tab and make sure *static-tests*, *hacs*, and *hassfest* all succeed.
- [ ] Back up your Home Assistant config, install as a custom repository in HACS/Marketplace, and verify an existing v1.1.0 entry survives the upgrade.
- [ ] Test fresh install: discovered H1167 selection, no-devices/manual choice, invalid MAC handling, duplicate prevention, power on/off and 12 enabled Lightshow modes; Carnival 1–10 remain disabled on main.
- [ ] Test an ESPHome Bluetooth proxy and a local connectable adapter if possible. Device-level tests must use real hardware.
- [ ] Capture sanitized screenshots and add them to the README when available.
- [ ] For each owner-approved update to `main`, bump `manifest.json` to a new stable version (starting `1.0.0`, next `1.1.0`), then verify the Publish Stable HACS Release workflow succeeded and created the matching `vX.Y.Z` GitHub tag/release and `archive/vX.Y` branch. Never reuse a stable tag.
- [ ] After independent tests and successful validation, optionally request inclusion in the default HACS/Marketplace catalog.

Current publication requirements: https://contributors.home-assistant.io/marketplace/guides/integrations/ and https://hacs.dev/docs/publish/integration/
