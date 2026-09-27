"""Inventory MAP01 progression and skill placement. Does not prove reachability or balance."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_campaign import scripts, udmf
from build_utnt import read_wad
from check_engine import ROOT

KEYS = {5, 6, 13, 38, 39, 40}
WEAPONS = {2001, 2002, 2003, 2004, 2005, 2006, 82, 6001, 6003}
AMMO = {17, 2007, 2008, 2010, 2046, 2047, 2048, 2049, 6002, 6005}
HEALTH = {2011, 2012, 2013, 2014, 83}


def audit(path):
    lumps = {n.rstrip(b"\0").decode(): d for n, d in read_wad(path)[1]}
    data = udmf(lumps["TEXTMAP"].decode())
    report = {"map": path.name, "limitation": "Static placement and script inventory; no reachability, ammo sufficiency or full-playthrough claim.",
              "counts": {k: len(v) for k, v in data.items()},
              "lump_sha256": {n: hashlib.sha256(d).hexdigest() for n, d in lumps.items()},
              "skills": [], "keys": [], "player_starts": [], "locks": [],
              "progression_scripts": scripts(lumps["SCRIPTS"].decode())}
    for mode in ("single", "coop"):
        for skill in range(1, 6):
            things = [t for t in data["thing"] if t.get(mode, False) and t.get(f"skill{skill}", False)]
            counts = Counter(t["type"] for t in things)
            report["skills"].append({"mode": mode, "skill": skill, "things": len(things),
                                     "weapon_pickups": sum(counts[t] for t in WEAPONS),
                                     "ammo_pickups": sum(counts[t] for t in AMMO),
                                     "health_pickups": sum(counts[t] for t in HEALTH),
                                     "keys": sum(counts[t] for t in KEYS), "type_counts": dict(sorted(counts.items()))})
    for i, thing in enumerate(data["thing"]):
        if thing["type"] in KEYS:
            report["keys"].append(dict(index=i, **thing))
        if thing["type"] in (1, 2, 3, 4, 4001, 4002, 4003, 4004):
            report["player_starts"].append(dict(index=i, **thing))
    for i, line in enumerate(data["linedef"]):
        if line.get("special") in (13, 83, 85) or line.get("locknumber", 0):
            report["locks"].append(dict(index=i, **line))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=ROOT / "zdcmp1/Maps/map01.wad")
    parser.add_argument("--output", type=Path, default=ROOT / "logs/zdc-map-audit.json")
    args = parser.parse_args()
    report = audit(args.map)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("map", "limitation", "counts")}))
    for row in report["skills"]:
        print(json.dumps({k: v for k, v in row.items() if k != "type_counts"}))


if __name__ == "__main__":
    main()
