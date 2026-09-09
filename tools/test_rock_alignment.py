"""Focused algorithm regressions for continuity, branch cuts and patch preservation."""
import unittest,math
from expand_rock_walls import trails,patch,parse,excluded_sectors

def edge(line,a,b,lo=0,hi=1024):return dict(line=line,side=line,start=a,end=b,length=math.dist(a,b),tiers=[dict(lo=lo,hi=hi)])
class AlignmentTests(unittest.TestCase):
    def test_open_front_uses_true_length(self):
        e=[edge(0,(0,0),(3,4)),edge(1,(3,4),(8,4))]
        c=trails(e);self.assertEqual(len(c),1);self.assertEqual(sum(x['length'] for x in c[0][0]),10);self.assertIsNone(c[0][1])
    def test_branch_is_explicitly_split(self):
        c=trails([edge(0,(0,0),(10,0)),edge(1,(10,0),(20,0)),edge(2,(10,0),(20,5))])
        self.assertEqual(len(c),3)
    def test_vertically_disjoint_faces_do_not_merge(self):
        self.assertEqual(len(trails([edge(0,(0,0),(10,0),0,64),edge(1,(10,0),(20,0),128,256)])),2)
    def test_closed_loop_has_documented_corner(self):
        c=trails([edge(0,(0,0),(64,0)),edge(1,(64,0),(64,64)),edge(2,(64,64),(0,64)),edge(3,(0,64),(0,0))])
        self.assertEqual(len(c),1);self.assertEqual(c[0][1]['angle'],90)
    def test_patch_preserves_unrelated_scope(self):
        raw='vertex { x=0; y=1; }\nsidedef { sector=2; texturemiddle="QROCK3"; offsetx=17; }\nsidedef { sector=2; texturemiddle="QROCK3"; }'
        out=patch(raw,{'0':{'texturemiddle':'"QROCK3X8"','offsetx_mid':'3.0'}})
        a,_=parse(raw);b,_=parse(out)
        self.assertEqual(a['vertex'],b['vertex']);self.assertEqual(a['sidedef'][1],b['sidedef'][1]);self.assertEqual(b['sidedef'][0]['offsetx'],'17')
    def test_script_motion_and_unknown_argument(self):
        g={'linedef':[],'sidedef':[],'sector':[{}, {'id':'5'},{'id':'6'}]}
        excluded,meta=excluded_sectors(g,'Floor_LowerToLowest(5,20);',{})
        self.assertEqual(excluded,{1})
        excluded,meta=excluded_sectors(g,'Floor_LowerToLowest(tag,20);',{})
        self.assertEqual(excluded,{1,2});self.assertTrue(meta['unknown_motion_argument'])

if __name__=='__main__':unittest.main()
