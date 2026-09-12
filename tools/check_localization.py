"""Check every UTNT translation before packaging (Python standard library only).

After reviewing translations for changed English text, run --accept-reviewed.
This records source/translation fingerprints; it never fills missing translations.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('en', 'de', 'es', 'fr')
ALIASES = {'enu': 'en', 'default': 'en', 'deu': 'de', 'esp': 'es', 'fra': 'fr'}
TOKEN = re.compile(r'\s+|//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_][\w-]*|[\[\]=;]')
COLOR = re.compile(r'\\c(?:\[[^\]]+\]|[A-Za-z+*!=~-])')
PLACEHOLDER = re.compile(r'%%|%[-+0#]*\d*(?:\.\d+)?[diufseoxghkr]|\{[A-Za-z_]\w*\}')
ESCAPE = re.compile(r'\\(?:c(?:\[[^\]]+\]|[A-Za-z+*!=~-])|[nrt"\\])')

def parse(text, source='<text>'):
    tokens=[]; pos=0
    while pos < len(text):
        match=TOKEN.match(text,pos)
        if not match:
            raise ValueError(f'{source}: invalid syntax near {text[pos:pos+60]!r}')
        token=match.group(); pos=match.end()
        if not token.isspace() and not token.startswith(('//','/*')): tokens.append(token)
    result={lang:{} for lang in LANGUAGES}; section=[]; i=0
    while i<len(tokens):
        if tokens[i]=='[':
            i+=1; section=[]
            while i<len(tokens) and tokens[i]!=']':
                lang=ALIASES.get(tokens[i],tokens[i])
                if lang not in LANGUAGES: raise ValueError(f'{source}: unsupported language {lang}')
                if lang not in section: section.append(lang)
                i+=1
            if not section or i==len(tokens): raise ValueError(f'{source}: invalid language section')
            i+=1; continue
        if not section: raise ValueError(f'{source}: entry outside language section')
        key=tokens[i];i+=1
        if i>=len(tokens) or tokens[i]!='=': raise ValueError(f'{source}: expected = after {key}')
        i+=1; values=[]
        while i<len(tokens) and tokens[i].startswith('"'):
            values.append(tokens[i][1:-1]);i+=1
        if not values or i>=len(tokens) or tokens[i]!=';': raise ValueError(f'{source}: invalid value for {key}')
        i+=1
        for lang in section:
            if key in result[lang]: raise ValueError(f'{source}: duplicate {lang}/{key}')
            result[lang][key]=''.join(values)
    return result

def catalogs(root, pk3=None):
    if pk3:
        with zipfile.ZipFile(pk3) as archive:
            files={n:archive.read(n).decode('utf-8-sig') for n in archive.namelist()
                   if '/' not in n and n.upper().startswith('LANGUAGE')}
    else:
        folder=Path(root)/'tutnt/language'
        if not folder.is_dir(): folder=Path(root)/'tutnt'
        files={p.name:p.read_text(encoding='utf-8-sig') for p in sorted(folder.glob('LANGUAGE*'))}
    result={lang:{} for lang in LANGUAGES}
    for name,text in files.items():
        parsed=parse(text,name)
        if name=='LANGUAGE.zzbuild':
            if not pk3: raise ValueError('LANGUAGE.zzbuild is reserved for generated package metadata')
            for lang in LANGUAGES:
                if set(parsed[lang])!={'UTNT_BUILD_INFO'}: raise ValueError(f'Build metadata missing {lang}')
            continue
        for lang in LANGUAGES:
            overlap=result[lang].keys() & parsed[lang].keys()
            if overlap: raise ValueError(f'{name}: duplicate {lang}: {sorted(overlap)}')
            result[lang].update(parsed[lang])
    return result

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def fingerprints(catalog):
    return {key:{lang:digest(catalog[lang][key]) for lang in LANGUAGES} for key in sorted(catalog['en'])}

def references(root, english):
    errors=[]
    paths=[]
    for folder,dirs,names in os.walk(Path(root)/'tutnt'):
        dirs[:]=[name for name in dirs if not name.startswith('.') and name not in ('tools','#PSD')]
        paths.extend(Path(folder)/name for name in names if Path(name).suffix.lower() in ('.zc','.zs','.acs','.txt'))
    for path in paths:
        text=path.read_text(encoding='utf-8-sig',errors='replace')
        text='\n'.join(line for line in text.splitlines() if not line.lstrip().startswith(('//','#')))
        keys=set(re.findall(r'"\$(UTNT_[A-Z0-9_]+)"',text))
        keys.update(re.findall(r'\bLocal\(\s*"(UTNT_[A-Z0-9_]+)"\s*\)',text))
        for key in sorted(keys-english.keys()):errors.append(f'{path.name}: undefined localization key {key}')
        if path.parent.name=='credits':
            for line in text.splitlines():
                if not line.startswith(('P|','N|')):continue
                columns=line.split('|');index=4 if columns[0]=='P' else 2
                if len(columns)<=index:errors.append(f'{path}: invalid credit record');continue
                value=columns[index]
                if value and (not value.startswith('$') or value[1:] not in english):
                    errors.append(f'{path}: credit text must reference a translated LANGUAGE key: {value}')
    return errors

def validate(root=ROOT, *, pk3=None, accept_reviewed=False):
    root=Path(root); data=catalogs(root,pk3); errors=[]; english=data['en']
    if not english: errors.append('English catalog is empty')
    for lang in LANGUAGES:
        missing=english.keys()-data[lang].keys(); extra=data[lang].keys()-english.keys()
        if missing: errors.append(f'{lang}: missing keys: '+', '.join(sorted(missing)))
        if extra: errors.append(f'{lang}: orphan keys: '+', '.join(sorted(extra)))
        for key,text in data[lang].items():
            if not text.strip(): errors.append(f'{lang}/{key}: empty value')
            if '\ufffd' in text or any(s in text for s in ('Ã','Â\u00a0','â€')): errors.append(f'{lang}/{key}: damaged UTF-8')
            if '\\' in ESCAPE.sub('',text): errors.append(f'{lang}/{key}: unknown escape sequence')
            if key not in english: continue
            if Counter(PLACEHOLDER.findall(text))!=Counter(PLACEHOLDER.findall(english[key])):
                errors.append(f'{lang}/{key}: placeholder mismatch')
            if Counter(COLOR.findall(text))!=Counter(COLOR.findall(english[key])):
                errors.append(f'{lang}/{key}: color-code mismatch')
            if text.count(r'\n')!=english[key].count(r'\n'):
                errors.append(f'{lang}/{key}: explicit line-break mismatch')
            if key.startswith('UTNT_INTERMAP_') and bool(re.search(r'\\n$',text))!=bool(re.search(r'\\n$',english[key])):
                errors.append(f'{lang}/{key}: lost story join separator')
    if errors: raise ValueError('\n'.join(errors))
    if not pk3:
        errors=references(root,english)
        if errors:raise ValueError('\n'.join(errors))
    review=root/'tools/localization-review.json'; current=fingerprints(data)
    if accept_reviewed:
        if pk3: raise ValueError('Review source files, not a built package')
        review.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif not review.exists():
        raise ValueError('Missing localization-review.json; review all four catalogs')
    else:
        previous=json.loads(review.read_text(encoding='utf-8'))
        changed=[key for key in sorted(current.keys()|previous.keys()) if current.get(key)!=previous.get(key)]
        if changed: raise ValueError('Translation review required (all four languages): '+', '.join(changed))
    return {'languages':{lang:len(data[lang]) for lang in LANGUAGES},'reviewed':True,'package':str(pk3) if pk3 else None}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--pk3',type=Path)
    parser.add_argument('--accept-reviewed',action='store_true')
    args=parser.parse_args()
    try:
        result=validate(args.root,pk3=args.pk3,accept_reviewed=args.accept_reviewed)
        from check_font_coverage import validate as validate_fonts
        result["fonts"]=validate_fonts(args.root,args.pk3)
        print(json.dumps(result,indent=2))
    except (ValueError,UnicodeError) as error: parser.exit(1,f'Localization check failed:\n{error}\n')

if __name__=='__main__': main()
