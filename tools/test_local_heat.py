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
    sector=index if kind in (0,2) else int(b['sidedef'][index]['sector'])
    self.assertTrue(inside((x,y),edges[sector]),(path.name,index,x,y))
    if kind in (0,2):
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

 def test_tnt02_first_lake_uses_visible_3d_floor(self):
  b=parse(ROOT/'tutnt/maps/tnt02.wad');rows=detect(b)
  lake=[r for r in rows if r[0]==2 and r[1]==46]
  self.assertGreater(len(lake),0)
  self.assertTrue(all(float(b['sector'][r[2]]['heightceiling'])==-512 for r in lake))
  self.assertTrue(any(r[7]>250 for r in lake),'large lake needs broad plumes')
  self.assertNotIn(b['sector'][46]['texturefloor'].strip('"'),LAVA)

 def test_3d_floor_tags_and_invisible_controls(self):
  b=parse(ROOT/'tools/fixtures/environment/maps/envtest.wad')
  b['sector'][13]['textureceiling']='"QLAVA"'
  rows=detect(b);tops=[r for r in rows if r[0]==2]
  self.assertEqual({r[1] for r in tops},{9,14})
  self.assertTrue(all(r[2]==13 for r in tops))
  for line in b['linedef']:
   if int(line.get('special',0))==160 and int(line.get('arg0',0))==90:line['arg3']='0'
  self.assertFalse(any(r[0]==2 for r in detect(b)))

if __name__=='__main__':unittest.main()
