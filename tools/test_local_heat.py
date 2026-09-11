"""Geometry coverage and placement contracts for automatic lava heat."""
from pathlib import Path
import unittest
from build_local_heat import detect, parse, LAVA, distance_edge
from build_environment_fx import geometry, inside
ROOT=Path(__file__).resolve().parent.parent

class LocalHeatTests(unittest.TestCase):
 def test_placement_stays_on_eligible_geometry(self):
  total=0
  for path in (ROOT/'tutnt/maps').glob('*.wad'):
   b=parse(path);edges=geometry(b);rows=detect(b)
   self.assertEqual(len(rows),len({tuple(r) for r in rows}))
   for kind,index,part,texture,x,y,z,rx,ry,rz in rows:
    self.assertIn(texture,LAVA);self.assertGreater(min(rx,ry,rz),0)
    sector=index if kind==0 else int(b['sidedef'][index]['sector'])
    self.assertTrue(inside((x,y),edges[sector]),(path.name,index,x,y))
    if kind==0:
     margin=min(distance_edge((x,y),a,c) for a,c,*_ in edges[sector])
     self.assertLessEqual(rx,margin+.002)
    total+=1
  self.assertGreater(total,1000)
 def test_control_sectors_do_not_emit(self):
  b=parse(ROOT/'tools/fixtures/environment/maps/envtest.wad')
  b['sector'][13]['texturefloor']='"QLAVA"'
  rows=detect(b)
  self.assertFalse(any(row[0]==0 and row[1]==13 for row in rows))
  self.assertTrue(any(row[0]==0 and row[1]==3 for row in rows))
  self.assertTrue(any(row[0]==1 for row in rows))

if __name__=='__main__':unittest.main()
