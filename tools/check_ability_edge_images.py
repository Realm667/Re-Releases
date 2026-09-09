"""Check captured ability borders: sharp center, pulse change and clean teardown.

Requires Pillow; pass the log directory from test_ability_edges.py.
"""
from pathlib import Path
import argparse,json
from PIL import Image,ImageChops,ImageStat
p=argparse.ArgumentParser(description=__doc__);p.add_argument('logs',type=Path);a=p.parse_args()
checks=[]
def difference(left,right,box):
    d=ImageChops.difference(left.crop(box),right.crop(box))
    return sum(ImageStat.Stat(d).mean)/3
for path in sorted(a.logs.glob('*-edges-*-off.png')):
    prefix=path.name.removesuffix('-off.png')
    base=Image.open(path).convert('RGB')
    assert base.size==(960,540),base.size
    def read(name):return Image.open(a.logs/(prefix+'-'+name+'.png')).convert('RGB')
    for slot in (1,2):
        low,high,repeat=[read(f'{slot}-{suffix}') for suffix in ['low','high','low-repeat']]
        for name,im in [('low',low),('high',high)]:
            delta=difference(base,im,(280,180,680,350))
            checks.append({'case':prefix,'check':f'{slot} {name}: center unchanged','difference':delta,'ok':delta<0.05})
        delta=difference(low,high,(2,100,40,400))
        metal=prefix.startswith('commando') and slot==2
        checks.append({'case':prefix,'check':f'{slot}: '+('armor is steady' if metal else 'pulse has visible contrast'),'difference':delta,'ok':delta<0.1 if metal else delta>3})
        delta=difference(low,repeat,(2,100,40,400))
        checks.append({'case':prefix,'check':f'{slot}: repeat phase matches','difference':delta,'ok':delta<1.0})
    for name in ('expired','cutscene','frozen'):
        delta=difference(base,read(name),(2,100,958,400))
        checks.append({'case':prefix,'check':name+': view restored','difference':delta,'ok':delta<0.05})
assert checks,'No test captures found'
result={'ok':all(c['ok'] for c in checks),'checks':checks}
(a.logs/'image-checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'ok':result['ok'],'checks':len(checks),'failed':[c for c in checks if not c['ok']]}))
raise SystemExit(0 if result['ok'] else 1)
