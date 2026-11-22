# Bluetooth discovery and troubleshooting

## Why the setup wizard can find a device without a MAC address

This integration asks **Home Assistant's Bluetooth integration** for cached service advertisements from nearby **connectable** adapters/proxies (`bluetooth.async_discovered_service_info(..., connectable=True)`). At the start of the wizard (or on refresh), it asks Home Assistant for a five-second active scan window on scanners that support it, then filters the results by a name containing `H1167` and displays the H1167's advertised device name **and its own Bluetooth address** in a dropdown. Selecting the box saves that discovered address in Home Assistant's config entry.

There is **no hard-coded MAC address**, no developer-specific identifier, and no custom BLE scanner running outside Home Assistant. The scan uses Home Assistant's existing managed scanners, not an independent scanner; active scan windows only affect scanners configured in AUTO mode. If no advertisement is available yet, wait and try **Scan again**. Nearby devices with different advertised names cannot be safely identified as H1167 without verification.

## Checklist if zero H1167 boxes appear

1. Power the light show box and put it near a connectable HA Bluetooth adapter or ESPHome Bluetooth proxy.
2. Verify **Settings → Devices & services → Bluetooth** is set up and the relevant proxy or adapter is connected.
3. Wait for advertisements, then choose **Scan again / refresh device list**. Cancel and reopen setup if the advertisement cache has not updated.
4. Close the Govee phone app so it is not holding the BLE connection.
5. Look for an advertisement named like `Govee_H1167_XXXX` or `GVH1167...`; generic `Govee_*` devices intentionally do **not** appear because they might be unrelated models.
6. If your device advertises a different name, choose **Enter Bluetooth address manually** and supply its address from Home Assistant's advertisement information or another BLE scanner.
7. If you know the address but Home Assistant shows `Cannot reach Govee BLE ... with a connectable Bluetooth adapter`, improve adapter/proxy coverage. A scanner that only receives advertisements cannot make a GATT connection.

## Manual setup

Bluetooth MAC format: six two-digit hexadecimal octets separated by colons, e.g. `AA:BB:CC:DD:EE:FF`. Optional name can be any friendly label. The integration validates address syntax; it does not automatically verify physical model or probe a device on the manual form. Use only with a confirmed H1167 box.

## Logs

In Settings → System → Logs, search for `govee_light_ble` or enable debug logging:

```yaml
logger:
  logs:
    custom_components.govee_light_ble: debug
```

Restart HA after changing logger configuration. Be careful when sharing logs: devices' Bluetooth addresses and related identifiers can appear in error messages.

## Bluetooth Proxy support

The integration resolves the BLE device through Home Assistant's scanner manager, and Home Assistant chooses a connectable adapter/proxy. You do not need to enter the proxy's MAC address or IP address into this integration. A passive-only proxy cannot execute the GATT writes needed for H1167 power/mode control.
