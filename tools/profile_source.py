"""Measure the Source finale in a fixed view, optionally using prior source materials.

Run sequentially with the same immutable full PK3 and renderer/settings. Results
include first-use stalls; no samples are trimmed. Work products stay in .codex.
"""
from pathlib import Path
import argparse,json,re,statistics,subprocess,tempfile
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('engine','iwad','mod','work'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--label',default='source-profile');p.add_argument('--renderer',choices=['0','1'],default='1')
 p.add_argument('--baseline-ref');p.add_argument('--shadows',choices=['true','false'],default='true')
 a=p.parse_args();work=a.work.resolve();work.mkdir(parents=True,exist_ok=True)
 if not re.fullmatch(r'[A-Za-z0-9_-]+',a.label):p.error('label must be a plain identifier')
 fixture_root=ROOT/'tutnt/.codex/work/source-performance'/a.label;fixture_root.mkdir(parents=True,exist_ok=True)
 fixture=Path(tempfile.mkdtemp(prefix='fixture-',dir=fixture_root))
 (fixture/'ZSCRIPT.txt').write_text((ROOT/'tools/source-tests/ZSCRIPT').read_text()+'\n'+(ROOT/'tools/source-profile/frames.zc').read_text())
 (fixture/'MAPINFO').write_text('GameInfo { AddEventHandlers = "UTNTSourceTests", "UTNTSourceFrameProfile" }\n')
 if a.baseline_ref:
  def git(*args):return subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','-C',str(ROOT),*args])
  ref=git('rev-parse','--verify',a.baseline_ref+'^{commit}').decode().strip()
  paths=['tutnt/zscript/UTNT_Source.zc','tutnt/GLDEFS.source','tutnt/TEXTURES.source']
  paths+=git('ls-tree','-r','--name-only',ref,'tutnt/shaders/sourcefx','tutnt/graphics/source-beam').decode().splitlines()
  for path in paths:
   dest=fixture/path[6:];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(git('show',ref+':'+path))
 r=run_case(a.engine,a.iwad,root=work,mod=a.mod,addon=fixture,mapname='TNT04CN',renderer=a.renderer,timeout=160,label=a.label,
  commands='wait 380; netevent sourceview 4; wait 100; netevent sourcekill; wait 248; echo UTNT_TEST_END; wait 3; quit',
  settings=[('win_w',1298),('win_h',767),('vid_maxfps',0),('vid_vsync','false'),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false'),('UTNT_shaderoverlayswitch','true'),('gl_lights','true'),('gl_light_shadowmap',a.shadows)])
 match=re.search(r'SOURCE_FRAME_MS ([0-9:.,]+)',Path(r['log']).read_text())
 r.update(renderer=a.renderer,shadows=a.shadows,baseline_ref=a.baseline_ref,phases={})
 if not match:r['ok']=False;r['errors'].append('missing frame measurements')
 else:
  samples=[(int(x.split(':')[0]),float(x.split(':')[1])) for x in match[1].strip(',').split(',')];r['samples']=samples
  for name,lo,hi in [('alive',0,1),('hold',1,35),('forming',35,70),('suction',70,158),('flash',158,193),('tail',193,245),('death',1,245)]:
   values=sorted(v for age,v in samples if lo<=age<hi)
   if values:r['phases'][name]={'n':len(values),'mean_ms':round(statistics.mean(values),3),'median_ms':statistics.median(values),'p95_ms':values[int((len(values)-1)*.95)],'max_ms':max(values),'frames_over_50ms':sum(v>50 for v in values)}
 (work/'profile.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['phases'],indent=2))
 return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
