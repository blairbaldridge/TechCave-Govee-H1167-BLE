# Upgrade, backups and rollback

## Upgrading from the v1.1.0 local installation

The public build **keeps the same `govee_light_ble` domain**, config entry version `2`, existing light unique ID (`<MAC>`), and show-mode select unique ID (`<MAC>_h1167_mode`). It deliberately preserves your existing device entry; the new address finder is for **newly configured devices**.

1. Make a complete Home Assistant backup in **Settings → System → Backups**.
2. In Terminal & SSH, optionally take a separate source backup:

   ```sh
   mkdir -p /config/backups
   tar -czf /config/backups/govee_light_ble_before_v1_2_0.tar.gz -C /config/custom_components govee_light_ble
   ```

3. Install the new integration files using HACS or manually copy **`custom_components/govee_light_ble/`** over the installed folder.
4. Restart Home Assistant. **Do not delete or re-add the configured integration.**
5. Confirm your existing light entity and `Show Mode` select work. If you change a friendly name, existing entity IDs should remain registered.

## Manual installation

Copy the repository's `custom_components/govee_light_ble/` folder to `/config/custom_components/govee_light_ble/`. It must contain `manifest.json`, `config_flow.py`, `discovery.py`, `light.py`, `select.py`, and the other Python files. Restart Home Assistant.

## Rollback

If you need to return to your original working code, replace the updated folder using the backup and restart:

```sh
rm -rf /config/custom_components/govee_light_ble
mkdir -p /config/custom_components
tar -xzf /config/backups/govee_light_ble_before_v1_2_0.tar.gz -C /config/custom_components
```

**Warning:** ensure the archive exists and is valid before running `rm -rf`. No backup is created automatically. Reverting files should not alter HA's config entries. If you used HACS to install v1.2.0, it may offer updates or reinstall newer files until you select the older version or disable updates.
