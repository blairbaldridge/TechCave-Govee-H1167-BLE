# Contributing

Bug reports and pull requests are welcome, particularly independent hardware tests with H1167 boxes and different Bluetooth proxies.

- Before reporting an issue, test the latest tagged release and check `docs/BLUETOOTH_SETUP.md`.
- Include a reproducible scenario, HA version, adapter/proxy type, and sanitized logs. Redact addresses.
- For code changes, preserve the `govee_light_ble` domain and entity unique IDs; do not modify captured H1167 frames without test evidence.
- Run `python scripts/validate_local.py` and `python -m unittest discover -s tests -v` before a PR.
- Keep new model support opt-in and hardware-tested; generic `Govee_*` advertisements must not automatically be claimed as H1167.