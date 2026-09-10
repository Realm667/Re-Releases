"""Verify restored Doom-format assets, offsets, and optional packaged bytes.
Uses only the Python standard library. The manifest records the reviewed conversion.
"""
import argparse,hashlib,json,pathlib,struct,zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=pathlib.Path,default=ROOT)
    p.add_argument('--manifest',type=pathlib.Path,default=ROOT/'tools/fixtures/palette-restore/assets.json')
    p.add_argument('--pk3',type=pathlib.Path)
    args=p.parse_args();assets=json.loads(args.manifest.read_text(encoding='utf-8'))
    archive=zipfile.ZipFile(args.pk3) if args.pk3 else None
    try:
        for a in assets:
            path=args.root/a['lmp'];raw=path.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==a['sha256'],path
            assert not raw.startswith(b'\x89PNG\r\n\x1a\n'),path
            assert not (args.root/a['removed_png']).exists(),a['removed_png']
            w,h=a['width'],a['height']
            if '/flats/' in a['lmp']:assert len(raw)==w*h,path
            else:
                assert struct.unpack_from('<hhhh',raw)==(w,h,*a['offsets']),path
                for x in range(w):
                    off=struct.unpack_from('<I',raw,8+4*x)[0];top=-1
                    while raw[off]!=255:
                        delta,n=raw[off:off+2];top=top+delta if delta<=top else delta
                        assert 0<=top<=h and top+n<=h and off+n+4<=len(raw),path
                        off+=n+4
            if archive:
                name=a['lmp'].removeprefix('tutnt/');old=a['removed_png'].removeprefix('tutnt/')
                assert archive.read(name)==raw,name
                assert old not in archive.namelist(),old
        print(json.dumps({'ok':True,'assets':len(assets),'package_checked':bool(archive)}))
    finally:
        if archive:archive.close()

if __name__=='__main__':main()
