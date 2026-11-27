# Stable versioning, archive branches, and HACS rollback

## Version convention

The first public stable release line is **v1.0** (manifest `1.0.0`, GitHub tag/release `v1.0.0`). Next owner-approved functional release: **v1.1.0**. Patches may use `1.0.1` or `1.1.1`. Use full `MAJOR.MINOR.PATCH` in Home Assistant manifests, tags and releases.

The older development manifest version `1.2.2` and `v1.2.2b1`–`v1.2.2b3` test prereleases predate this stable numbering reset. They remain historical test builds and can sort above v1.0.0 in beta-enabled version selectors; select the intended tag explicitly.

| Git reference | Purpose | Behavior |
| --- | --- | --- |
| `main` | Approved stable source | Only the owner authorizes changes; current 1.0.0 |
| `archive/v1.0` | Frozen v1.0 release line | Keep after v1.1 arrives; it can hold the last v1.0.x if that series receives patches |
| `v1.0.0` Git tag/release | Immutable v1.0.0 snapshot | Intended for HACS selection and rollback |
| `test` | Experimental development | Contains all 22 renamed H1167 modes; auto beta prereleases |

## Publishing a new stable release

1. Validate a beta on Home Assistant and request explicit authorization to promote the desired changes. Never update `main` just because a test passes.
2. Bump `custom_components/govee_light_ble/manifest.json` to the approved target, e.g. `1.1.0`, and update README/changelog, tests, and the stable documentation as needed.
3. Push the approved changes to protected `main` using the owner's authorized connection. The `.github/workflows/stable-release.yml` workflow is triggered by the push.
4. The workflow validates syntax and JSON, runs offline unit tests and Hassfest, and only then creates a permanent GitHub tag `v1.1.0`, a normal GitHub Release, and the matching `archive/v1.1` branch. It must not overwrite existing release tags. Monitor Actions and verify the new release URL.
5. Previous Git tags/releases and archive branches are **never removed or moved** when publishing another minor series. The test branch is independent.

The workflow is intentionally strict: a push to `main` that reuses the same stable manifest version while changing the commit cannot silently replace an existing release. Increment the version for the next approved change.

## Installing or rolling back with HACS

Use the same custom repository URL `https://github.com/blairbaldridge/TechCave-Govee-H1167-BLE`. Go to the integration's HACS page, select **Redownload**, choose the appropriate version tag (`v1.0.0`, `v1.1.0`, etc.), then restart Home Assistant. Back up first; do **not** remove the configured H1167 device. The integration domain and entity unique IDs are unchanged.

HACS's normal version selector usually shows **the five latest GitHub releases plus the default branch**, not every Git branch or every older release. The `archive/v1.0` branch is a GitHub source backup, not a guaranteed HACS dropdown entry. If v1.0.0 becomes too old to appear, use its permanent GitHub tag/release for manual download and restore into `/config/custom_components/govee_light_ble/`, followed by a restart.

The beta `test` workflow remains separate. It currently generates historical `1.2.2bN` beta versions, which compare numerically higher than the new stable `1.0.0`. Coordinate a future beta numbering transition separately and **do not mistake a beta for a newer approved stable release**.

## Safety and GitHub branch protection

The protected `main` ruleset remains in place; only changes explicitly requested by the repository owner should be pushed there. The release workflow creates tags and archive branches but does not write back to `main` and never merges `test` automatically. Run hardware tests before promotion.
