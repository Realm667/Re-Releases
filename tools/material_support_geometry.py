"""Source-traced tiles, scratches, supports and matching wall trims.
All coordinates are original texels; height is signed map units, plane zero.
"""
import numpy as np
from material_geometry import Field
from material_panel_geometry import _profiles
NAMES=set('CFLOOR2 CFLOOR4 OBSUP1 IKSUP5 QTECH17 QTECH22 OBR01 OBRL11 QCITY07 QCITY10 QCITY11 IKWALL70'.split())


def _rounded_tile(f,x0,y0,x1,y1,radius,bevel):
    # Analytic rounded rectangle: straight parallel sides and circular corners.
    # A bevel only softens the perimeter; the broad tile face stays at zero.
    qx=abs(f.x-(x0+x1)/2)-((x1-x0)/2-radius)
    qy=abs(f.y-(y0+y1)/2)-((y1-y0)/2-radius)
    sd=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius
    f.put(-sd,0,bevel)


def _slabs(f):
    f.z[:]=-.85
    for y in (1.5,33.5):
        for x in (1.5,33.5):_rounded_tile(f,x,y,x+29,y+29,3,1.25)
    # Surface wear stays much shallower than the tile joints.
    for p in [[(34,20),(41,18),(46,14),(52,12),(56,7)],
              [(47,29),(48,25),(52,22),(54,18)],
              [(4,54),(10,53),(14,52),(18,53),(24,50)],
              [(11,33),(15,36),(14,40)]]:
        f.clip=(f.z>-.01).astype(float);f.groove(p,.45,-.18);f.clip=1


def _scratched_tile(f):
    # One 64-texel square tile, repeated by the engine. The diagonal marks
    # are shallow cuts/wear in its face, never raised ribs or an inner grid.
    f.z[:]=-.65
    f.rect(.65,.65,63.35,63.35,0,.85)
    face=(f.z>-.01).astype(float)
    strokes=[[(2,5),(10,0)],[(13,5),(20,0)],[(34,12),(44,4)],
             [(43,16),(51,9)],[(57,12),(66,5)],[(0,27),(9,20)],
             [(7,22),(18,13)],[(17,27),(27,19)],[(34,30),(43,22)],
             [(43,35),(53,27)],[(1,45),(10,38)],[(10,41),(20,33)],
             [(18,46),(28,38)],[(36,50),(45,43)],[(47,50),(57,42)],
             [(3,60),(12,53)],[(13,59),(23,51)],[(25,65),(34,57)]]
    f.clip=face
    for p in strokes:f.groove(p,.55,-.18)
    f.clip=1


def _supports(f,n):
    if n=='OBSUP1':
        for y in range(8,128,16):f.rivet(8,y,3.5,.7)
        for x in (1,15):f.groove([(x,-2),(x,130)],.5,-.4)
    elif n=='IKSUP5':
        for y in range(4,128,8):f.rect(3,y,13,y+5,-1.1,.8)
        for x in (1,15):f.groove([(x,-2),(x,130)],.4,-.35)
    else:
        # Same .85-unit fastener crown as the related broad Quake girder.
        for y in range(8,128,16):f.rivet(8,y,2,.85)
        for x in (1,15):f.groove([(x,-2),(x,130)],.45,-.4)


def _ogro(f,n):
    for y in range(0,129,16):f.groove([(-2,y+.5),(66,y+.5)],.55,-.55)
    if n=='OBRL11':
        # Regular round embossed heads include their painted lower shadows.
        for y in range(3,112,8):f.bolts(range(4,64,8),[y],1.8,.4)
        f.rect(-2,112,66,128,0,.4)
        f.rect(3,113,61,126,-1,.65)
        for x in range(6,61,6):f.rect(x,115,x+2,123,-.35,.35)


def _trim(f,n):
    # Three skins share the wall plane and two source-positioned band forms.
    # 07 repeats a band across each 64-row boundary; 10 has a deeper frieze;
    # 11 combines 10 above and 07 below, matching their actual crops.
    f.z[:]=0
    def small(y):
        for a,b,z in [(-8,-6,.22),(-5,-3,.4),(-2,0,.15),(1,3,.4),(4,6,.22)]:
            f.rect(-2,y+a,66,y+b,z,.45)
        for dy in (-6,-3,0,3):f.groove([(-2,y+dy),(66,y+dy)],.35,-.3)
    def large(y):
        f.rect(-2,y+6,66,y+18,.22,.7)
        for a,b in [(6,8),(13,16)]:f.rect(-2,y+a,66,y+b,.5,.6)
        for dy in (11,17):f.groove([(-2,y+dy),(66,y+dy)],.4,-.3)
    for y in (-64,0,64,128):
        small(y)
        if n=='QCITY10' or (n=='QCITY11' and y%128==0):large(y)



def support_height(rgb,logical,detail):
    n=detail['name'];h,w=rgb.shape[:2]
    expected=(64,64) if n.startswith('CFLOOR') else (16,128) if n in ('OBSUP1','IKSUP5','QTECH17') else (128,128) if n in ('QTECH22','IKWALL70') else (64,128)
    if (w,h)!=expected or n not in NAMES:raise ValueError('Untraced artwork '+n)
    f=Field(w,h,2)
    if n=='CFLOOR2':_slabs(f)
    elif n=='CFLOOR4':_scratched_tile(f)
    elif n in ('OBSUP1','IKSUP5','QTECH17'):_supports(f,n)
    elif n=='QTECH22':
        # Same pale inset outline/depth as QTECH20, but source-specific bolts.
        left=[(-2,19),(5,19),(32,106),(21,120),(-2,120)]
        for poly in (left,[(128-x,y) for x,y in left[::-1]]):f.poly(poly,-2.5,1)
        for x,y in [(21,28),(24,40),(27,50),(30,61),(33,72),(36,84),(39,95),(42,107),(37,119)]:
            f.bolts([x,128-x],[y],1.4,.85)
        for x in (53,67):
            f.rect(x,7,x+9,118,-1.1,1)
            for y in (12,68):f.rect(x+2,y,x+6,y+45,-.35,.6)
    elif n in ('OBR01','OBRL11'):_ogro(f,n)
    elif n.startswith('QCITY'):_trim(f,n)
    else:_profiles(f,'IKWALL73') # Shared rounded family, no invented panel cuts.
    return f.z
