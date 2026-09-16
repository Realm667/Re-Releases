"""Review/apply strictly verified PNGCrush -> PNGOUT -> DeflOpt compression.

Production files are changed only with --apply-report. All working files and
original-byte backups stay in tutnt/.codex. No optimizer binary is distributed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import zlib
from zipfile import ZipFile, ZIP_STORED
from PIL import Image
from build_utnt import ROOT, input_files
from png_storage import chunks, decoded, encode, equivalent, normalized, restore_chunks


def sha(data): return hashlib.sha256(data).hexdigest()
def packed_size(data):
    compressor = zlib.compressobj(6, zlib.DEFLATED, -15)
    return len(compressor.compress(data) + compressor.flush())
def save_report(path, report):
    path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

def optimize_one(original, work, plugins, timeout):
    key = sha(original); folder = work/(key+'-'+uuid.uuid4().hex); folder.mkdir(parents=True, exist_ok=True)
    parts = chunks(original); original_pixels = decoded(original)
    best = original; stages = []; warnings = []
    def accept(data, stage):
        nonlocal best
        data = restore_chunks(original, data)
        if len(data) >= len(best): return
        if not equivalent(original, data):
            raise ValueError(stage+': changed pixels or ancillary data')
        if packed_size(data) > packed_size(original): return
        best = data; stages.append(stage)
    # A merged IDAT stream and corrected CRCs alone can already save bytes.
    accept(normalized(original), 'container')
    source = folder/'input.png'; source.write_bytes(normalized(original))
    header = parts[0][1]; depth, color = header[8], header[9]
    # Preserve palette indices and grayscale representation (alPh/shader users).
    # An entirely opaque alpha channel may be removed if no dependent chunks exist.
    blocked = {b'tRNS',b'PLTE',b'bKGD',b'sBIT',b'hIST',b'alPh'}
    if color in (4,6) and not any(k in blocked for k,_,_ in parts):
        with Image.open(source) as im:
            if im.getchannel('A').getextrema() == (255,255):
                out = io.BytesIO(); im.convert('RGB' if color == 6 else 'L').save(out,format='PNG',compress_level=9)
                accept(out.getvalue(), 'opaque-alpha')
    def run(name, arguments, output):
        try:
            proc = subprocess.run([str(plugins/(name+'.exe')), *map(str,arguments)],
                cwd=folder, capture_output=True, timeout=timeout,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if output.exists():
                try: accept(output.read_bytes(), name)
                except (ValueError,OSError) as exc: warnings.append(str(exc))
            elif proc.returncode not in (0,2):
                warnings.append(name+': '+(proc.stderr+proc.stdout).decode('utf-8','replace')[-400:])
        except subprocess.TimeoutExpired:
            warnings.append(name+': timed out after '+str(timeout)+'s')
    source.write_bytes(normalized(best))
    run('pngcrush', ['-q','-noreduce','-brute',source,folder/'crush.png'], folder/'crush.png')
    source.write_bytes(normalized(best))
    header = chunks(best)[0][1]; depth,color=header[8],header[9]
    run('pngout', [source,folder/'out.png','/q','/y','/k1','/kp','/c'+str(color),'/d'+str(depth)],folder/'out.png')
    output = folder/'defl.png';output.write_bytes(normalized(best))
    run('deflopt', ['/sf',output], output)
    result = dict(before_sha256=key,after_sha256=sha(best),before=len(original),after=len(best),
                  packed_before=packed_size(original),packed_after=packed_size(best),stages=stages,warnings=warnings,
                  crc_errors=[k.decode() for k,v,valid in parts if not valid],
                  rgba_sha256=sha(original_pixels[1]),size=list(original_pixels[0]))
    if len(best) < len(original):
        output = work/(key+'.png');output.write_bytes(best);result['candidate']=output.as_posix()
    # Only known task-owned leaves, never recursive deletion or user paths.
    for p in folder.iterdir():
        if p.name in ('input.png','crush.png','out.png','defl.png'):p.unlink()
    folder.rmdir()
    return result

def manifest_updates(root, rows):
    """Update only hashes tied to verified changed production images.

    Historical reference/source hashes remain unchanged. Unrelated stale manifest
    fields are not blessed by this operation.
    """
    by_path = {r['path']:r for r in rows if 'candidate' in r}
    updates = {}
    def load(name): return json.loads((root/name).read_text(encoding='utf-8'))
    def update(record, key, name):
        row = by_path.get(name)
        if row and record.get(key) == row['before_sha256']:
            record[key] = row['after_sha256']
    def save(name, data):
        encoded = (json.dumps(data, indent=2)+'\n').encode()
        if encoded != (root/name).read_bytes(): updates[name] = encoded
    for name, prefix in [('tools/organic-materials/generated.json',''),
                         ('tools/artwork/brightmaps/custom-manifest.json','tutnt/')]:
        data = load(name)
        for section in ('inputs','outputs'):
            for path in data[section]:
                update(data[section], path, prefix+path if section=='outputs' else path)
        save(name,data)
    name='tools/font-glyphs.json'; data=load(name)
    for font,record in data['fonts'].items():
        for code,glyph in record['glyphs'].items():
            update(glyph,'sha256',f'tutnt/fonts/{font}/{code}.png')
    save(name,data)
    name='tools/asset-consolidation.json';data=load(name)
    for row in data['duplicates']:update(row,'sha256','tutnt/'+row['canonical'])
    save(name,data)
    name='tools/fixtures/png-blue.json';data=load(name)
    for row in data['assets']:update(row,'result_sha256',row['path'])
    save(name,data)
    name='tools/brightmap-reference.json';data=load(name)
    for row in data['bindings']:
        if row.get('map'):update(row,'map_sha256','tutnt/'+row['map'])
        if row.get('base'):update(row['base'],'sha256',row['base']['path'])
    for row in data['preserved']:update(row['map'],'sha256',row['map']['path'])
    save(name,data)
    name='tools/alternate-deaths.json';data=load(name)
    for row in data['assets']:
        previous=row['sha256'];update(row,'sha256',row['target'])
        if row['sha256'] != previous:row.setdefault('source_sha256',previous)
    save(name,data)
    return updates

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plugins',type=Path,default=Path('F:/DoomDev/Tools/Slade3 v3.2.1/plugins'))
    p.add_argument('--workers',type=int,default=12);p.add_argument('--timeout',type=int,default=180)
    p.add_argument('--apply-report',type=Path);p.add_argument('--limit',type=int)
    p.add_argument('--run-name', help='Unique name for retained backup and report files')
    a=p.parse_args();root=ROOT.resolve();work=root/'tutnt/.codex/work/png-optimization';work.mkdir(parents=True,exist_ok=True)
    if a.apply_report:
        report=json.loads(a.apply_report.read_text(encoding='utf-8')); applied=[]
        if report['errors']:raise ValueError('Resolve report errors before applying PNGs')
        # Validate the entire reviewed set and recovery archive before first write.
        with ZipFile(report['backup']) as backup:
            for row in report['files']:
                if 'candidate' not in row:continue
                path=(root/row['path']).resolve();path.relative_to(root/'tutnt')
                candidate=Path(row['candidate']).resolve();candidate.relative_to(work)
                before=path.read_bytes();after=candidate.read_bytes()
                assert sha(before)==row['before_sha256'], 'Concurrent edit: '+row['path']
                assert backup.read(row['path'])==before
                assert sha(after)==row['after_sha256'] and len(after)<len(before)
                assert equivalent(before,after), row['path']
                assert packed_size(after)<=packed_size(before), row['path']
                applied.append((path,after,row['before_sha256']))
        updates=manifest_updates(root,report['files'])
        metadata_backup=work/'manifest-before'/a.apply_report.stem
        metadata_backup.mkdir(parents=True,exist_ok=True)
        for name in updates:
            target=metadata_backup/name
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes((root/name).read_bytes())
        for path,after,expected in applied:
            if sha(path.read_bytes())!=expected:raise ValueError('Concurrent edit: '+str(path))
            temporary=work/('apply-'+uuid.uuid4().hex+'.png')
            try:
                temporary.write_bytes(after)
                os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        for name,data in updates.items():(root/name).write_bytes(data)
        print(json.dumps({'applied':len(applied),'saved':sum(r['before']-r['after'] for r in report['files'])}))
        return
    for name in ('pngcrush','pngout','deflopt'):
        if not (a.plugins/(name+'.exe')).is_file():raise FileNotFoundError(name)
    files=[p for p in input_files(root) if p.suffix.lower()=='.png']
    files.sort(key=lambda p:p.stat().st_size,reverse=True)
    if a.limit:files=files[:a.limit]
    label=a.run_name or ('pilot' if a.limit else 'all')
    if not label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in label):
        raise ValueError('Run name must contain only letters, digits, dash or underscore')
    backup=root/('tutnt/.codex/backups/png-optimization-'+label+'.zip')
    if backup.exists():raise FileExistsError('Use a new run after preserving existing evidence: '+str(backup))
    groups={}; report=dict(schema=1,backup=backup.as_posix(),tools={},files=[],errors=[])
    for name in ('pngcrush','pngout','deflopt'):
        exe=a.plugins/(name+'.exe');report['tools'][name]={'path':exe.as_posix(),'sha256':sha(exe.read_bytes())}
    with ZipFile(backup,'w',ZIP_STORED) as z:
        for path in files:
            data=path.read_bytes();name=path.relative_to(root).as_posix();z.writestr(name,data)
            key=sha(data)
            if key not in groups:groups[key]=[data,[]]
            groups[key][1].append(name)
    start=time.monotonic();total=len(groups)
    destination=root/('tutnt/.codex/validation/png-optimization-'+label+'.json')
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        tasks={pool.submit(optimize_one,data,work,a.plugins.resolve(),a.timeout):names for data,names in groups.values()}
        for done,future in enumerate(as_completed(tasks),1):
            names=tasks[future]
            try:
                result=future.result()
                report['files'].extend(dict(result,path=name) for name in names)
            except Exception as exc:
                report['errors'].append({'paths':names,'error':str(exc)})
            if done%20==0 or done==total:
                save_report(destination,report)
                print(json.dumps({'done':done,'total':total,'seconds':round(time.monotonic()-start),
                    'changed':sum('candidate' in r for r in report['files']),
                    'saved':sum(r['before']-r['after'] for r in report['files']),'errors':len(report['errors'])}),flush=True)
    report['seconds']=round(time.monotonic()-start);save_report(destination,report)
    print(str(destination))

if __name__=='__main__':main()
