"""Audit eight-player starts and run eight real peers through campaign entries.
This checks spawns, hub travel and TNT04A intro skip, not a full playthrough.
Outputs stay under tutnt/.codex; use --static-only without launching the engine.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time

from audit_campaign import udmf
from build_utnt import ROOT, read_wad

START_TYPES = (1, 2, 3, 4, 4001, 4002, 4003, 4004)
# Map, numeric level, authored entry position. TNT03A2 position 0 is a solo
# editor start; the campaign enters position 1 through TNT03A1 script 250.
ROUTE = (
    ('TNT04A', 6, 0), ('TNTLE', 10, 0), ('TNT01', 1, 0),
    ('TNT02', 2, 0), ('TNT03A1', 3, 0), ('TNT03A2', 4, 1),
    ('TNT03A1', 3, 1), ('TNT03B', 5, 0), ('TNT04B', 7, 0),
    ('TNT04CN', 8, 0), ('TNT04C', 9, 0), ('INTERMAP', 99, 0),
    ('ENDMAP01', 88, 0),
)
ERRORS = ('UTNT_ASSERT FAIL', 'VM execution aborted', 'Consistency failure',
          'Script error,', 'Execution could not continue', 'errors while parsing')


def things(path):
    lumps = {name.rstrip(b'\0').decode(): data for name, data in read_wad(path)[1]}
    if 'TEXTMAP' in lumps:
        return udmf(lumps['TEXTMAP'].decode())['thing']
    assert 'BEHAVIOR' in lumps, 'Expected Hexen-format presentation map'
    result = []
    for off in range(0, len(lumps['THINGS']), 20):
        tid, x, y, z, angle, kind, flags, special, *args = struct.unpack_from('<HhhhHHH6B', lumps['THINGS'], off)
        result.append(dict(type=kind, x=x, y=y, height=z, arg0=args[0],
                           coop=not bool(flags & 0x400), flags=flags))
    return result


def audit():
    starts = []
    report = []
    for name, number, entry in ROUTE:
        objects = things(ROOT / 'tutnt/maps' / (name.lower() + '.wad'))
        group = []
        for kind in START_TYPES:
            matches = [t for t in objects if t['type'] == kind and t.get('arg0', 0) == entry]
            assert len(matches) == 1, f'{name} entry {entry}: expected one start of type {kind}'
            start = matches[0]
            assert start.get('coop', True), f'{name}: disabled cooperative start {kind}'
            for skill in range(1, 6):
                assert start.get(f'skill{skill}', True), f'{name}: disabled skill {skill} start {kind}'
            group.append(start)
        checkpoint_ids = {t.get('id', 0) for t in objects if t.get('type') in (9001, 9044)}
        for checkpoint in (1, 2, 3):
            first = 1000 + checkpoint * 100
            slots = checkpoint_ids.intersection(range(first, first + 8))
            if slots:
                assert slots == set(range(first, first + 8)), f'{name}: incomplete checkpoint {checkpoint}'
        starts.append(group)
        report.append(dict(map=name, entry=entry, starts=len(group)))
    return starts, report


def fixture(starts, work):
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'tools/fixtures/eight-player/ZSCRIPT', work / 'ZSCRIPT')
    (work / 'MAPINFO').write_text('gameinfo { AddEventHandlers = "UTNTEightPlayerCampaign" }\n')
    names = ','.join(json.dumps(name) for name, _, _ in ROUTE)
    levels = ','.join(str(number) for _, number, _ in ROUTE)
    entries = ','.join(str(entry) for _, _, entry in ROUTE)
    coords = ','.join(f'({t["x"]},{t["y"]})' for group in starts for t in group)
    (work / 'expected.zc').write_text(f'''class UTNTEightExpected : Object
{{
    const Count = {len(ROUTE)};
    static String Map(int stage) {{ String names[]={{ {names} }}; return names[stage]; }}
    static int Level(int stage) {{ int values[]={{ {levels} }}; return values[stage]; }}
    static int Entry(int stage) {{ int values[]={{ {entries} }}; return values[stage]; }}
    static Vector2 Position(int stage,int player) {{ Vector2 values[]={{ {coords} }}; return values[stage*8+player]; }}
}}
''')


def run(args, addon, logs):
    processes = []
    logs.mkdir(parents=True, exist_ok=True)
    options = {}
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        options = dict(startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for p in range(8):
            ini = logs / f'peer-{p}.ini'
            ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=400\nwin_h=300\nvid_maxfps=35\nvid_vsync=false\n')
            out = logs / f'peer-{p}.log'
            handle = out.open('wb')
            command = [str(args.engine), '-iwad', str(args.iwad), '-file', str(args.mod), str(addon),
                       '-config', str(ini), '-savedir', str(logs), '-noautoload', '-nosound', '-stdout',
                       '-noidle', '-nomonsters', '+vid_fullscreen', 'false', '+vid_preferbackend', '1',
                       '+use_mouse', 'false', '+use_joystick', 'false', '+vid_activeinbackground', 'true',
                       '+playerclass', ('Marine', 'Scout', 'Commando')[p % 3],
                       '+UTNT_fxquality', '0', '+UTNT_reducedfx', 'true', '+map', ROUTE[0][0]]
            command += ['-host', '8', '-port', str(args.port)] if p == 0 else ['-join', f'127.0.0.1:{args.port}']
            try:
                child = subprocess.Popen(command, cwd=logs, stdout=handle, stderr=subprocess.STDOUT, **options)
            except BaseException:
                handle.close()
                raise
            processes.append((child, handle, out))
            if p == 0:
                time.sleep(1)
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            outputs = [out.read_text(errors='replace') for _, _, out in processes]
            if all('UTNT_EIGHT_CAMPAIGN_COMPLETE' in text for text in outputs):
                break
            if any(any(error in text for error in ERRORS) for text in outputs):
                break
            if any(child.poll() is not None for child, _, _ in processes):
                break
            time.sleep(.5)
        results = []
        for p, (_, _, out) in enumerate(processes):
            text = out.read_text(errors='replace')
            errors = [error for error in ERRORS if error in text]
            completed = [line for line in text.splitlines() if line.startswith('UTNT_EIGHT_MAP_COMPLETE')]
            ok = not errors and len(completed) == len(ROUTE) and 'UTNT_EIGHT_CAMPAIGN_COMPLETE' in text
            results.append(dict(player=p + 1, ok=ok, maps=len(completed),
                                assertions=text.count('UTNT_ASSERT PASS'), errors=errors, log=str(out)))
        return results
    finally:
        for child, handle, _ in processes:
            if child.poll() is None:
                child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
            handle.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only', action='store_true')
    parser.add_argument('--engine', type=Path, default=os.environ.get('UTNT_ENGINE', ROOT / 'engine/uzdoom.exe'))
    parser.add_argument('--iwad', type=Path, default=os.environ.get('UTNT_IWAD', 'F:/DoomDev/DOOM2.WAD'))
    parser.add_argument('--mod', type=Path, default=ROOT / 'tutnt.pk3')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--port', type=int, default=15239)
    args = parser.parse_args()
    starts, report = audit()
    print(json.dumps(dict(starts=report)), flush=True)
    if args.static_only:
        return
    for key in ('engine', 'iwad', 'mod'):
        value = getattr(args, key).resolve()
        if not value.exists():
            parser.error(f'{key} does not exist: {value}')
        setattr(args, key, value)
    work = ROOT / 'tutnt/.codex/work/eight-player/campaign-fixture'
    fixture(starts, work)
    results = run(args, work, ROOT / 'tutnt/.codex/logs/eight-player-campaign')
    output = ROOT / 'tutnt/.codex/validation/eight-player-campaign.json'
    output.write_text(json.dumps(dict(starts=report, peers=results), indent=2))
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if all(item['ok'] for item in results) else 1)


if __name__ == '__main__':
    main()
