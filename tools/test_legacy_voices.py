"""Exercise both voice sets through dialogue/chapter playback with a real audio backend."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, default=os.environ.get('UTNT_ENGINE', ROOT/'engine/uzdoom.exe'))
    parser.add_argument('--iwad', type=Path, default=os.environ.get('UTNT_IWAD', 'F:/DoomDev/DOOM2.WAD'))
    parser.add_argument('--mod', type=Path, default=ROOT/'tutnt.pk3')
    args = parser.parse_args()
    logs = ROOT/'tutnt/.codex/logs/legacy-voices'
    report = ROOT/'tutnt/.codex/validation/legacy-voices'
    logs.mkdir(parents=True, exist_ok=True)
    report.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.mod) as archive:
        voices = [p for p in archive.namelist() if p.startswith('sounds/voices/')]
        assert len(voices) == 86, voices
        for n in range(1,44):
            for name in (f'sounds/voices/VOC{n:03}.mp3', f'sounds/voices/legacy/LGVOC{n:03}.ogg'):
                assert hashlib.sha256(archive.read(name)).digest() == hashlib.sha256((ROOT/'tutnt'/name).read_bytes()).digest(), name
    config = logs/'audio.ini'
    config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=640\nwin_h=480\ni_pauseinbackground=false\nvid_activeinbackground=true\nsnd_sfxvolume=0\nsnd_musicvolume=0\n')
    # Keep each exec line below the engine's input buffer limit. Chain stages
    # after their waits so network events and user-CVar changes stay ordered.
    stages = [(0, range(1,44)), (1, range(1,44)), (0, [1,36])]
    for stage, (mode, numbers) in enumerate(stages):
        commands = ['wait 20']
        if stage: commands += [f'UTNT_legacyvoices {mode}', 'wait 10']
        for n in numbers:
            commands += [f'netevent legacyvoicecheck {n} {mode}', 'wait 5', 'listsoundchannels']
        commands += ([f'exec audio{stage+1}.cfg'] if stage<2 else ['echo UTNT_TEST_END', 'quit'])
        line = '; '.join(commands)+'\n'
        assert len(line)<4000
        (logs/f'audio{stage}.cfg').write_text(line)
    cfg = logs/'audio0.cfg'
    si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow=0
    result = subprocess.run([str(args.engine), '-iwad', str(args.iwad), '-file', str(args.mod),
        str(ROOT/'tools/fixtures/legacy-voices'), '-config', str(config), '-savedir', str(logs),
        '-noautoload', '-stdout', '-noidle', '+map', 'INTERMAP', '+exec', str(cfg)],
        cwd=logs, capture_output=True, timeout=60, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW)
    output = (result.stdout+result.stderr).decode(errors='replace')
    (logs/'audio.log').write_text(output, encoding='utf-8')
    expected = {f'{prefix}voc{n:03}' for prefix in ('','lg') for n in range(1,44)}
    playing = set(re.findall(r'\b((?:lg)?voc\d{3}) at \(',output.lower()))
    failures = [line for line in output.splitlines() if 'UTNT_ASSERT FAIL' in line]
    success = result.returncode in (0,1337) and 'UTNT_TEST_END' in output and not failures and expected<=playing
    evidence = dict(ok=success, exit_code=result.returncode, assertions=output.count('UTNT_ASSERT PASS'),
                    recordings_observed=len(playing), missing=sorted(expected-playing), failures=failures)
    (report/'audio.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
    if not success: print(output[-5000:])
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
