"""Real 3D-floor, height-transfer and portal fixtures for weather fallback checks."""
import argparse
import os
from pathlib import Path
import tempfile
import zipfile

from build_utnt import write_wad
from check_engine import ROOT, run_case


def geometry(linked=False):
    parts = ['namespace="ZDoom";']
    vertices = sides = 0

    def room(index, x, floor=0, ceiling=256, tag=0, specials=(), texture="FLAT5_4"):
        nonlocal vertices, sides
        ceiling_texture = "QLAVA" if texture == "QLAVA" else "CEIL1_1"
        parts.append(f'sector {{ heightfloor={floor}; heightceiling={ceiling}; texturefloor="{texture}"; textureceiling="{ceiling_texture}"; lightlevel=192; id={tag}; }}')
        for dx, y in ((-512, -512), (-512, 512), (512, 512), (512, -512)):
            parts.append(f'vertex {{ x={x+dx}.0; y={y}.0; }}')
        for i in range(4):
            parts.append(f'sidedef {{ sector={index}; texturemiddle="STARTAN3"; }}')
            extra = specials[i] if i < len(specials) else ""
            parts.append(f'linedef {{ v1={vertices+i}; v2={vertices+(i+1)%4}; sidefront={sides+i}; blocking=true; {extra} }}')
        vertices += 4
        sides += 4

    if linked:
        room(0, 0, tag=10, specials=(
            "special=57; arg0=10; arg1=6; arg2=0; arg3=0; arg4=255;",
            "special=57; arg0=11; arg1=6; arg2=1; arg3=1;"))
        room(1, 2048, floor=-256, ceiling=0, tag=11, specials=(
            "special=57; arg0=10; arg1=6; arg2=0; arg3=1;",
            "special=57; arg0=11; arg1=6; arg2=1; arg3=0; arg4=255;"))
    else:
        room(0, 0)
        room(1, 2048, tag=55)
        room(2, 4096, tag=56)
        room(3, 6144, tag=57, specials=("special=57; arg0=57; arg1=0; arg2=0; arg3=0; arg4=255;",))
        room(4, 8192, floor=64, ceiling=128, texture="QLAVA",
             specials=("special=160; arg0=55; arg1=1; arg3=255;",))
        room(5, 10240, floor=64, ceiling=192, specials=("special=209; arg0=56;",))
        room(6, 12288, floor=-256, ceiling=0,
             specials=("special=57; arg0=57; arg1=0; arg2=0; arg3=1;",))
    flags = "skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true;"
    for i in range(2):
        parts.append(f'thing {{ x={-200+i*128}.0; y=0.0; type={i+1}; {flags} }}')
    return write_wad(b"PWAD", [(b"ZDCEDGE", b""), (b"TEXTMAP", "\n".join(parts).encode()), (b"ENDMAP", b"")])


def fixture(path, linked=False):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("maps/zdcedge.wad", geometry(linked))
        archive.write(ROOT / "tools/zdcmp1-tests/edges.zc", "zscript.zc")
        archive.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers="ZDCMP1Edges" }\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default=os.environ.get("UTNT_ENGINE"), required=not os.environ.get("UTNT_ENGINE"))
    parser.add_argument("--iwad", default=os.environ.get("UTNT_IWAD"), required=not os.environ.get("UTNT_IWAD"))
    parser.add_argument("--mod", type=Path, default=ROOT / "zdcmp1")
    parser.add_argument("--renderer", choices=("0", "1"), default="1")
    args = parser.parse_args()
    for linked in (False, True):
        with tempfile.TemporaryDirectory() as directory:
            addon = Path(directory) / "edges.pk3"
            fixture(addon, linked)
            # Network events must settle before save/load or shutdown on fast renderers.
            floor_check = "netevent zdcfloor; wait 35; " if not linked else ""
            cmd = (f"unbindall; wait 35; netevent zdcedges {int(linked)}; wait 10; {floor_check}save zdc-edges; wait 10; "
                   f"load zdc-edges; wait 35; netevent zdcedges {int(linked)}; wait 10; {floor_check}"
                   "echo UTNT_REGRESSION_COMPLETE; echo UTNT_TEST_END; quit\n")
            result = run_case(args.engine, args.iwad, mod=args.mod, addon=addon, mapname="ZDCEDGE",
                              playerclass="ZDCMPPlayer", renderer=args.renderer, regression=True, timeout=50,
                              label=f"zdc-edges-{args.renderer}-{int(linked)}", commands=cmd,
                              settings=[("use_mouse", False), ("use_joystick", False), ("i_pauseinbackground", False)])
            expected = 10 if linked else 24
            if not result["ok"] or result["assertions"] != expected:
                print(Path(result["log"]).read_text()[-6000:])
                raise SystemExit(1)


if __name__ == "__main__":
    main()
