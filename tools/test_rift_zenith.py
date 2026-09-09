"""Check the map geometry that anchors the cloud ceiling and the black abyss."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from test_caldera_structure import parse
from build_rift_sky import BEAM
ROOT=Path(__file__).resolve().parent.parent

def verify(root=ROOT):
 _,g=parse(root/'tutnt/maps/tnt04cn.wad')
 # The apparent upper beam is the stacked room, not the lower cylinder at 8392.
 vertices=[];heights=set()
 for line in g['linedef']:
  for sidekey in ['sidefront','sideback']:
   if sidekey not in line:continue
   side=g['sidedef'][int(line[sidekey])];sector=g['sector'][int(side['sector'])]
   if 'T4_BM2' not in side.get('texturemiddle','') or sector.get('id')!='8':continue
   heights.add(float(sector['heightceiling']))
   vertices.extend((float(g['vertex'][int(line[k])]['x']),float(g['vertex'][int(line[k])]['y'])) for k in ['v1','v2'])
 assert heights=={20000.0}
 center=tuple((min(v[a] for v in vertices)+max(v[a] for v in vertices))/2 for a in [0,1])
 assert center==(10624.0,-192.0)
 portals=[l for l in g['linedef'] if l.get('special')=='57' and l.get('arg1')=='6']
 assert len(portals)==4
 pair=[l for l in portals if l.get('id')=='1001']
 origins=[g['vertex'][int(l['v2'])] for l in pair]
 shift=tuple(float(origins[1][a])-float(origins[0][a]) for a in ['x','y'])
 assert shift==(10496.0,128.0)
 assert BEAM==(center[0]-shift[0],center[1]-shift[1],20000.0)
 down=np.asarray(Image.open(root/'tutnt/textures/URFD.png').convert('RGB'))
 assert not down.any(),'The static abyss must be black'
 return dict(ok=True,upper_beam_center=center,upper_beam_ceiling=20000,portal_translation=shift,unwrapped_beam_endpoint=BEAM,black_nadir=True)

if __name__=='__main__':print(json.dumps(verify(),indent=2))
