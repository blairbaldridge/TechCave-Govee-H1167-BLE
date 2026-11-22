# Bluetooth device discovery and troubleshooting

## New first-time setup (v1.2.1)

Choose **Settings → Devices & services → Add integration → TechCave Govee H1167 BLE**. The wizard requests a five-second active scan using Home Assistant's Bluetooth manager, then shows **all BLE advertisements** currently cached by Home Assistant. The list is not filtered by the H1167 name.

Each row contains the advertised name (or **Unnamed BLE device**), Bluetooth address, H1167-name match status, **Connectable** or **Scan only (cannot control)**, and signal strength where available. Connectable devices appear first, and H1167/Govee names are prioritized within those groups.

A device marked **Scan only** is useful for locating the box, but cannot be selected until a connectable Bluetooth adapter or proxy can reach it. H1167 needs a GATT connection for power and mode control.

Selecting a device with a name that doesn't identify it as H1167 requires **explicit model confirmation**. The list includes unrelated devices such as smart home sensors, phones, and headphones; **do not select them** unless you can verify the Bluetooth address belongs to your box. Already configured devices are excluded to avoid duplicate integrations.

## If your box is not listed

1. Ensure the H1167 is powered and within BLE range of a Home Assistant adapter or an ESPHome **connectable** Bluetooth proxy.
2. Verify **Settings → Devices & services → Bluetooth** is configured and your adapter/proxy appears.
3. Close the Govee mobile app if it is using the box, and choose **Scan again**.
4. Try correlating an unknown or unnamed BLE address by switching the H1167 off/on and observing which advertisement disappears or returns.
5. If the box shows as **Scan only**, improve connectable BLE coverage. Passive reception alone cannot send commands.
6. If the box remains absent, choose **Enter Bluetooth address manually** and use its actual BLE address. Manual setup does not bypass BLE range requirements.

Home Assistant enumerates BLE advertisements, **not Bluetooth Classic devices**. Scanners in AUTO mode can perform the requested active scan; depending on scanner configuration, some devices may not advertise during the short window.

## Manual setup

Use six hexadecimal octets separated by colons, e.g. `AA:BB:CC:DD:EE:FF`. The optional friendly name does not affect discovery. The form checks address syntax, not device identity.

## Logging

Home Assistant **Settings → System → Logs** can show `govee_light_ble` errors. To enable verbose logging:

```yaml
logger:
  logs:
    custom_components.govee_light_ble: debug
```

Restart after changing YAML logging. Redact Bluetooth addresses and other identifying data before sharing logs.

## ESPHome Bluetooth Proxy

Home Assistant's Bluetooth manager chooses a connectable proxy/adapter for the BLE address. The address entered is **the H1167's**, not the proxy's MAC or IP address. An advertisement visible only on a passive scanner is not sufficient for GATT commands.
