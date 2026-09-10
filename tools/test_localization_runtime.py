"""Verify actual engine localization, font coverage and layouts in all locales.

Generated expectations come from the reviewed LANGUAGE files, not an English
fallback. Tests use a separate temporary addon and separate game configuration.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from check_localization import ROOT, LANGUAGES, COLOR, catalogs
from check_engine import run_case

def fixture(root, directory):
    catalog=catalogs(root)
    blocks=['version "5.0"', 'class UTNTLocalizationTest : StaticEventHandler {',
      'ui void Check(bool ok,String label) { Console.Printf("UTNT_ASSERT %s: %s",ok?"PASS":"FAIL",label); }',
      'ui void Expect(String key,String expected,String plain) {',
      ' String actual=StringTable.Localize("$"..key);',
      ' Check(actual==expected,"lookup "..key);',
      ' Check(AlternativeSmallFont.CanPrint(plain,false),"glyphs "..key);',
      '}',
      'override void ConsoleProcess(ConsoleEvent e) {',
      ' if(e.Name=="loccredits") {',
      ' let h=UTNTCreditsHandler(EventHandler.Find(\'UTNTCreditsHandler\'));Check(h && h.Initialized,"credits initialized");if(!h)return;',
      ' for(int n=0;n<h.Pages.Size();n++) { let page=h.Pages[n];let view=new("UTNTCreditsUI");view.Prepare(page);',
      ' for(int i=0;i<page.Contributions.Size();i++) { String value=StringTable.Localize(page.Contributions[i]);Check(value.Left(1)!="$","credit contribution resolved");',
      ' if(page.Layout=="creator") Check(123+view.Wrapped[i].Count()*13<=164,"creator text fits");',
      ' else if(page.Layout=="thanks") Check(60+view.Wrapped[i].Count()*18<=108,"thanks text clears signature");',
      ' else Check(view.Tops[page.Layout=="dense"?i%3:i]+view.Heights[i]<=672,"credit card fits"); }',
      ' Check(StringTable.Localize(page.Heading).Left(1)!="$","credit heading resolved");',
      ' } Console.Printf("UTNT_REGRESSION_COMPLETE");return; }',
      ' if(e.Name=="locmenu") { Menu.SetMenu(e.Args[0]==0?\'PlayerclassMenu\':e.Args[0]==1?\'UTNTOptions\':\'MainMenu\'); return; }',
      ' if(e.Name=="locclose") { if(Menu.GetCurrentMenu()) Menu.GetCurrentMenu().MenuEvent(Menu.MKEY_Back,false); return; }',
      ' if(e.Name!="loccheck") return;']
    methods=[]
    for index,lang in enumerate(LANGUAGES):
        rows=list(catalog[lang].items())
        for chunk in range(0,len(rows),50):
            method=f'Locale{index}Part{chunk//50}'
            blocks.append(f' if(e.Args[0]=={index}) {method}();')
            methods.append('ui void '+method+'() {')
            for key,value in rows[chunk:chunk+50]:
                if key=='UTNT_BUILD_INFO':continue # generated build provenance overrides source label
                plain=COLOR.sub('',value).replace(r'\n',' ').replace(r'\t',' ')
                methods.append(f' Expect("{key}","{value}","{plain}");')
            methods.append('}')
    blocks += [
      ' let font=AlternativeSmallFont;',
      ' String cards[]={"RAGE","REGEN","WEAK","CLOAK","OVERDRIVE","BULWARK"};',
      ' for(int n=0;n<6;n++) { let lines=font.BreakLines(StringTable.Localize("$UTNT_AB_CARD_"..cards[n]),210); Check(lines.Count()<=4,"ability fits "..cards[n]); }',
      ' String foot[]={"TIMING","EXCLUSIVE","LOCK"};',
      ' for(int n=0;n<3;n++) Check(font.StringWidth(StringTable.Localize("$UTNT_AB_CARD_"..foot[n]))<=212,"ability footer fits "..foot[n]);',
      ' Check(font.StringWidth(String.Format(StringTable.Localize("$UTNT_CLASS_SPEED"),150))*1.15<=212,"class speed fits");',
      ' for(int n=1;n<=10;n++) { let chapter=new("UTNTChapterState");chapter.Init(n,0);let view=new("UTNTChapterUI");view.Prepare(chapter);',
      ' Check(view.BodyX>=0 && view.BodyY+view.BodyHeight<Screen.GetHeight(),"chapter layout "..n);',
      ' Check(view.PageCount>=1 && view.PageCount<=128,"chapter pagination "..n); }',
      ' Console.Printf("UTNT_REGRESSION_COMPLETE");','}']
    blocks+=methods+['}']
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'ZSCRIPT.localization').write_text('\n'.join(blocks)+'\n',encoding='utf-8')
    (directory/'MAPINFO').write_text('gameinfo { AddEventHandlers = "UTNTLocalizationTest" }\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE',str(ROOT/'engine/uzdoom.exe')))
    p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD',r'F:\DoomDev\DOOM2.WAD'))
    p.add_argument('--overlay',action='store_true',help='Preview the supplied root catalogs over the base package')
    p.add_argument('--output',type=Path,default=ROOT/'tutnt/.codex/validation/localization-2026-09-10')
    p.add_argument('--languages',nargs='+',default=list(LANGUAGES),choices=LANGUAGES)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);results=[]
    with tempfile.TemporaryDirectory(prefix='utnt-localization-') as temp:
        addon=Path(temp);fixture(a.root,addon)
        if a.overlay:
            for source in (a.root/'tutnt').glob('LANGUAGE*'):shutil.copyfile(source,addon/source.name)
            shutil.copyfile(a.root/'tutnt/MENUDEF.txt',addon/'MENUDEF.txt')
            shutil.copytree(a.root/'tutnt/zscript',addon/'zscript',dirs_exist_ok=True)
            shutil.copytree(a.root/'tutnt/credits',addon/'credits',dirs_exist_ok=True)
        compiled=run_case(a.engine,a.iwad,root=a.output,mod=a.mod,addon=addon,label='localization-compile',timeout=15)
        if not compiled['ok']:
            print(Path(compiled['log']).read_text(encoding='utf-8')[-6000:]);raise SystemExit(1)
        for lang in a.languages:
            label='localization-'+lang
            commands=['wait 70',f'event loccheck {LANGUAGES.index(lang)}','wait 5',
                'event locmenu 0','wait 8',f'screenshot logs/{label}-classes.png','wait 3','event locclose',
                'event locmenu 1','wait 8',f'screenshot logs/{label}-options.png','wait 3','event locclose',
                'event locmenu 2','wait 8',f'screenshot logs/{label}-main.png','wait 3','event locclose',
                'echo UTNT_TEST_END','wait 3','quit']
            result=run_case(a.engine,a.iwad,root=a.output,mod=a.mod,addon=addon,mapname='TNT01',
                label=label,commands='; '.join(commands),timeout=50,regression=True,
                settings=[('language',lang),('con_notifytime',0),('vid_activeinbackground',True),
                          ('i_pauseinbackground',False),('win_w',978),('win_h',767)])
            results.append(result)
            (a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
            if not result['ok']:
                lines=Path(result['log']).read_text(encoding='utf-8').splitlines()
                print('\n'.join(s for s in lines if 'FAIL' in s or 'error' in s.lower())[-8000:])
            label='localization-credits-'+lang
            commands=['wait 70','event loccredits','netevent utnt_credit 0','wait 40',
                f'screenshot logs/{label}-creator.png','netevent utnt_credit 0','wait 40',
                f'screenshot logs/{label}-dense.png','echo UTNT_TEST_END','wait 3','quit']
            result=run_case(a.engine,a.iwad,root=a.output,mod=a.mod,addon=addon,mapname='ENDMAP01',
                label=label,commands='; '.join(commands),timeout=50,regression=True,
                settings=[('language',lang),('con_notifytime',0),('vid_activeinbackground',True),
                          ('i_pauseinbackground',False),('win_w',978),('win_h',767)])
            results.append(result)
            (a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
            if not result['ok']:
                lines=Path(result['log']).read_text(encoding='utf-8').splitlines()
                print('\n'.join(s for s in lines if 'FAIL' in s)[-3000:])
        if any(not result['ok'] for result in results):raise SystemExit(1)
if __name__=='__main__':main()
