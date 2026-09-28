"""Check the reviewed UZDoom 5 clientside actor decisions."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "clientside_manifest.json"
UNSAFE_ACTIONS = re.compile(
    r"\b(?:ACS_\w+|A_Explode|A_CustomMissile|A_SpawnItem(?:Ex)?|"
    r"A_GiveInventory|A_Damage\w*|A_CustomRailgun)\b",
    re.IGNORECASE,
)


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = data["actors"]
    names = [item["class"].lower() for item in records]
    errors: list[str] = []
    if len(names) != len(set(names)):
        errors.append("duplicate class in clientside manifest")

    for path in (ROOT / "Zscript" / "converted").rglob("*.zc"):
        if re.search(r"\+CLIENTSIDEONLY\b", path.read_text(errors="replace"), re.I):
            errors.append(f"legacy CLIENTSIDEONLY flag remains in {path}")

    for item in records:
        path = ROOT / item["source"]
        text = path.read_text(errors="replace")
        pattern = re.compile(rf"(?im)^class\s+{re.escape(item['class'])}\s*:")
        matches = list(pattern.finditer(text))
        if len(matches) != 1:
            errors.append(f"{item['class']}: expected one class in {path}")
            continue
        next_class = re.search(r"(?im)^class\s+\w+\s*:", text[matches[0].end() :])
        end = matches[0].end() + next_class.start() if next_class else len(text)
        body = text[matches[0].start() : end]
        enabled = bool(re.search(r"\+CLIENTSIDE\b", body, re.I))
        if item["disposition"] == "client_visual":
            if not enabled:
                errors.append(f"{item['class']}: real CLIENTSIDE flag missing")
            if UNSAFE_ACTIONS.search(body) or re.search(r"\breplaces\b", body.split("{", 1)[0], re.I):
                errors.append(f"{item['class']}: clientside safety needs review")
        elif item["disposition"] == "world_simulation":
            if enabled:
                errors.append(f"{item['class']}: world actor was made clientside")
        else:
            errors.append(f"{item['class']}: unknown disposition")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated {len(records)} former CLIENTSIDEONLY actors; "
          f"{sum(x['disposition'] == 'client_visual' for x in records)} are clientside visuals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
