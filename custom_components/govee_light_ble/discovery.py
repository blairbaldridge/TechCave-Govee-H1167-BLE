"""Small model-name helpers; no Home Assistant imports so they can be tested."""


def is_h1167_name(name: str) -> bool:
    """Match model-bearing advertisements only; do not claim all Govee BLE supported."""
    return "H1167" in name.strip().upper()
