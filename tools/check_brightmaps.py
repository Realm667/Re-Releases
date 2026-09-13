"""Validate the TNT release brightmap import, ownership and source provenance.

Python 3.11+ and Pillow. Run from any directory; no files are written.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse
import hashlib
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def pixels(path):
    with Image.open(path) as image:
        image = image.convert('RGBA')
        # Transparent RGB does not affect the visible brightmap.
        data = bytearray(image.tobytes())
        for offset in range(0, len(data), 4):
            if data[offset + 3] == 0:
                data[offset:offset + 3] = b'\0\0\0'
        return image.size, hashlib.sha256(data).hexdigest()


def uncomment(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)


def check(root=ROOT):
    root = Path(root)
    mod = root / 'tutnt'
    manifest = json.loads((root / 'tools/brightmap-reference.json').read_text())
    records = manifest['bindings']
    errors = []
    for reference in manifest["reference_definitions"]:
        if digest(root / reference["path"]) != reference["sha256"]:
            errors.append("Reference declarations changed: " + reference["path"])
    ownership = Counter()
    maps = set()
    definitions = {}
    active = []

    def expand(path, stack=()):
        if path in stack:
            errors.append('Cyclic include: ' + str(path))
            return
        text = uncomment(path.read_text())
        active.append(path)
        # Preserve repeated includes: a second load is a real duplicate owner.
        for match in re.finditer(r'#include\s+(?:"([^"]+)"|(\S+))', text, re.I):
            expand(mod / (match[1] or match[2]), (*stack, path))

    expand(mod / 'GLDEFS.txt')
    for path in active:
        text = uncomment(path.read_text())
        for match in re.finditer(r'\bbrightmap\s+(sprite|texture|flat)\s+(\S+)\s*\{([^}]*)\}', text, re.I):
            kind, name, body = match.groups()
            name = name.strip('"').upper()
            token = (kind.lower(), name)
            ownership[token] += 1
            image = re.search(r'\bmap\s+"([^"]+)"', body, re.I)
            definitions[token] = (image[1] if image else None,
                                  {f for f in ('iwad', 'thiswad', 'disablefullbright')
                                   if re.search(r'\b' + f + r'\b', body, re.I)})
    auto = {p.stem.upper(): p for p in (mod / 'materials/brightmaps/auto').glob('*.png')}
    material_maps = {}
    for path in active:
        # Brightmap is a top-level property within the existing Material blocks.
        for match in re.finditer(r'\bMaterial\s+"([^"]+)"\s*\{([^}]*)\}', uncomment(path.read_text()), re.I):
            if re.search(r'\bBrightmap\s+"', match[2], re.I):
                material_maps[match[1].upper()] = path
    for name in auto.keys() & material_maps.keys():
        errors.append('Auto/material duplicate: ' + name)
    for record in records:
        token = (record['kind'], record['target'])
        if ownership[token] != 1:
            errors.append(f'{token}: {ownership[token]} active bindings')
        if definitions.get(token) != (record['map'], set(record['flags'])):
            errors.append(f'{token}: definition differs from audited manifest')
        if record['target'] in auto or record['target'] in material_maps:
            errors.append(f'{token}: duplicate auto/material ownership')
        base = record.get('base')
        if base and digest(root / base['path']) != base['sha256']:
            errors.append(f'{token}: target artwork changed; reaudit alignment')
        if record['map']:
            path = mod / record['map']
            maps.add(path)
            if not path.is_file() or digest(path) != record['map_sha256']:
                errors.append(f'{token}: missing/changed mask')
                continue
            for reference in record['references']:
                source = root / reference['path']
                if digest(source) != reference['sha256'] or pixels(source) != pixels(path):
                    errors.append(f'{token}: release source mismatch: {source}')
    for record in manifest['preserved']:
        path = root / record['map']['path']
        if digest(path) != record['map']['sha256']:
            errors.append('Existing mask changed: ' + str(path))
    for record in manifest['removed_crt_auto_duplicates']:
        if (root / record['path']).exists():
            errors.append('Removed CRT auto mask has returned: ' + record['path'])
    new = set((mod / 'materials/brightmaps/reference').rglob('*.png'))
    if new - maps:
        errors.append('Unreferenced imported masks: ' + ', '.join(p.name for p in new - maps))
    seen = {}
    for path in sorted(set(auto.values()) | set((mod / 'materials/crt/brightmaps').glob('*.png'))):
        seen.setdefault(pixels(path), path)
    for path in sorted(new):
        fingerprint = pixels(path)
        if fingerprint in seen:
            errors.append(f'Duplicate imported image: {path} / {seen[fingerprint]}')
        seen[fingerprint] = path
    if len(new) != manifest['copied_images']:
        errors.append('Imported image count differs from manifest')
    result = {'ok': not errors, 'bindings': len(records),
              'by_kind': dict(Counter(r['kind'] for r in records)),
              'custom_bindings': sum('thiswad' in r['flags'] for r in records),
              'imported_images': len(new), 'preserved_auto_masks': len(manifest['preserved']),
              'removed_crt_duplicates': len(manifest['removed_crt_auto_duplicates']),
              'errors': errors}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    result = check(args.root)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['ok'] else 1)
