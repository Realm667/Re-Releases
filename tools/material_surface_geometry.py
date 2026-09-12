"""Source-traced supplementary floors, planks and riveted plates.

All values are signed map units. Diffuse paint is never used as height.
Coordinates are original texels, including the authored phase of wood skins.
"""
import numpy as np
from material_geometry import Field

NAMES=set("CITYF17 CITYF18 FLOOR4 SFLOOR1 QFLAT06 ADEL_G01 ADEL_F67 ADEL_F68 ADEL_F71 OBR09 OBR10 OBR04 ADEL_G02 ADEL_G03 ADEL_G04".split())


def _city(f):
    # Both color skins use the same irregular arrangement of cut slabs.
    # A 16x16 grid would cut false seams through the taller left/centre slabs.
    for y,x0,x1 in [(0,-2,66),(16,-2,16),(16,32,66),
                    (32,16,66),(48,-2,16),(48,32,66),(64,-2,66)]:
        f.groove([(x0,y),(x1,y)],.75,-.85)
    for x,y0,y1 in [(0,-2,66),(16,-2,66),(32,-2,16),(32,32,66),
                    (48,16,32),(48,48,66),(64,-2,66)]:
        f.groove([(x,y0),(x,y1)],.75,-.85)


def _floor(f):
    # Narrow horizontal holes in a continuous cast-metal grate. Draw each
    # complete opening, including its shaded half, not just the black texels.
    rows=[(0,[(18,27),(39,47)]),(7,[(8,17),(29,37),(49,58)]),
          (11,[(18,27),(39,47)]),(15,[(7,18),(48,59)]),
          (19,[(18,27),(39,47)]),(23,[(8,17),(29,37),(49,58)]),
          (27,[(18,27),(39,47)]),(31,[(8,17),(29,37),(49,58)]),
          (35,[(18,27),(39,47)]),(39,[(8,17),(29,37),(49,58)]),
          (43,[(18,27),(39,47)]),(47,[(8,17),(29,37),(49,58)]),
          (51,[(18,27),(39,47)]),(55,[(8,17),(29,37),(49,58)]),
          (59,[(18,27),(39,47)])]
    for y,spans in rows:
        for x0,x1 in spans:
            for oy in (-64,0,64):f.rect(x0,y+oy,x1,y+oy+2,-1.25,.35)


def _slots(f):
    # Rounded long slots alternate with short round holes. The remaining
    # metal webs stay exactly on the base plane.
    for x,ya,yb in [(8.5,17,48),(20.5,6,25),(20.5,41,58),
                    (32.5,18,48),(44.5,6,24),(44.5,41,58),(56.5,17,48)]:
        f.groove([(x,ya),(x,yb)],3.15,-1.55)
    for x,ys in [(8.5,[6,58]),(20.5,[32]),(32.5,[6,58]),(44.5,[32]),(56.5,[6,58])]:
        for y in ys:f.groove([(x,y),(x+.01,y)],3.1,-1.55)


def _ornament(rgb,logical):
    # This dense worn ornament has no reliable straight component boundaries.
    # Integrate the original upper-lit slope field at fixed physical amplitude,
    # as for the approved snow reconstruction, rather than inventing channels.
    from material_traced_geometry import snow_height
    return snow_height(rgb,logical)*.45


def _wood(f,n):
    if n in ('ADEL_F67','ADEL_F68'):
        # F68 is byte-for-byte the horizontal reflection of F67.
        for k in (-64,0,64):
            for phase in (0,24,52):f.groove([(phase+k-66,-66),(phase+k+130,130)],.65,-.8)
        if n=='ADEL_F68':f.z=f.z[:,::-1].copy()
        return
    # G02/G03 use the same grain shifted 32 pixels horizontally; G04 shares
    # the G01 phase. Respect that phase rather than shifting the data UVs.
    phase=32 if n in ('ADEL_G02','ADEL_G03') else 0
    for x in (19.5,43.5,53.5):
        x=(x+phase)%64
        if n=='ADEL_F71' and x!=43.5:continue
        f.groove([(x,-2),(x,f.h+2)],.7,-.8)
    if n in ('ADEL_G02','ADEL_G03'):
        y=8 if n=='ADEL_G02' else 32
        f.rect(-2,-2,66,y,1.2,.65)
        f.poly([(23,y-1),(40,y-1),(40,y+11),(35,y+16),(35,y+39),
                (40,y+47),(33,y+58),(25,y+47),(29,y+39),(29,y+16),(23,y+11)],1.5,.8)
        f.bolts([32],[y+8,y+46],2,2.2,1.5)
    elif n=='ADEL_G04':
        # Riveted straps are 16 pixels high in this artwork, not 10.
        for a,b in [(-2,16),(112,130)]:
            f.rect(-2,a,66,b,.65,.6)
        f.bolts([4,12,20,28,36,44,52,60],[5,11,117,123],1.2,1.1,.65)


def _plates(f,n):
    if n=='OBR04':
        for x in range(0,65,16):f.groove([(x,-2),(x,130)],.55,-.55)
        for y in range(0,129,16):f.groove([(-2,y),(66,y)],.55,-.55)
        for oy in range(0,128,16):
            for ox in range(0,64,16):f.bolts([ox+3,ox+12],[oy+3,oy+12],1.0,.55)
    elif n=='OBR09':
        for y in (0,64,128):f.groove([(-2,y),(66,y)],.65,-.65)
        for x in (0,64):f.groove([(x,-2),(x,130)],.65,-.65)
        for oy in (0,64):f.bolts([4,59],[oy+y for y in (4,15,26,37,48,59)],1.25,.7)
    else:
        for y in (0,112,128):f.groove([(-2,y),(66,y)],.65,-.65)
        for x in (0,64):f.groove([(x,-2),(x,130)],.65,-.65)
        f.bolts([4,16,28,40,59],[4],1.25,.7)
        f.rect(-2,113,66,128,.2,.6)
        f.bolts([4,16,28,40,59],[117],1.55,.9,.2)
        f.rect(28,120,36,125,-.5,.55)


def surface_height(rgb,logical,detail):
    n=detail['name'];h,w=rgb.shape[:2]
    if n not in NAMES:raise ValueError(n)
    if (w,h) not in ((64,64),(64,128)):raise ValueError('Untraced expanded artwork: '+n)
    f=Field(w,h,2)
    if n.startswith('CITYF'):_city(f)
    elif n=='FLOOR4':_floor(f)
    elif n=='SFLOOR1':_slots(f)
    elif n=='QFLAT06':return _ornament(rgb,logical)
    elif n.startswith('ADEL'):_wood(f,n)
    else:_plates(f,n)
    return f.z
