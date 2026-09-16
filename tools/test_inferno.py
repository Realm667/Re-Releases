"""TNT04B inferno structure and engine/save-load checks. No source regeneration."""
from pathlib import Path
import argparse,json
from test_caldera_structure import parse
from check_engine import run_case
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True);p.add_argument('--mod',type=Path);p.add_argument('--renderer',default='1');a=p.parse_args()
 l,g=parse(ROOT/'tutnt/maps/tnt04b.wad');assert [len(g[k]) for k in ('vertex','linedef','sidedef','sector')]==[19506,29567,55102,10625]
 assert len([t for t in g['thing'] if 25200<=int(t['type'])<25300])==83
 assert len([t for t in g['thing'] if 25300<=int(t['type'])<25400])==83
 assert len([t for t in g['thing'] if int(t['type'])==25400])==71
 assert g['linedef'][-4]['special']=='209' and g['linedef'][-4]['arg1']=='34'
 assert [i for i,s in enumerate(g['sector']) if s.get('moreids')=='"64123"']==[1463,2227]
 assert all(g['sector'][i]['lightcolor']=='15911343' for i in (1463,2227))
 assert l['SCRIPTS'].find(b'sector_setfade(23, 255, 120, 0);')<0
 for i in (1449,1450):assert g['sector'][i]['texturefloor']=='"UFID"' and g['sector'][i]['textureceiling']=='"UFIU"'
 cmd='wait 140; netevent infernocheck; wait 8; save inferno-test; wait 8; load inferno-test; wait 105; netevent infernocheck; wait 8; echo UTNT_TEST_END; quit'
 result=run_case(a.engine,a.iwad,root=ROOT/'tutnt/.codex',mod=a.mod or ROOT/'tutnt',addon=ROOT/'tools/fixtures/inferno',mapname='TNT04B',renderer=a.renderer,label='inferno-runtime-'+a.renderer,timeout=90,commands=cmd,settings=[('use_mouse','false'),('use_joystick','false'),('i_pauseinbackground','false'),('vid_activeinbackground','true')])
 out=ROOT/'tutnt/.codex/validation/tnt04b-inferno-finish';out.mkdir(parents=True,exist_ok=True)
 (out/('runtime-'+a.renderer+('-package' if a.mod else '')+'.json')).write_text(json.dumps(result,indent=2))
 assert result['ok'] and result['assertions']==18,Path(result['log']).read_text()[-4500:]
if __name__=='__main__':main()
