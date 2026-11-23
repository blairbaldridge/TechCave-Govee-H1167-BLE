# Testing from the `test` branch using HACS

This repository has two permanent branches:
- **`main`** — stable integration code; changes arrive here only when tested and intentionally merged.
- **`test`** — experimental changes; pushing here builds a GitHub **prerelease** for testing on Jarvis.

## Important HACS limitation

Adding the URL `https://github.com/blairbaldridge/TechCave-Govee-H1167-BLE/tree/test` as a HACS custom repository **will not select the test branch**. HACS normally installs the default branch or one of the repository's GitHub releases. To test non-default branch code through HACS, we publish a tagged **prerelease from the test branch** and select that version explicitly.

## How beta releases are created

Every new push to `test` runs `.github/workflows/test-prerelease.yml`.

The workflow:
1. Checks out the exact `test` commit.
2. Creates a matching beta version (for example `1.2.2b7`) **in a separate release-only commit**, without modifying `test` or `main`.
3. Runs the offline tests and Home Assistant Hassfest against that release candidate.
4. Pushes a unique `v1.2.2bN` Git tag pointing to the validated snapshot.
5. Publishes a GitHub **Prerelease** for the tag. Only after that step can HACS list the beta version.

If a test fails, no prerelease should be published. If a new push comes in, wait for its corresponding completed release workflow before using that version. You can inspect the workflow on GitHub under **Actions → Publish HACS Test Prerelease** and releases at `https://github.com/blairbaldridge/TechCave-Govee-H1167-BLE/releases`.

The version inside the published tag's `custom_components/govee_light_ble/manifest.json` matches the prerelease tag. The version shown on the branch itself is only the development baseline.

## Install on Jarvis via HACS

1. Back up Jarvis's Home Assistant `/config` folder. The integration domain remains `govee_light_ble`, so don't add two copies of this integration to the same Home Assistant instance.
2. Make sure HACS can access the repository. For a public repository, add `https://github.com/blairbaldridge/TechCave-Govee-H1167-BLE` via **HACS → Custom repositories → Integration**. If already added, keep the same repository.
3. Wait until a test prerelease appears under the repository's **GitHub Releases** page.
4. Open the integration in **HACS**, use **Download** (or **Redownload** if previously downloaded).
5. Enable **Show beta versions**, and choose the corresponding `v1.2.2bN` release. Do **not** choose `main` or the default branch.
6. Download, restart Home Assistant, then use **Settings → Devices & services → Add integration → TechCave Govee H1167 BLE**.
7. Verify Bluetooth discovery, manual entry, power on/off, all 22 H1167 modes, connection recovery, and adapter/proxy behavior on Jarvis.
8. Confirm the installed `/config/custom_components/govee_light_ble/manifest.json` version matches your selected beta tag.

**Important:** Bluetooth on Jarvis's Docker container also requires functional BlueZ/D-Bus integration, the `/run/dbus:/run/dbus:ro` mount, and `NET_ADMIN` and `NET_RAW` capabilities for local adapter management. These must be fixed independently of the custom integration.

## Rollback

To move Jarvis back to a known-good release, use **HACS → Redownload** and select the stable version, if one has been published. If there is no stable release yet, use a known-good beta tag or restore your saved `/config/custom_components/govee_light_ble` backup. Restart Home Assistant after replacing the integration files.

## Promote to main

When a beta has passed Jarvis's full install and regression tests:
1. Open a GitHub pull request: **base = main**, **compare = test**.
2. Review the code diff, verify Actions and hardware results, and explicitly approve merging.
3. Merge the PR into `main` only when ready. The tagged beta release commit is separate from the branch so version numbering in `main` should be set to the desired stable version when promoting.
4. Tag or create a normal stable GitHub release from `main` for HACS users. Never treat a `test` push as a stable release.

## Repository visibility

At the time this guide was created, GitHub reported the repository as **public**. If you want private testing, change visibility in GitHub **Settings → General → Danger Zone**. HACS access to private repositories may require additional GitHub authorization or might not work with the same custom-repository flow; verify the credentials on Jarvis before changing visibility.
