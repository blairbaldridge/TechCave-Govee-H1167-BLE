# TechCave Govee H1167 BLE

> **Testing branch:** This is the `test` branch. Work here is not merged into `main` until verified. For HACS installs, use [test prereleases](docs/TESTING_WITH_HACS.md), not a `/tree/test` URL. A GitHub Actions workflow creates a beta release from every new push to `test` after validation.

An **unofficial, local-only Home Assistant integration** for the **Govee H1167 Light Show Box**. Control power and choose from 12 named Lightshow modes and 10 named Carnival modes via Bluetooth Low Energy, including a connectable ESPHome Bluetooth proxy. No cloud service, Govee account, or separate controller host is required.

> **Status:** v1.2.1 release candidate. Originally validated on one H1167 device. Community Bluetooth/hardware validation is still needed. Not affiliated with or endorsed by Govee.

## Features

- Light entity for on/off power.
- Select entity for **22 captured modes** using the actual in-app names, including `Rhythm`, `Hopping`, `Brilliant`, and `Shimmer`.
- **Browse all nearby BLE devices detected by Home Assistant** during initial setup, including unnamed and scan-only advertisements; view MAC addresses, connection capability and signal strength when available.
- Manual Bluetooth MAC entry if discovery cannot identify the device.
- Uses Home Assistant's built-in Bluetooth scanning and connectable adapters/proxies.
- Preserves prior `govee_light_ble` config entries and MAC-based entity unique IDs when upgrading from v1.1.0.
- Restores the *last Home Assistant-selected* mode after restart (does not resend the command automatically).


### H1167 mode names used in the Govee app

The test branch uses these names in the Show Mode dropdown. The 20-byte BLE command packets are unchanged.

| Previous mode | Govee app name | Previous mode | Govee app name |
| --- | --- | --- | --- |
| Lightshow 1 | Rhythm | Carnival 1 | Brilliant |
| Lightshow 2 | Sprouting | Carnival 2 | Pulsate |
| Lightshow 3 | Shiny | Carnival 3 | Dazzle |
| Lightshow 4 | Beat | Carnival 4 | Fascination |
| Lightshow 5 | Waves | Carnival 5 | Aspiring |
| Lightshow 6 | Spectrum | Carnival 6 | Cadence |
| Lightshow 7 | Rolling | Carnival 7 | Revel |
| Lightshow 8 | Hopping | Carnival 8 | Fluctuate |
| Lightshow 9 | Starlight | Carnival 9 | Funny |
| Lightshow 10 | Piano Keys | Carnival 10 | Shimmer |
| Lightshow 11 | Jumping | — | — |
| Lightshow 12 | Luminous | — | — |

## Requirements

- Home Assistant **2026.10.0 or newer** (target minimum; tested by the original author on a 2026.10.x installation, not all versions).
- Bluetooth integration set up in Home Assistant.
- A **connectable** Bluetooth adapter or ESPHome Bluetooth proxy that can see the powered-on H1167 box.
- HACS / Marketplace for easy install, or manual file installation.

## Installation with HACS / Marketplace

1. Create/download the release from `https://github.com/blairbaldridge/TechCave-Govee-H1167-BLE`.
2. In Home Assistant, open **HACS** (or **Marketplace** on versions that support it).
3. Use the menu for **Custom repositories** / **Add repository** and add the URL above, of type **Integration**. The repository does not need to be in the default catalog.
4. Find **TechCave Govee H1167 BLE** and select **Download / Install**.
5. Restart Home Assistant if prompted; updates to an already loaded custom integration require a restart.
6. Open **Settings → Devices & services → Add Integration** and search for **TechCave Govee H1167 BLE**.

### First-time setup: find the Bluetooth device automatically

1. Plug in and power on your H1167 box and put it in Bluetooth range of your HA adapter/proxy.
2. Start the **TechCave Govee H1167 BLE** integration setup. The wizard requests a brief managed scan and lists **all BLE devices Home Assistant currently sees**, including unrelated and unnamed devices. Each item shows its name, address, whether it is connectable or scan-only, and optional signal strength. **Select only your actual H1167.**
3. Choose your H1167 and submit. If its advertised name does not include `H1167`, explicitly confirm that you have identified the correct box. Home Assistant stores its Bluetooth address; **the integration does not contain any preprogrammed MAC address**. A scan-only listing cannot be installed until a connectable adapter or proxy can reach it.
4. If the list is empty, choose **Scan again / refresh device list** after allowing time for advertisements. You may need to close the Govee phone app, move the proxy closer, or confirm that Bluetooth is enabled in HA.
5. If scanning still does not show it, select **Enter Bluetooth address manually** and enter your own `AA:BB:CC:DD:EE:FF` address. Name is optional.

Home Assistant may also present an automatically discovered H1167 under *Discovered integrations*. Select **Configure** and confirm it. Automatic Home Assistant discovery still uses the `H1167` name match, but the manual Add Integration wizard lists all cached BLE devices. Nonmatching names require explicit confirmation; this does **not** mean those devices are supported.

**Finding the address if manual setup is required:** Home Assistant's Bluetooth integration/device diagnostics can display nearby advertisements and addresses on supported versions. Alternatively, check with a BLE scanner application or Bluetooth scanner on another computer. Do not use a Wi-Fi MAC, the MAC of a proxy, or a different Govee device. The address must be discoverable through a **connectable** HA scanner for commands to work. See [Bluetooth troubleshooting](docs/BLUETOOTH_SETUP.md).

## Entities

- `light.<your_device_name>` — on/off. Your original entity ID stays intact when you update an existing installation.
- `select.<your_device_name>_show_mode` — last HA-selected Lightshow/Carnival option. Use the actual entity ID shown in **Settings → Devices & services → Entities**.

### Example automation

```yaml
sequence:
  - action: light.turn_on
    target:
      entity_id: light.REPLACE_WITH_YOUR_H1167_LIGHT
  - action: select.select_option
    target:
      entity_id: select.REPLACE_WITH_YOUR_SHOW_MODE_SELECT
    data:
      option: "Hopping"
```

### Example dashboard (built-in Entities card)

```yaml
type: entities
title: Govee H1167 Light Show Box
entities:
  - entity: light.REPLACE_WITH_YOUR_H1167_LIGHT
  - entity: select.REPLACE_WITH_YOUR_SHOW_MODE_SELECT
```

## Important limitations

- **Renamed modes:** Old saved dropdown selections are mapped to their new app names on restart; automations, scripts, and dashboards using a literal old option (such as `Lightshow 8`) should be updated to the new name (such as `Hopping`). Entity IDs are unchanged.
- **Mode state is optimistic.** The select reports the last mode chosen through Home Assistant; it does not track changes from the Govee app or hardware after the fact. It restores the saved UI state after restart, not the actual device mode.
- **Selecting a mode does not automatically turn the box on.** Turn on its light entity first as needed.
- Only the H1167 commands captured on the developer's test box are verified. **Do not assume other Govee models work.** The underlying legacy code may contain LED strip support, but that is not publicly claimed or discovered by this release.
- Bluetooth apps may compete for the box's single BLE connection. Close the Govee app while testing Home Assistant.
- Device must be within range of a **connectable** Bluetooth adapter/proxy; a passive-only scanner will not work.
- Manual entry does not bypass range: unavailable devices will be retried by Home Assistant until connectable.

## Existing v1.1.0 users

Back up `/config/custom_components/govee_light_ble/` and make a full Home Assistant backup before updating. **Do not delete the existing Home Assistant integration/config entry.** Replace the component files through HACS or manually, restart Home Assistant, and confirm the light/select entities are still present. See [upgrade/rollback instructions](docs/UPGRADING.md).

## Support and reporting issues

Open an issue at [Issues](https://github.com/blairbaldridge/TechCave-Govee-H1167-BLE/issues) . Include the Home Assistant version, integration version, proxy type, visible advertised name, and a sanitized log. **Redact Bluetooth MAC addresses and other identifying details** unless you intentionally choose to share them.

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Acknowledgements](ATTRIBUTION.md) · [License](LICENSE)

## Disclaimer

Not an official Govee integration. Run at your own risk and follow safe electrical and installation practices. This project does not communicate with Govee's cloud API.