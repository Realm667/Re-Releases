"""Real exits, saved ledgers and hub revisits in the unified transition system."""
import argparse,json,os
from pathlib import Path
from check_engine import ROOT,run_case

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--case',choices=['flow','hub','empty','fade','acs'],default='flow')
    p.add_argument('--language',default='en')
    p.add_argument('--renderer',default='1')
    p.add_argument('--width',type=int,default=960)
    p.add_argument('--height',type=int,default=540)
    p.add_argument('--scale',type=float,default=1)
    a=p.parse_args();label='transitions-'+a.case+'-'+a.language
    if a.case=='fade':
        commands=['wait 120','netevent trseed','wait 10','netevent trfade 1','wait 8',
          f'screenshot logs/{label}-out.png','netevent trfading','save tr-fade','wait 70',
          'load tr-fade','wait 3','netevent trfading','wait 240','netevent trcheck 20 20 0',
          'netevent utnt_chapter 4 1','wait 12','event trview',f'screenshot logs/{label}-chapter.png',
          'netevent utnt_chapter 3 1','wait 140','netevent trmap 2','netevent trreleased']
        mapname='TNT01'
    elif a.case=='acs':
        commands=['wait 120','netevent trseed','wait 10','netevent tracsexit','wait 15',
          'netevent trfading','wait 240','netevent trcheck 20 20 0',
          'netevent utnt_chapter 3 1','wait 140','netevent trmap 6']
        mapname='TNT03B'
    elif a.case=='flow':
        commands=['wait 100','netevent trdefs','netevent trseed','wait 10','netevent trverifylive 20',
          'save tr-before','wait 5','netevent tradd 7','wait 10','netevent trverifylive 27','wait 5',
          'netevent trdie','wait 10','netevent trdeaths 1','wait 5',
          'load tr-before','wait 15','netevent trdeaths 0','netevent trverifylive 20','netevent trexit','wait 240',
          'netevent trcheck 20 20 0','netevent utnt_chapter 4 1','wait 12','event trview',
          f'screenshot logs/{label}-chapter.png','save tr-board','wait 5','netevent utnt_chapter 4 1',
          'wait 12','load tr-board','wait 20','netevent trcheck 20 20 1',
          'netevent utnt_chapter 4 1','wait 12',f'screenshot logs/{label}-campaign.png',
          'netevent utnt_chapter 5 1','wait 130','netevent trmap 2',
          'netevent trseed','wait 12','netevent trexit','wait 240','netevent trcheck 20 40 0',
          'netevent utnt_chapter 3 1','wait 130','netevent trmap 3','wait 5','map TNT01','wait 100','netevent trreset','wait 5']
        mapname='TNT01'
    elif a.case=='hub':
        commands=['wait 120','netevent trseed','wait 10','netevent trverifylive 20',
          'netevent trtravel 4','wait 140','netevent trmap 4','netevent trseed','wait 10',
          'netevent trverifylive 20','netevent trtravel 3','wait 140','netevent trmap 3',
          'netevent trverifylive 20','netevent tradd 3','wait 10','netevent trverifylive 23',
          'netevent trtravel 99','wait 240','netevent trcheck 43 43 0',
          'netevent utnt_chapter 4 1','wait 15','event trview',f'screenshot logs/{label}.png',
          'netevent utnt_chapter 3 1','wait 130','netevent trmap 5']
        mapname='TNT03A1'
    else:
        commands=['wait 240','netevent utnt_chapter 4 1','wait 15','event trview',
          f'screenshot logs/{label}.png','netevent utnt_chapter 3 1','wait 130','netevent trmap 2']
        mapname='INTERMAP'
    commands=[f'vid_setsize {a.width} {a.height}','wait 5']+commands
    commands+=['echo UTNT_TEST_END','wait 5','quit']
    result=run_case(os.environ.get('UTNT_ENGINE','F:/DoomDev/uzdoom.exe'),
        os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'),mod=a.mod,
        addon=ROOT/'tools/fixtures/transitions',mapname=mapname,label=label,renderer=a.renderer,
        timeout=100,commands='; '.join(commands),settings=[('language',a.language),('wipetype',1),
        ('win_w',a.width+18),('win_h',a.height+47),('UTNT_uiscale',a.scale),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True)])
    if a.case=='fade':
        log=Path(result['log']).read_text(encoding='utf-8',errors='replace')
        result['ok'] = result['ok'] and 'UTNT_ASSERT PASS: load restores departure clock before travel' in log
    (ROOT/'tutnt/.codex/logs'/f'{label}-results.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['ok']:print(Path(result['log']).read_text()[-6500:])
    raise SystemExit(0 if result['ok'] else 1)

if __name__=='__main__':main()
