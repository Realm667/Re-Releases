"""Prove notice adapters preserve campaign geometry and all other ACS statements."""
from pathlib import Path
import argparse, collections, json, re, struct, subprocess
from build_utnt import read_wad

R = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--base', default='125d46b4302c491afaf689af0273a3da7c6c7fc3')
a = p.parse_args()

def before(path):
    return subprocess.check_output(['git', '-c', f'safe.directory={R.as_posix()}',
        '-C', str(R), 'show', f'{a.base}:{path}'])

def lumps(data):
    _, count, directory = struct.unpack_from('<4sII', data)
    result = {}
    for i in range(count):
        pos, size, name = struct.unpack_from('<II8s', data, directory+i*16)
        result[name.rstrip(b'\0').decode()] = data[pos:pos+size]
    return result

def mask_comments(s):
    return re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',
        lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0])
        if m[0].startswith('/') else m[0], s, flags=re.S)

def strip_notices(s, new):
    pattern = (r'ScriptCall\("UTNTWorldHandler","BeginNotice",[^;]*?\);' if new
        else r'(?i)\bprint(?:bold)?\s*\([^;]*?\)\s*;')
    for m in reversed(list(re.finditer(pattern, mask_comments(s)))):
        s = s[:m.start()] + s[m.end():]
    return s

manifest = json.loads((R/'tools/fixtures/minor-notices/manifest.json').read_text(encoding='utf-8'))
report = []
for path in sorted((R/'tutnt/maps').glob('*.wad')):
    old = lumps(before(path.relative_to(R).as_posix()))
    new = lumps(path.read_bytes())
    assert old.keys() == new.keys(), path.name
    changed = [n for n in old if old[n] != new[n]]
    assert set(changed) <= {'SCRIPTS', 'BEHAVIOR'}, (path.name, changed)
    old_source, new_source = [d['SCRIPTS'].decode('utf-8') for d in (old,new)]
    assert strip_notices(old_source,False) == strip_notices(new_source,True), path.name
    # Verify each adapter's recipient and dynamic expression, including duplicates.
    expected = collections.Counter(f'ScriptCall("UTNTWorldHandler","BeginNotice",{m["id"]},{m["target"]},{m["value"]});'
        for m in manifest['messages'] if m['map']==path.stem)
    actual = collections.Counter(re.findall(r'ScriptCall\("UTNTWorldHandler","BeginNotice",[^;]*?\);',mask_comments(new_source)))
    assert actual == expected, (path.name, actual-expected, expected-actual)
    report.append({'map':path.stem, 'changed_lumps':changed,
        'all_non_notice_script_code_identical':True,'adapters':sum(actual.values())})

shared = 'tutnt/source/tutnt.acs'
old = before(shared).decode('utf-8').replace('\r\n','\n')
new = (R/shared).read_text(encoding='utf-8')
old_call = 'HudmessageBold(l:"UTNT_COMMON_057"; HUDMSG_FADEINOUT,19,CR_UNTRANSLATED,320.0,470.0,1.0,1.0,1.0);'
new_call = 'ScriptCall("UTNTWorldHandler","BeginNotice",57,-2,-1);'
assert old.count(old_call)==new.count(new_call)==1
assert old.replace(old_call,new_call)==new, 'shared ACS changes outside checkpoint presentation'
result = {'ok':True,'base':a.base,'maps':report,'checkpoint_adapters':1,
    'map_adapters':sum(x['adapters'] for x in report)}
(R/'logs/minor-notices-contracts.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(f"PASS: {len(report)} maps, {result['map_adapters']} message adapters and checkpoint; geometry and remaining ACS unchanged.")
