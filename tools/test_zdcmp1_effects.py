"""Run ZDCMP1 lifecycle assertions with UZDoom 5.0.1+ and a Doom II IWAD.

Set UTNT_ENGINE and UTNT_IWAD, or pass --engine and --iwad. Freedoom 2 is
sufficient for these code checks; use Doom II for visual acceptance.
"""

import argparse
import os
from pathlib import Path
import struct
import tempfile
import zipfile

from check_engine import run_case

ROOT = Path(__file__).resolve().parent.parent


def fixture(path):
    text = 'namespace="ZDoom";\n'
    for x, y in [(-512, -512), (-512, 512), (512, 512), (512, -512)]:
        text += f'vertex {{ x={x}.0; y={y}.0; }}\n'
    text += 'sector { heightfloor=0; heightceiling=256; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }\n'
    for i in range(4):
        text += 'sidedef { sector=0; texturemiddle="STARTAN3"; }\n'
        text += f'linedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
    text += 'thing { x=-200.0; y=-64.0; type=1; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }\n'
    lumps = [(b'ZDCFTEST', b''), (b'TEXTMAP', text.encode()), (b'ENDMAP', b'')]
    data = bytearray()
    entries = bytearray()
    for name, content in lumps:
        entries += struct.pack('<II8s', 12 + len(data), len(content), name)
        data += content
    wad = struct.pack('<4sII', b'PWAD', len(lumps), 12 + len(data)) + data + entries
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('maps/zdcftest.wad', wad)
        for name in ('zscript.zc', 'mapinfo.txt'):
            source = ROOT / 'tools/zdcmp1-tests' / name
            archive.write(source, source.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', default=os.environ.get('UTNT_ENGINE'), required=not os.environ.get('UTNT_ENGINE'))
    parser.add_argument('--iwad', default=os.environ.get('UTNT_IWAD'), required=not os.environ.get('UTNT_IWAD'))
    parser.add_argument('--mod', type=Path, default=ROOT / 'zdcmp1')
    parser.add_argument('--renderer', choices=('0', '1'), default='1')
    args = parser.parse_args()
    commands = '''unbindall; wait 20; netevent zdcsetup; wait 30;
netevent zdclight; wait 5; netevent zdcoff; wait 10;
netevent zdclight; wait 5; netevent zdcoff; wait 10;
netevent zdcdestroy; netevent zdcladder; netevent zdcweather;
nashgore_maxgore 8; netevent zdcgore; wait 35; netevent zdccount 8;
ZDCMP1_fxquality 1; wait 35; netevent zdccount 4;
ZDCMP1_fxquality 0; wait 35; netevent zdccount 2;
nashgore_maxgore 0; wait 35; netevent zdccount 0;
nashgore_maxgore -1; netevent zdcgore; wait 35; netevent zdccount 0;
ZDCMP1_fxquality 2; nashgore_maxgore 8; netevent zdcgore; wait 35; netevent zdccount 8;
netevent zdcsmokemark; wait 35; netevent zdcsmoke 1;
ZDCMP1_shaderoverlayswitch false; wait 10; netevent zdcheat; netevent zdcsmokemark; wait 35; netevent zdcsmoke 0;
netevent zdcreplacesmoke; wait 20; netevent zdcsmokemark; wait 35; netevent zdcsmoke 0;
ZDCMP1_shaderoverlayswitch true; netevent zdcsmokemark; wait 35; netevent zdcsmoke 1;
netevent zdcrange 10; wait 10; netevent zdcsmokemark; wait 35; netevent zdcsmoke 0;
netevent zdcrange 1200; netevent zdcsmokemark; wait 35; netevent zdcsmoke 1;
save zdcmp1-effects; wait 10; ZDCMP1_shaderoverlayswitch false; wait 10;
load zdcmp1-effects; wait 30; ZDCMP1_shaderoverlayswitch false; wait 10;
netevent zdcsmokemark; wait 35; netevent zdcsmoke 0;
ZDCMP1_shaderoverlayswitch true; netevent zdcsmokemark; wait 35; netevent zdcsmoke 1;
motionblur_samples -1; +left; wait 10; motionblur_samples 999; wait 10; event zdcblur 1; -left;
motionblur false; wait 10; event zdcblur 0; motionblur true; wait 10; netevent zdcnetwork; wait 5;
echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit
'''
    with tempfile.TemporaryDirectory(prefix='zdcmp1-tests-') as directory:
        addon = Path(directory) / 'tests.pk3'
        fixture(addon)
        result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon,
                          mapname='ZDCFTEST', playerclass='ZDCMPPlayer',
                          renderer=args.renderer, label='zdcmp1-effects-' + args.renderer,
                          commands=' '.join(commands.splitlines()) + '\n', regression=True, timeout=90,
                          settings=[('use_mouse', False), ('use_joystick', False),
                                    ('i_pauseinbackground', False),
                                    ('vid_activeinbackground', True)])
    if not result['ok'] or result['assertions'] != 34:
        print(Path(result['log']).read_text()[-10000:])
        raise SystemExit(1)


if __name__ == '__main__':
    main()
