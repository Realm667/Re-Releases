"""Package-only native precache lists for generated cosmetic actor classes.

Source map definitions stay authoritative; no actor is spawned by this metadata.
The engine's gl_precache setting controls GPU uploads at map loading.
"""
import re


def prepare_precache(payload):
    payload = dict(payload)
    classes = {}
    for name, data in payload.items():
        if name.lower().startswith(("skyedges/", "lavalips/")) and name.lower().endswith(".txt"):
            mapname = name.rsplit("/", 1)[-1][:-4].upper()
            for row in data.decode().splitlines():
                kind = row.split("|", 1)[0]
                if re.fullmatch(r"UTNT[A-Za-z0-9_]+", kind):
                    classes.setdefault(mapname, set()).add(kind)
    def add(match):
        names = sorted(classes.get(match[1].upper(), ()))
        if not names:
            return match[0]
        return match[0] + '\n    PrecacheClasses = ' + ', '.join('"'+n+'"' for n in names) + '\n'
    for name in list(payload):
        if name.lower() == "mapinfo.txt":
            text = payload[name].decode()
            payload[name] = re.sub(r'(?im)^map\s+(\w+)\s+[^\n{]*\s*\{', add, text).encode()
    return payload
