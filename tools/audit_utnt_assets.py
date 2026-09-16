"""Read-only size/duplicate audit and reference checks for consolidated UTNT assets.

No missing text match is treated as proof that an asset is unused. Doom namespaces,
implicit frames, animation ranges, IWAD replacements and generated names matter.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
from build_utnt import ROOT, input_files


def check_consolidation(root=ROOT):
    root=Path(root); mod=root/'tutnt'
    manifest=json.loads((root/'tools/asset-consolidation.json').read_text())
    definitions=[mod/'TEXTURES.txt', *sorted((mod/'textures/definitions').glob('*'))]
    text='\n'.join(p.read_text() for p in definitions)
    for row in manifest['duplicates']:
        old=(mod/row['removed']).resolve(); target=(mod/row['canonical']).resolve()
        old.relative_to(mod.resolve()); target.relative_to(mod.resolve())
        if old.exists(): raise ValueError('Duplicate reintroduced: '+row['removed'])
        if not target.is_file(): raise ValueError('Missing canonical asset: '+row['canonical'])
        if hashlib.sha256(target.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Canonical content changed; review shared consumers: '+row['canonical'])
        if 'remap' in row:
            directive='Remap "'+row['remap']+'" "'+row['canonical']+'"'
            if directive not in text: raise ValueError('Missing hires remap: '+row['removed'])
        elif re.search(r'\bPatch\s+"'+re.escape(old.stem)+r'"\s*,',text,re.I):
            raise ValueError('Reference to removed patch: '+row['removed'])
    for row in manifest['unused']:
        if (mod/row['path']).exists(): raise ValueError('Obsolete asset reintroduced: '+row['path'])
    # Explicit image paths, unlike bare lump names, must resolve locally.
    for name in re.findall(r'\b(?:Patch|Remap\s+"[^"\n]+")\s+"([^"\n]+)"',text,re.I):
        if '/' in name and not (mod/name).is_file(): raise ValueError('Missing texture image: '+name)
    return {'duplicates':len(manifest['duplicates']), 'unused':len(manifest['unused']),
            'removed_image_bytes':sum(r['bytes'] for r in manifest['duplicates']+manifest['unused'])}


def audit(root=ROOT):
    root=Path(root); groups=collections.defaultdict(list); folders=collections.Counter()
    files=input_files(root)
    for path in files:
        data=path.read_bytes(); name=path.relative_to(root/'tutnt').as_posix()
        folders[name.split('/')[0]]+=len(data)
        groups[hashlib.sha256(data).hexdigest()].append({'path':name,'bytes':len(data)})
    duplicates=sorted((v for v in groups.values() if len(v)>1),
                      key=lambda v:v[0]['bytes']*(len(v)-1),reverse=True)
    return {'files':len(files),'bytes':sum(folders.values()),'folders':dict(folders.most_common()),
            'duplicate_bytes':sum(v[0]['bytes']*(len(v)-1) for v in duplicates),
            'duplicates':duplicates,
            'note':'Candidates only: identical content may require separate namespaces or public names.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--report',type=Path)
    parser.add_argument('--check',action='store_true',help='Check reviewed consolidations only')
    args=parser.parse_args()
    result=check_consolidation(args.root) if args.check else audit(args.root)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='duplicates' or args.check},indent=2))
