"""Offline validation without an installed Home Assistant instance."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "govee_light_ble"


def main() -> None:
    files = list(COMPONENT.rglob("*.py")) + list((ROOT / "tests").rglob("*.py"))
    for file in files:
        ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    for file in ROOT.rglob("*.json"):
        json.loads(file.read_text(encoding="utf-8"))
    manifest = json.loads((COMPONENT / "manifest.json").read_text())
    assert manifest["domain"] == "govee_light_ble"
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:b\d+)?", manifest["version"])
    assert manifest["config_flow"] is True
    assert len(manifest["bluetooth"]) == 2
    assert (COMPONENT / "brand" / "icon.png").is_file()
    for file in COMPONENT.rglob("*.py"):
        source = file.read_text()
        assert not re.search(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b", source), file
    print(f"Validated {len(files)} Python files, JSON files, manifest, and icon.")


if __name__ == "__main__":
    main()
