"""Validate imported death assets and unique active sprite names against the manifest."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def check(root=ROOT):
    root=Path(root);mod=root/'tutnt'
    manifest=json.loads((root/'tools/alternate-deaths.json').read_text(encoding='utf-8'))
    names=defaultdict(list)
    for p in (mod/'sprites').rglob('*'):
        if p.is_file():names[p.stem.upper()].append(p)
    targets=set();digests=set();references=0
    for asset in manifest['assets']:
        path=root/asset['target'];digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==asset['sha256'], 'Changed reference asset: '+str(path)
        assert path not in targets and digest not in digests, 'Duplicate imported image: '+str(path)
        assert len(names[path.stem.upper()])==1, 'Sprite name collision: '+path.stem
        targets.add(path);digests.add(digest)
    assert targets==set((mod/'sprites/alternate-deaths').iterdir()), 'Unrecorded imported asset'
    for source in manifest['sources']:
        folder=root/source/'sprites'
        if not folder.is_dir():continue
        originals={p.name.casefold():p for p in folder.rglob('*') if p.is_file()}
        for asset in manifest['assets']:
            for name in [asset['source']]+asset.get('source_aliases',[]):
                p=originals[Path(name).name.casefold()]
                assert hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256'], 'Reference differs: '+str(p)
        references+=1
    states=(mod/'actors/alternate-deaths.txt').read_text(encoding='utf-8')
    used=set()
    for sprite,frames in re.findall(r'^\s+(UD\w{2})\s+([A-Z]+)\s+-?\d+',states,re.M):
        for frame in frames:
            name=sprite+frame+'0';assert len(names[name])==1, 'Missing state image: '+name
            used.add(names[name][0])
    assert used==targets, 'Unused imported image'
    for item in manifest['classes']:
        assert states.count('actor '+item['class']+' : '+item['base']+' replaces '+item['base'])==1
    return {'assets':len(targets),'classes':len(manifest['classes']),
            'sequences':sum(len(c['states']) for c in manifest['classes']),
            'local_references_compared':references,'sprite_names':'unique','hashes':'ok'}

if __name__=='__main__':print(json.dumps(check(),indent=2))
