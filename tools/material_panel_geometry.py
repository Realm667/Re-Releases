"""Source-coordinate relief for profiled panels, rivets and door families.

The broad original components define the height; grime, blood, painted logos
and rust color do not move the base plane. All values are signed map units.
"""
import numpy as np
from material_geometry import Field

NAMES=set('IKWALL73 IKWALL74 IKWALL75 IKWALL76 IKWALL78 IKFLAT2 IKFLAT4 N_MTRC1 NMTRC1 NMTRC2 ADEL_F09 ADEL_F36 QDOOR1 QDOOR2 QDOOR3 QDOOR4 QDOOR5 QDOOR6 QDOOR7 QDOOR8 QDOOR9 OIDOOR2 OSNOW2'.split())


def _profiles(f,n):
    # Rounded, weathered vertical folds, NOT rectangular panel joints. The
    # dark and light sides form one continuous body. Coarse profiles are
    # shared by the differently weathered/colored wall skins.
    if n.startswith('IKWALL'):
        curves=[[(19,0),(19,24),(18,48),(19,72),(18,96),(19,128)],
                [(61,0),(62,24),(61,48),(62,72),(61,96),(61,128)],
                [(99,0),(99,24),(100,48),(99,72),(100,96),(99,128)]]
        widths=[11,12,12]
    else:
        curves=[[(12,0),(12,16),(12.5,32),(12,48),(12,64)],
                [(32,0),(32,16),(32,32),(32,48),(32,64)],
                [(51,0),(51.5,16),(52,32),(51,48),(51,64)]]
        widths=[5.5,6,6]
    for pts,r in zip(curves,widths):
        # Crown includes the right-hand painted shadow; adjacent troughs
        # remain rounded and shallow, without cutting thin false seams.
        center=np.interp(f.y,[p[1] for p in pts],[p[0]+r*.2 for p in pts])
        t=(f.x-center)/r
        bump=np.where(abs(t)<1,.65*np.cos(t*np.pi/2)**2,0)
        trough=-.45*np.exp(-((abs(t)-1.25)/.38)**2)
        f.z+=bump+trough
    if n.startswith('IKWALL'):
        # Continuous top/bottom trim, no vertical breaks at tile boundaries.
        f.rect(-2,0,130,8,0,.5);f.rect(-2,120,130,128,0,.5)
        if n in ('IKWALL76','IKWALL78'):
            for a,b in [(1,3),(6,8),(120,122),(125,127)]:f.rect(-2,a,130,b,.4,.35)
        else:
            for y in (1,7,121,126):f.groove([(-2,y),(130,y)],.45,-.45)


def _riveted(f,n):
    if n=='ADEL_F36':
        # Uniform small fasteners. There is no panel grid in this artwork.
        f.bolts([4.5,15,26,37,48,58],[4,12,20,28,36,44,52,60],1.5,.55)
        return
    patterns=[[5,12,20.5,44.5,59.5], [5,12,21.5,33.5,41.5,50.5,60.5]]
    if n=='ADEL_F09':patterns[1]=[5,12,26,44.5,59.5]
    for row,y in enumerate(range(0,f.h,32)):
        pattern=patterns[row%2] if row<3 else patterns[0]
        for x in pattern:f.groove([(x,y+2),(x,y+29)],.65,-.65)
        f.groove([(-2,y+31.5),(66,y+31.5)],.6,-.65)
        f.bolts([7.5,15.5,23.5,31.5,39.5,47.5,55.5,63.5],
                [y+3.5,y+11.5,y+19.5,y+27.5],1.25,.6)
    if n=='NMTRC2':f.z=np.rot90(f.z).copy()


def _lock(f,y=60):
    f.rect(54,y,73,y+12,.35,.7)
    f.rect(55.5,y+1.5,61.5,y+10.5,0,.5)
    f.rect(64,y+1.5,71.5,y+10.5,-.35,.5)
    f.rect(66,y+4,69,y+8,.65,.4)


def _framed_door(f,n):
    # The shared outer frame is the actual map plane. Four inset fields.
    for x in (8,72):
        for y in (10,68):f.rect(x,y,x+44,y+50,-1.15,1.5)
    if n in ('QDOOR1','QDOOR3'):
        # Complete slat faces include painted dark sides; red paint in 3
        # does not alter the construction of the undamaged door.
        for x in (8,72):
            for y in (10,68):
                for dx in (1,8,15,23,31,38):f.rect(x+dx,y+1,x+dx+5,y+49,-.55,.65)
        _lock(f)
    else:
        # Crossbars on QDOOR2/4 connect to the frame. Their vertical parts
        # remain above the dark inset backing, including shadow halves.
        for x in (8,72):
            for y in (10,68):
                for dx in (8,21,34):f.rect(x+dx,y+2,x+dx+6,y+49,-.2,.65)
                for dy in (11,31):f.rect(x,y+dy,x+44,y+dy+5,0,.7)
        if n=='QDOOR2':
            f.poly([(42,48),(54,48),(54,53),(72,53),(72,48),(84,48),(84,78),
                    (72,78),(72,84),(54,84),(54,78),(42,78)],.35,.8)
            # Recessed horseshoe around a raised central tongue.
            f.poly([(49,56),(54,56),(56,68),(62,71),(69,68),(71,56),(76,56),
                    (77,69),(72,74),(54,74),(49,70)],-.8,.7)
            f.poly([(59,57),(67,57),(65,68),(62,70)],.75,.6)
        else:
            f.rect(38,43,89,82,.35,.8)
            # Four negative spaces leave the complete eight-point emblem.
            f.poly([(44,51),(57,51),(62,59),(55,56),(48,61)],-.85,.7)
            f.poly([(68,51),(82,51),(79,61),(72,57),(65,60)],-.85,.7)
            f.poly([(45,67),(55,66),(61,72),(57,77),(46,77)],-.85,.7)
            f.poly([(70,67),(81,67),(81,77),(69,77),(65,72)],-.85,.7)
            _lock(f,30)
    f.groove([(63.5,-2),(63.5,130)],.8,-1.25)


def _plain_door(f):
    f.groove([(63.5,-2),(63.5,130)],.85,-1.1)
    # Paired square bolt heads, not the randomly distributed dents/rust.
    for x in (3,58,67,122):
        for y in (7,19,31,43,56,78,90,102,115,125):
            f.rect(x-1.7,y-1.8,x+1.7,y+1.8,.6,.65)
    _lock(f)


def _carved_door(f,n):
    if n=='QDOOR6':
        f.rect(12,12,53,118,-.65,1.2)
        # Worn heraldic forms are ambiguous at this texel density. Retain
        # the painted relief inside the complete recess rather than invent
        # spikes from individual highlights.
    else:
        for y in (7,21,35,49,63,77,91,105):
            for x in (7,26,44):f.rect(x,y,x+14,y+12,-.7,.85)
    for a,b in [(2,4),(124,126)]:f.rect(-2,a,66,b,.2,.5)


def _angled_door(f):
    # Black triangular corners are outside the door leaf. They stay flat;
    # do not pull texture coordinates across this original silhouette.
    left=np.clip((f.x-(37-37*f.y/128))/3,0,1)
    right=np.clip(((90+38*f.y/128)-f.x)/3,0,1)
    mask=left*right
    f.groove([(64,-2),(64,130)],.8,-.75)
    f.z*=mask


def _zigzag(f):
    # Pale inset metal lies BELOW the dark outer frame/zigzag division.
    # The inner return is horizontal at source row 72, with a short bevel
    # at its right tip; a single diagonal would cut through the metal face.
    f.poly([(7,7),(92,7),(75,39),(39,39),(15,82),(45,84),(25,120),(7,120)],-1.05,1.3)
    f.poly([(110,7),(121,7),(121,120),(46,120),(67,77),(66,74),(63,72),(39,72),
            (49,54),(82,54)],-1.05,1.3)
    f.groove([(103,-2),(76,46),(43,46),(27,76),(59,76),(33,130)],1.0,-1.55)


def _ogro_door(f,n):
    # Both source images share exactly the same metal structure. The bright
    # lower bevels of these handle pockets are recessed, not raised bars.
    for x,y in ((13,12),(96,52)):
        f.rect(x,y,x+16,y+63,-1.25,1.0)
        # Sloping lower end of the recess, smoothly returning to the plate.
        ramp=np.clip((f.y-(y+45))/18,0,1)
        f.clip=((f.x>x)&(f.x<x+16)&(f.y>=y+45)&(f.y<y+63)).astype(float)
        f.rect(x,y+44,x+16,y+63,-1.25*(1-ramp),1.0);f.clip=1
    for x,y in ((5,5),(114,4),(122,16),(5,113),(15,121),(122,122)):
        f.rivet(x,y,2,.65)
    f.groove([(-3,131),(131,-3)],1.35,-1.4)
    for x in (1,127):f.groove([(x,-2),(x,130)],.5,-.45)
    for y in (1,127):f.groove([(-2,y),(130,y)],.5,-.45)
    if n=='OSNOW2':
        # Snow sits ONLY on the ledges visible in the painted winter skin.
        # Metal outside these explicit deposits is byte-identical to OIDOOR2.
        for pts,r,z in [([(-2,1),(13,1)],1.4,.45),([(56,1),(113,1)],1.2,.4),
                        ([(59,1),(62,5),(65,1)],1.2,.6),
                        ([(16,73),(20,70),(25,71)],2.0,.55),
                        ([(100,113),(106,109),(111,113)],2.1,.55),
                        ([(46,80),(53,73)],1.0,.35),
                        ([(79,47),(86,40)],1.0,.35),
                        ([(113,13),(122,4)],1.1,.4)]:
            f.wire(pts,r,z,0,.45)


def panel_height(rgb,logical,detail):
    n=detail['name'];h,w=rgb.shape[:2]
    if n not in NAMES:raise ValueError(n)
    expected=(64,64) if n in ('IKFLAT2','IKFLAT4','NMTRC1','NMTRC2','ADEL_F09','ADEL_F36') else (64,128) if n in ('N_MTRC1','QDOOR6','QDOOR7') else (128,128)
    if (w,h)!=expected:raise ValueError('Untraced artwork dimensions: '+n)
    f=Field(w,h,2)
    if n.startswith('IK'):_profiles(f,n)
    elif n.startswith('QDOOR'):
        if n in ('QDOOR1','QDOOR2','QDOOR3','QDOOR4'):_framed_door(f,n)
        elif n=='QDOOR5':_plain_door(f)
        elif n in ('QDOOR6','QDOOR7'):_carved_door(f,n)
        elif n=='QDOOR8':_angled_door(f)
        else:_zigzag(f)
    elif n in ('OIDOOR2','OSNOW2'):_ogro_door(f,n)
    else:_riveted(f,n)
    return f.z
