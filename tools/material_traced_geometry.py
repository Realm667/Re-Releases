"""Source-traced component relief, in map units at the original pixel coordinates.

Painted highlights/shadows belong to the same solid body. Authored construction
is independent of the diffuse colors. Brick seams and snow shading have their
own bounded reconstruction, rather than a generic luminance-to-height curve.
"""
import numpy as np
from PIL import Image, ImageFilter
from material_geometry import Field

NAMES={'ADEL_W39','IKTCR05B','IKWALL28','PANBOOK','OTECH6','TECHG',
       'QTECH30','QTECH31','QTECH32','METALF12','QMET10','QMET33','CITYF01','SNOW3'}

def _blur(a,r):
    pad=max(2,int(r*4+2))
    # Pillow GaussianBlur does not support float; preserve signed data via bytes.
    lo=float(a.min());span=max(float(a.max()-lo),1e-6)
    im=Image.fromarray(np.round(np.clip((np.pad(a,pad,mode='wrap')-lo)/span,0,1)*255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)),np.float32)[pad:-pad,pad:-pad]/255*span+lo

def _door(f):
    # 16..48 and 80..112 are the inset panels; 0..16, 48..80,
    # 112..128 are continuous stiles. The centre joint is at 64.
    for a,b in ((16,48),(80,112)):
        f.rect(a,15,b,113,-1.3,.65)
        f.rect(a+1,18,b-1,112,-.65,.55)
        f.groove([((a+b)/2,18),((a+b)/2,112)],.65,-1.3)
        f.rect(a,-2,b,15,.35,.8);f.rect(a,112,b,130,.35,.8)
        f.bolts([a+8,b-8],[7,119],1.15,.8,.35)
    f.groove([(64,-2),(64,130)],.75,-1.25)
    # Flat sawn boards, not cylinders; end cuts meet the inner frame.
    for p in [[(17,73),(47,20),(47,47),(17,109)],
              [(81,20),(111,73),(111,109),(81,47)]]:f.poly(p,.65,.9)
    # The black plates start at row 68; their narrowing grips extend to 106.
    for x in (56,72):
        f.poly([(x-7,68),(x+7,68),(x+6,75),(x+3,80),(x+3,97),
                (x+6,99),(x+3,104),(x,106),(x-3,104),(x-6,99),(x-3,97),(x-3,80),(x-6,75)],.7,.55)
        f.rect(x-1.7,77,x+1.7,98,1.15,.6)
        f.bolts([x],[71,99],1.25,1.35,.7)

def _crate(f):
    # Three dark openings, separated by TWO parallel diagonal braces.
    f.rect(.5,.5,63.5,63.5,.25,.8)
    f.rect(5,5,59,59,-1.1,.75)
    f.rect(8,8,56,55,.45,.8)
    f.rect(15,16,50,49,-1.35,.8)
    f.poly([(24,16),(32,16),(50,34),(50,44)],.65,.8)
    f.poly([(15,23),(15,33),(31,49),(41,49)],.65,.8)
    # A highlight on the top and shadow below each board does not split it.

def _runes(f):
    f.grid(32,32,-1.2,1.15)
    # Filled incisions follow the visible stroke width, including dark sides.
    paths=[[(9,10),(23,10),(23,13),(12,13),(12,15),(23,15),(23,23),(9,23),(9,20),(20,20),(20,18),(9,18)],
           [(43,10),(55,10),(55,14),(47,14),(47,21),(51,21),(51,18),(55,18),(55,24),(43,24)],
           [(9,42),(13,42),(13,49),(20,49),(20,44),(24,44),(24,52),(13,52),(13,57),(9,57)],
           [(41,41),(55,41),(55,55),(51,55),(51,45),(41,45)],
           [(41,47),(47,47),(47,51),(44,51),(44,53),(47,53),(47,55),(41,55)]]
    for oy in range(0,f.h,64):
        for p in paths:f.poly([(x,y+oy) for x,y in p],-1.5,.45)
        for yy in (5,26,37,58):f.bolts([5,26,37,58],[yy+oy],1,.35)

def _vent(f):
    # Native TECHG is repeated verbatim twice by OTECH6. Slat crowns lie
    # at rows 8,14,...,50. Their shadowed lower faces slope into the slot.
    for oy in range(0,f.h,64):
        f.rect(4,oy+3,60,oy+56,-1.6,.6)
        for y in range(8,55,6):
            t=(f.y-(oy+y))/3.0
            face=-.15-1.45*np.clip(t,0,1)
            f.rect(4,oy+y-.25,60,oy+y+3,face,.3)
        f.rect(3,oy+55,61,oy+57,0,.55)
        f.rect(2,oy+58,62,oy+62,.2,.65)
        # Small perimeter fasteners belong to the frame, not the slots.
        f.bolts([2,62],[oy+2,oy+61],.9,.45)

def _books(f):
    # Raised wooden surround with six independently traced shelves.
    f.rect(10,25,54,108,-2.8,.5)
    for a,b in ((43,47),(56,60),(69,72),(82,86),(95,98),(107,111)):
        f.rect(10,a,54,b,0,.45)
    rows=[(43,[(12,34,15),(16,34,19),(20,35,22),(29,31,32),(33,32,36),(38,35,41),(43,35,46),(48,33,50),(51,33,54)]),
          (56,[(12,49,15),(16,48,19),(21,49,24),(26,52,28),(31,48,34),(35,49,38),(40,47,43),(45,50,47),(49,49,52)]),
          (69,[(12,62,15),(16,63,18),(20,63,23),(26,62,29),(30,61,32),(33,63,36),(39,62,42),(44,63,46),(47,63,50),(51,62,53)]),
          (82,[(12,73,15),(16,74,18),(20,73,23),(24,74,26),(27,74,29),(31,73,34),(35,73,38),(39,74,41),(43,73,46),(48,74,51),(52,73,54)]),
          (95,[(12,88,15),(16,87,19),(21,89,24),(25,88,28),(30,86,33),(34,88,36),(38,87,42),(44,88,46),(48,87,51),(52,88,54)]),
          (107,[(13,100,16),(17,99,19),(21,100,24),(26,99,28),(30,100,33),(34,100,36),(38,100,41),(43,99,46),(48,101,50),(51,99,54)])]
    for bottom,books in rows:
        for a,top,b in books:f.rect(a,top,b,bottom,-1.1,.45)
    # The sloping first-row volume is a leaning book, not a vertical bar.
    f.poly([(21,32),(24,32),(28,43),(24,43)],-.95,.45)
    # Twisted columns are complete carved bands; no darkness-to-hole mapping.
    for x in (4,54):
        f.rect(x,17,x+6,124,.15,.55)
        for y in range(16,124,7):
            f.poly([(x,y),(x+6,y+5),(x+6,y+8),(x,y+3)],.5,.65)
    for a,b in ((7,25),(40,57)):
        f.rect(a,4,b,13,-.55,.5);f.rect(a+2,5,b-2,11,0,.6)
    for x in (15,27,39):
        f.rect(x,111,x+10,122,-.55,.5);f.rect(x+2,112,x+8,119,0,.65)
    f.rect(-1,-1,65,2,.25,.5);f.rect(-1,14,65,17,.25,.5)
    f.rect(-1,124,65,127,.25,.5)

def _machine(f,n):
    # Actual side cutouts of these three skins are much narrower than the
    # generic QTECH25 V-frame. Shared side hardware uses the same coordinates.
    for sign in (False,True):
        p=[(-2,20),(4,20),(30,105),(21,119),(-2,119)]
        if n=='QTECH31':p=[(-2,20),(16,20),(16,120),(-2,120)]
        if sign:p=[(128-x,y) for x,y in p[::-1]]
        f.poly(p,-1.25,.85)
        if n=='QTECH31':
            f.clip=(f.z<-1.0)
            for y in range(28,120,13):f.rect(-2,y,130,y+1.5,-.9,.4)
            f.clip=1
    for y,x in [(27,20),(38,23),(49,27),(60,30),(71,33),(82,36),(93,39),(104,42),(117,38)]:
        if n=='QTECH31':x=25
        f.bolts([x,128-x],[y],1.3,.65)
    f.groove([(-2,126),(130,126)],.55,-.4)
    if n=='QTECH30':
        f.rect(40,18,86,79,-2.2,.5)
        paths=[[(44,20),(44,30),(51,37),(51,48),(46,54),(46,78)],
               [(49,20),(49,27),(57,38),(57,49),(53,55),(53,69),(55,78)],
               [(55,20),(55,28),(61,34),(61,47),(57,56),(57,68),(62,74),(62,79)],
               [(61,20),(61,32),(66,38),(66,49),(62,57),(62,70),(64,79)],
               [(68,20),(68,35),(64,40),(64,53),(70,59),(70,79)],
               [(75,20),(75,35),(73,40),(73,48),(67,53),(67,64),(72,74),(72,79)],
               [(81,20),(81,35),(78,40),(78,48),(82,53),(82,63),(80,69),(80,78)],
               [(83,20),(83,45),(76,52),(76,79)],
               [(44,59),(49,63),(57,59),(65,61),(70,56),(81,58)]]
        for pts in paths:f.wire(pts,.8,-.9,-2.2,.3)
        f.rect(46,13,57,18,.25,.5);f.rect(65,14,85,17,-.4,.4)
        f.rect(50,86,59,109,-.55,.5);f.rect(52,88,57,107,-.9,.5)
        f.rect(64,94,80,110,-1.7,.5)
        for x in (65,68,73,77):f.wire([(x,95),(x,101),(x+1,109)],.7,-.65,-1.7)
        f.rect(64,86,70,90,-.4,.3)
    elif n=='QTECH31':
        f.rect(33,33,96,121,-2.1,.6)
        f.rect(30,80,51,121,-2.1,.5)
        for pts in [[(49,36),(74,36),(86,41),(95,41)],[(48,39),(68,39),(75,43),(91,44)],[(48,44),(66,44),(83,41),(83,36)],[(53,49),(71,49),(81,45),(95,45)]]:
            f.wire(pts,.85,-.75,-2.1)
        for a,b,c,d in [(35,38,39,52),(41,40,45,52),(42,59,51,77),(55,50,85,65),(55,67,64,77),(53,83,61,91)]:f.rect(a,b,c,d,-.6,.6)
        f.rect(58,53,82,62,-1.4,.5)
        for x,y in [(61,55),(67,57),(72,55),(76,59)]:f.rect(x,y,x+2,y+2,-.85,.3)
        for y in (54,59,64,69,74):f.rect(34,y,41,y+1.6,-.8,.3)
        for y in (81,86,90):f.rect(33,y,49,y+1.5,-.75,.4)
        for x in (68,75,83,91):
            for y in (68,77,85,92):f.rect(x,y,x+3.5,y+3,-.65,.5)
        for x in (36,41,47,57,63,69,78,87,92):f.wire([(x,97),(x,119)],1.25,-.65,-2.1,.4)
        f.rect(33,15,51,28,.2,.6);f.rect(35,17,49,26,-.5,.5)
        f.rect(52,23,59,26,-.3,.35);f.rect(62,28,94,32,.1,.5)
    else:
        f.poly([(29,19),(99,19),(87,80),(44,80)],-2.1,.6)
        f.clip=(f.z<-1.8)
        # Traced irregular housings; do not impose a new regular chip grid.
        for a,b,c,d in [(33,23,39,31),(45,22,58,29),(60,22,65,31),(79,24,91,30),(34,33,40,40),(45,33,51,40),(57,33,64,39),(68,33,74,39),(77,32,84,39),(44,42,54,47),(58,43,63,48),(68,42,74,48),(81,42,88,48),(40,50,49,55),(56,50,63,56),(68,51,77,57),(42,59,49,66),(56,59,63,64),(65,61,73,67),(77,61,84,66),(46,69,54,74),(60,69,70,75),(73,71,81,76)]:f.rect(a,b,c,d,-.8,.65)
        for pts in [[(41,22),(41,30),(44,33)],[(73,24),(67,27),(67,31)],[(52,35),(52,41),(57,44)],[(50,48),(53,53),(53,58)],[(75,44),(78,49),(82,52)],[(50,63),(54,66),(58,66)]]:f.wire(pts,.7,-.65,-2.1)
        f.clip=1
        f.rect(32,5,94,14,-1.9,.4)
        for x in (35,41,46,54,60,66,72,80,86,91):f.wire([(x,6),(x,12)],1.3,-.65,-1.9)
        for a,b in ((44,53),(69,78)):f.rect(a,15,b,19,-.55,.4)
        f.rect(51,85,77,110,-2,.5)
        for x in (54,59,66,72):f.wire([(x,86),(x,108)],1.4,-.65,-2)

def _metal(f,n):
    if n=='QMET33':
        # One continuous strip: overlapping repeated rectangles would deepen
        # its bevel at every artificial 64-pixel boundary.
        f.rect(16,-2,48,f.h+2,-.65,.8)
        return
    if n=='QMET10':
        for oy in range(0,f.h,64):
            a,b=8,56
            # Upper/left dark bevel and lower/right lit bevel indicate recess.
            f.rect(a,oy+8,b,oy+56,-.65,.8)
        return
    # METALF12: connected angular castings, all substantially flatter than
    # the old bright-pixel embossing. The dark passages separate complete Ls.
    f.z[:]=-.6
    polys=[[(3,1),(17,1),(17,6),(9,6),(9,12),(5,12),(5,7),(3,7)],
           [(24,-2),(29,-2),(29,13),(25,13)],[(33,-2),(37,-2),(37,13),(32,13)],
           [(50,1),(64,1),(64,5),(53,5),(53,9),(48,9),(48,5)],
           [(3,16),(16,16),(16,21),(7,21),(7,25),(3,25)],
           [(4,25),(10,25),(10,32),(4,32)],[(12,22),(17,22),(17,30),(12,30)],
           [(24,18),(33,18),(33,28),(27,28),(27,23),(23,23)],
           [(39,16),(56,16),(56,22),(42,22),(42,27),(39,27)],
           [(2,35),(16,35),(16,46),(12,46),(12,39),(6,39),(6,44),(2,44)],
           [(21,33),(33,33),(33,38),(30,38),(30,42),(25,42),(25,38),(21,38)],
           [(42,33),(53,33),(53,37),(47,37),(47,42),(42,42)],
           [(26,46),(32,46),(32,54),(28,54),(28,50),(26,50)],
           [(35,43),(39,43),(39,52),(44,52),(44,56),(35,56)],
           [(50,46),(56,46),(56,51),(60,51),(60,56),(50,56)],
           [(3,50),(15,50),(15,55),(8,55),(8,62),(3,62)],
           [(19,56),(26,56),(26,62),(19,62)],[(44,59),(55,59),(55,64),(44,64)]]
    for p in polys:f.poly(p,0,.85)


def brick_height(rgb,logical):
    """Trace bright continuous mortar lines, then assign complete flat bricks.

    The original uses 8-pixel courses. Expanded artwork has distinct 11/12-
    pixel courses and irregular joints; these must be measured independently.
    """
    h,w=rgb.shape[:2];s=2 if max(h,w)<=128 else 1
    f=Field(w,h,s,base=0)
    if w==64:
        courses=[(0,8,[0,16,32,48,64]),(8,16,[8,24,40,56]),(16,24,[0,16,32,48,64]),(24,32,[8,24,40,56]),(32,40,[0,16,32,48,64]),(40,48,[8,24,40,56]),(48,56,[0,16,32,48,64]),(56,64,[8,24,40,56])]
    else:
        lum=rgb.astype(np.float32).mean(2)
        score=np.median(lum,axis=1)
        rise=score-np.roll(score,1)
        peaks=[i for i in range(h) if rise[i]>4 and rise[i]>=rise[(i-1)%h] and rise[i]>rise[(i+1)%h]]
        rows=[]
        for i in sorted(peaks,key=lambda j:-rise[j]):
            if all(abs(i-j)>=7 for j in rows):rows.append(i)
        rows.sort()
        courses=[]
        for a,b in zip([-1]+rows,rows+[h]):
            if b-a<4:continue
            strip=lum[max(0,a+2):min(h,b-2)]
            if len(strip)<2:continue
            # Mortar is consistently lighter over the full course; sporadic
            # face highlights disappear in the lower percentile statistic.
            v=np.percentile(strip,30,axis=0);contrast=v-(np.roll(v,3)+np.roll(v,-3))*.5
            continuity=np.mean(strip>np.maximum(np.roll(strip,3,axis=1),np.roll(strip,-3,axis=1))+3,axis=0)
            candidates=[x for x in range(w) if contrast[x]>4 and continuity[x]>=.7 and v[x]>=v[(x-1)%w] and v[x]>v[(x+1)%w]]
            xs=[]
            for x in sorted(candidates,key=lambda j:-contrast[j]):
                if all(min(abs(x-q),w-abs(x-q))>=12 for q in xs):xs.append(x)
            courses.append((a,b,sorted(xs)))
    for a,b,xs in courses:
        f.groove([(-2,a+.5),(w+2,a+.5)],.8,-1.1)
        for x in xs:f.groove([(x+.5,a+.5),(x+.5,b+.5)],.65,-1.05)
    return f.z


def snow_height(rgb,logical):
    """Bounded integration of the upper-lit slope field, not brightness peaks.

    Low-frequency illumination and sub-texel grain are excluded. The vertical
    derivative of height follows light/shadow pairs; missing horizontal shape
    information is regularized. This is an interpretation, not recovered mesh.
    """
    h,w=rgb.shape[:2];density=w/logical[0]
    lum=rgb.astype(np.float32).mean(2)/255
    signal=_blur(lum,max(.5,.45*density))-_blur(lum,5*density)
    ky=2*np.pi*np.fft.fftfreq(h,d=1/density)[:,None]
    kx=2*np.pi*np.fft.fftfreq(w,d=1/density)[None,:]
    z=np.fft.ifft2(np.fft.fft2(signal)*(-1j*ky)/(ky*ky+.18*kx*kx+.035)).real
    # Fixed scale keeps base, expanded field and band at compatible amplitude.
    z=(1.35*np.tanh(z*4/1.35)).astype(np.float32)
    z-=np.median(z)
    return z


def traced_height(rgb,logical,detail):
    n=detail['name'];h,w=rgb.shape[:2]
    if n=='CITYF01':return brick_height(rgb,logical)
    if n=='SNOW3':return snow_height(rgb,logical)
    if n not in NAMES:raise ValueError('Unknown traced material '+n)
    f=Field(w,h,1 if n in ('QMET10','QMET33','METALF12') else 2 if max(w,h)<=128 else 1)
    if n=='ADEL_W39':_door(f)
    elif n=='IKTCR05B':_crate(f)
    elif n=='IKWALL28':_runes(f)
    elif n=='PANBOOK':_books(f)
    elif n in ('TECHG','OTECH6'):_vent(f)
    elif n.startswith('QTECH'):_machine(f,n)
    else:_metal(f,n)
    return f.z
