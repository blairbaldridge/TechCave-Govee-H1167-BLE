"""Fill the GitHub owner/repository placeholders before the first publication."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "TechCave-Govee-H1167-BLE"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("github_owner", help="Existing GitHub username or organization")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args()
    for part in (args.github_owner, args.repo):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", part):
            parser.error("GitHub owner and repo must be simple valid identifiers")
    for path in [ROOT / "README.md", ROOT / "custom_components/govee_light_ble/manifest.json"]:
        content = path.read_text(encoding="utf-8")
        content = content.replace("YOUR_GITHUB_USERNAME", args.github_owner)
        content = content.replace(DEFAULT_REPO, args.repo)
        path.write_text(content, encoding="utf-8")
    print(f"Updated repository links to https://github.com/{args.github_owner}/{args.repo}")
    print("Review LICENSE and ATTRIBUTION.md before making repository public.")


if __name__ == "__main__":
    main()
