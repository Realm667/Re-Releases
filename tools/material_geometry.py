"""Authored, signed material geometry in map units; diffuse colors are not heights.

Coordinates refer to original texels. Bevels, complete cylindrical bodies and
recessed panels are evaluated at twice the source resolution for small artwork.
Related skins resolve to the same construction, before normal differentiation.
"""
import numpy as np
from PIL import Image, ImageFilter

ALIASES = {}
def family(canonical, *skins):
    for name in (canonical,)+skins: ALIASES[name]=canonical
family('ADEL_M02','ADEL_F59','ADEL_V99')
family('ADEL_M03','ADEL_V98')
family('CITYF14','CITYF15','CITYF16','QFLAT03')
family('IKCRATE1','IKCRATE2','IKCRATE3')
family('QCRATE1','QCRATE2')
family('IKWALL15','IKWALL18')
family('IKWALL86','IKWALL88')
family('QCITY01','QCITY02','QCITY03','QCITY04')
family('QTECH20','QTECH33')
family('QTECH25','QTECH26','QTECH34')
family('QTECH28','QTECH28B')
family('QTECH05','TECHF2')
family('TECHG','OTECH6')

class Field:
    def __init__(self,w,h,scale=2,base=0):
        self.w,self.h,self.scale=w,h,scale
        self.y,self.x=np.mgrid[:h*scale,:w*scale].astype(np.float32)
        self.x=(self.x+.5)/scale;self.y=(self.y+.5)/scale
        self.z=np.full(self.x.shape,base,np.float32)
        self.clip=1
    def put(self,d,z,bevel=.7):
        a=np.clip(d/max(bevel,.01),0,1)*self.clip
        a=a*a*(3-2*a)
        self.z=self.z*(1-a)+z*a
    def rect(self,x0,y0,x1,y1,z,bevel=.7):
        self.put(np.minimum.reduce([self.x-x0,x1-self.x,self.y-y0,y1-self.y]),z,bevel)
    def poly(self,points,z,bevel=.7):
        inside=np.zeros(self.x.shape,bool);dist=np.full(self.x.shape,1e9,np.float32)
        for (ax,ay),(bx,by) in zip(points,points[1:]+points[:1]):
            vx,vy=bx-ax,by-ay
            t=np.clip(((self.x-ax)*vx+(self.y-ay)*vy)/max(vx*vx+vy*vy,.001),0,1)
            dist=np.minimum(dist,np.hypot(self.x-ax-t*vx,self.y-ay-t*vy))
            if by!=ay:inside^=((ay>self.y)!=(by>self.y))&(self.x<(bx-ax)*(self.y-ay)/(by-ay)+ax)
        self.put(np.where(inside,dist,-dist),z,bevel)
    def wire(self,points,r,z,base,bevel=.3):
        dist=np.full(self.x.shape,1e9,np.float32)
        for (ax,ay),(bx,by) in zip(points,points[1:]):
            vx,vy=bx-ax,by-ay;t=np.clip(((self.x-ax)*vx+(self.y-ay)*vy)/max(vx*vx+vy*vy,.001),0,1)
            dist=np.minimum(dist,np.hypot(self.x-ax-t*vx,self.y-ay-t*vy))
        body=base+(z-base)*np.sqrt(np.clip(1-(dist/r)**2,0,1))
        self.put(r-dist,body,bevel)
    def rivet(self,x,y,r=1.4,z=.8,base=0):
        d=np.hypot(self.x-x,self.y-y)
        self.put(r-d,base+(z-base)*np.sqrt(np.clip(1-(d/r)**2,0,1)),.25)
    def bolts(self,xs,ys,r=1.1,z=.65,base=0):
        for y in ys:
            for x in xs:self.rivet(x,y,r,z,base)
    def groove(self,points,r=.55,z=-1):
        self.wire(points,r,z,z)
    def grid(self,pw,ph,depth=-1.2,bevel=.65,stagger=False,rounding=0):
        self.z[:]=depth
        for row,y in enumerate(range(-ph,self.h+ph,ph)):
            offset=pw/2 if stagger and (y//ph)%2 else 0
            for x in np.arange(-pw-offset,self.w+pw,pw):
                self.rect(x+.65,y+.65,x+pw-.65,y+ph-.65,0,rounding or bevel)
    def pipes(self,ys,r=2,z=0,base=-2,x0=-2,x1=None):
        for y in ys:self.wire([(x0,y),(self.w+2 if x1 is None else x1,y)],r,z,base)


def _wood(f,n):
    w,h=f.w,f.h
    # Quiet plank faces at zero, narrow cuts, complete hardware above them.
    for x in ([0,32,64] if n=='WOOD8' else [0,12,24,40,52,64]):
        f.groove([(x,-2),(x,h+2)],.55,-.8)
    if n=='WOOD8':return
    rails=[]
    if n=='ADEL_D11':
        # Native artwork: the dark inner frame seams occupy columns 7/8
        # and 55/56. Do not cut relief into the outer frame at column 3.
        f.rect(7,16,57,80,-1,.5);f.rect(9,17,55,79,0,.6)
        for y0,y1 in [(-2,16),(80,98)]:
            f.rect(-1,y0,65,y1,1.2,.65)  # Continuous across tile boundaries.
            f.bolts([16,48],[(max(0,y0)+min(h,y1))/2],1.6,2.0,1.2)
        # Row 57 is the upper bevel, 58..63 the plate, 64 its painted
        # shadow. The fastener is central, not at the ends of this strap.
        f.rect(15,57,49,64,1.2,1.0)
        f.rivet(32,61,1.9,2.0,1.2)
        return
    elif n in ('ADEL_G02','ADEL_G03'):
        y=8 if n=='ADEL_G02' else 32
        rails=[(0,-2,64,y)]
        f.poly([(23,y-1),(40,y-1),(40,y+11),(35,y+16),(35,y+39),(40,y+47),(33,y+58),(25,y+47),(29,y+39),(29,y+16),(23,y+11)],1.5,.8)
        f.bolts([32],[y+8,y+46],2.0,2.2,1.5)
    elif n=='ADEL_GXX':rails=[(0,48,64,66)]
    elif n=='ADEL_S69':rails=[(0,-2,64,16),(0,80,64,98)]
    elif n=='QWOOD1':rails=[(0,y,64,y+16) for y in range(0,h,64)]
    elif n=='QWOOD4':rails=[(0,y-8,64,y+8) for y in range(0,h+1,64)]
    elif n=='ADEL_W39':
        f.z[:]=-.5
        for x in (0,64,128):f.rect(x-4,-2,x+4,130,0)
        for y in (0,128):f.rect(-2,y-5,130,y+5,0)
        for pts in [[(5,123),(59,22)],[(69,22),(123,123)]]:f.wire(pts,4.0,1.0,.4,.7)
        for x in (55,73):f.rect(x-2,53,x+2,89,1.6);f.bolts([x],[57,84],1.3,2.2,1.6)
        return
    for x0,y0,x1,y1 in rails:
        f.rect(x0-1,y0,x1+1,y1,1.2,.65)
        f.bolts([16,48],[(max(0,y0)+min(h,y1))/2],1.6,2.0,1.2)


def _crate(f,n):
    if n=='IKTCR05B':
        f.z[:]=0;f.rect(6,6,58,58,-1.4,1)
        for x0,y0,x1,y1 in [(8,8,56,14),(8,50,56,56),(8,8,14,56),(50,8,56,56)]:f.rect(x0,y0,x1,y1,.6)
        f.poly([(13,13),(23,13),(51,42),(51,51),(42,51),(13,23)],1.0,1)
        return
    pw=64;ph=32 if n=='IKCRATE6' else 64
    for y in range(0,f.h,ph):
        for x in range(0,f.w,pw):
            if n=='IKCRATE1':
                f.rect(x+3,y+3,x+61,y+54,-.65,1)
                f.poly([(x+9,y+6),(x+55,y+6),(x+60,y+16),(x+4,y+16)],-2.5,1)
                f.rect(x+5,y+18,x+59,y+52,0,.8)
                f.rect(x+1,y+55,x+63,y+62,-2.0,.5)
                for bx in range(4,64,5):f.rect(x+bx,y+55,x+bx+1.2,y+62,-.2,.25)
                f.bolts([x+2,x+62],[y+3,y+51],.9,.55)
            elif n=='IKCRATE6':
                f.rect(x+7,y+3,x+57,y+29,-.5,.8)
                f.bolts([x+4,x+60],[y+5,y+27],1,.6)
            else:
                f.rect(x+4,y+10,x+60,y+47,-.8,.8)
                f.rect(x+7,y+13,x+57,y+44,-.3,.8)
                for l,r in [(4,29),(35,60)]:f.rect(x+l,y+55,x+r,y+61,-2,.6)
                f.bolts([x+3,x+61],[y+7,y+48],.8,.6)


def _computer(f,n):
    # Cabinets use flat boards, sockets and straight cylindrical components.
    f.z[:]=-1.4
    for y in range(0,f.h,64):
        f.rect(-1,y-1,65,y+3,0,.5);f.rect(-1,y+60,65,y+65,0,.5)
        for x in (0,55):
            f.rect(x,y,x+9,y+64,-.25,.5)
            for yy in range(6,61,7):f.rect(x+1,y+yy,x+8,y+yy+4,.25,.5)
        if n in ('QCOMP1','QCOMP2','QCOMP3','QCOMP6'):
            if n=='QCOMP3':
                for x in range(18,48,5):f.wire([(x,y+5),(x,y+27)],1.5,.5,-1.4)
            else:
                f.rect(15,y+4,49,y+28,-.25,.7);f.rect(18,y+7,46,y+24,-1.0,.5)
                if n=='QCOMP1':
                    for x in (17,31,43):f.rect(x,y+5,x+11,y+13,-.15,.5)
                    for x in (14,25,37):f.rect(x,y+18,x+10,y+26,-.25,.4)
            f.rect(19,y+33,46,y+43,-.5,.5)
            for x in (27,34):f.rect(x,y+34,x+5,y+40,.1,.4)
            for yy in range(47,60,4):f.rect(15,y+yy,49,y+yy+2.2,-.15,.45)
        elif n=='QCOMP4':
            f.rect(29,y,35,y+64,0,.5)
            for yy in range(3,64,16):
                for x in (4,36):
                    f.rect(x,y+yy,x+24,y+yy+11,-2,.4)
                    f.rect(x+1,y+yy+2,x+23,y+yy+5,0,.5)
        elif n in ('QCOMP5','QCOMP8'):
            f.rect(14,y+2,45,y+30,-2,.6)
            for x in (18,23,28,33,39):f.wire([(x,y+5),(x,y+29)],1.25,0,-2)
            for x0,y0,x1,y1 in [(10,35,24,44),(26,34,44,43),(13,47,29,59),(34,46,51,58)]:f.rect(x0,y+y0,x1,y+y1,-.25,.5)
        elif n=='QCOMP7':
            for yy in (2,23,44):
                for x in (2,42):f.rect(x,y+yy,x+20,y+yy+15,0,.6);f.rect(x+3,y+yy+3,x+17,y+yy+12,-.6,.4)
            for x in (25,30,35):f.wire([(x,y+2),(x,y+60)],1,0,-1.4)
        else: # QTWALL07: offset modules and a right-hand vertical vent.
            for x0,y0,x1,y1 in [(4,6,20,21),(22,7,38,20),(15,25,34,39),(28,43,49,59),(5,45,22,57)]:
                f.rect(x0,y+y0,x1,y+y1,-.25,.6);f.rect(x0+3,y+y0+3,x1-3,y+y1-3,-1,.5)
            for yy in range(4,35,4):f.rect(41,y+yy,51,y+yy+2,-.1,.35)
            for x in (7,11):f.wire([(x,y+22),(x,y+42)],1,.1,-1.4)


def _girder(f,n):
    f.z[:]=0
    wide=n in ('QTECH20','QTECH35')
    left=[(-2,19),(5 if wide else 25,19),(32 if wide else 47,106),(21 if wide else 39,120),(-2,120)]
    if n=='QTECH21':left=[(-2,19),(5,19),(16,64),(8,77),(-2,77)]
    right=[(128-x,y) for x,y in left[::-1]]
    for poly in (left,right):
        f.poly(poly,-2.5,1.0)
        if n not in ('QTECH09','QTECH20','QTECH21','QTECH30','QTECH32','QTECH35'):
            old=f.z.copy();f.clip=(old<-1.8).astype(np.float32)
            f.pipes(range(29,121,13),1.3,-1.4,-2.5)
            f.clip=1
    if n=='QTECH21':f.groove([(64,-2),(64,130)],.65,-.8)
    # The dark girder remains at zero; its fasteners protrude.
    for y in range(28,112,12):
        x=(20 if wide else 38)+(y-28)*.20
        f.bolts([x,128-x],[y],1.4,.85)
    if n in ('QTECH27','QTECH31'):
        # Vertical frame variants have rectangular rather than V side cutouts.
        f.z[:]=0
        for a,b in ((-2,20),(112,130)):
            f.rect(a,20,b,120,-2.5,.8);f.clip=((f.x>a+1)&(f.x<b-1)&(f.y>21)&(f.y<119))
            f.pipes(range(29,121,13),1.3,-1.4,-2.5);f.clip=1
        f.rect(31,27,99,123,-3,.8);f.rect(34,30,96,94,-1,.7)
        for x in range(37,97,6):f.wire([(x,96),(x,120)],1.5,-.6,-3)
        f.rect(31,12,49,27,.35,.7);f.rect(34,15,46,24,-1,.5)
        f.bolts([25,103],range(9,123,12),1.3,.7)
    elif n=='QTECH30':
        f.rect(40,16,88,79,-3.2,.8)
        for x in range(43,86,5):f.wire([(x,19),(x,37),(x-3,44),(x+1,59),(x,76)],1,-.5,-3.2)
        f.rect(49,86,78,111,-2,.6)
        for x in (52,60,69):f.rect(x,89,x+5,107,-.6,.5)
    elif n=='QTECH32':
        f.poly([(30,16),(97,16),(85,78),(43,78)],-3,.8)
        f.clip=(f.z<-2.6)
        for y in range(21,77,9):
            for x in range(34,95,12):f.rect(x,y,x+9,y+6,-1,.4)
        f.clip=1
        for a,b in ((32,96),(50,77)):
            yy=4 if a==32 else 85;end=13 if a==32 else 110
            f.rect(a,yy,b,end,-3,.5)
            for x in range(a+3,b-1,6):f.wire([(x,yy+2),(x,end-2)],1.5,-.6,-3)


def _pipes(f,n):
    f.z[:]=-2
    if n=='FTUB2':
        for y in range(0,f.h,16):
            f.pipes([y+6],4.2,.6,-2)
            for x in (1,27,59):f.rect(x,y+2,x+1.6,y+10,1,.35)
            f.pipes([y+13],1.25,-.6,-2)
        f.rect(-1,-1,1,f.h+1,0,.3)
    elif n=='QTECH05':
        for oy in range(0,f.h,64):f.pipes([oy+y for y in (5,18,31,44,57)],4.1,.7,-2)
    elif n=='QTECH02':
        for y in range(0,f.h,64):
            f.pipes([y+5,y+17,y+31,y+45,y+57],3,.5,-2)
            f.pipes([y+24,y+38,y+52,y+63],1,-.5,-2)
    elif n=='TECHF1':
        # Traced centerlines follow the bends visible in the 64px original.
        paths=[[(0,2),(23,2),(28,0),(43,0),(48,2),(64,2)],[(0,6),(10,6),(14,4),(27,4),(35,7),(46,7),(52,4),(64,4)],[(0,10),(24,10),(29,8),(33,8),(39,11),(54,11),(57,8),(64,8)],[(0,14),(16,14),(22,12),(38,12),(45,16),(64,16)],[(0,18),(26,18),(31,16),(39,16),(45,19),(54,19),(58,17),(64,17)],[(0,22),(19,22),(24,24),(48,24),(54,20),(64,20)],[(0,27),(12,27),(19,25),(34,25),(41,28),(52,28),(57,25),(64,25)],[(0,31),(18,31),(24,29),(29,29),(37,33),(49,33),(56,30),(64,30)],[(0,35),(8,35),(13,38),(25,38),(32,35),(47,35),(54,39),(64,39)],[(0,40),(18,40),(24,43),(37,43),(45,40),(64,40)],[(0,45),(13,45),(19,48),(26,48),(35,45),(51,45),(58,48),(64,48)],[(0,50),(11,50),(16,53),(35,53),(44,50),(54,50),(60,52),(64,52)],[(0,56),(17,56),(23,59),(36,59),(44,55),(64,55)],[(0,62),(9,62),(14,60),(27,60),(34,62),(50,62),(56,59),(64,59)]]
        for pts in paths:
            f.wire(pts,.85,0,-1.2,.2)
            f.wire([(x,y+2) for x,y in pts],.6,-.2,-1.2,.18)
        f.rect(-1,-1,1,f.h+1,0,.3)
    elif n=='QTECH01':
        for y in range(0,f.h,64):
            f.pipes([y+5],3.5,.5,-2)
            for yy in range(13,64,4):
                bend=2 if (yy//4)%2 else -2
                f.wire([(-2,y+yy),(19,y+yy),(25,y+yy+bend),(46,y+yy+bend),(53,y+yy),(66,y+yy)],1,0,-2)
    else: # QTWALL08
        f.pipes(range(5,f.h+5,13),3.8,.6,-2)
        for y in range(0,f.h,64):
            f.rect(15,y+4,49,y+31,1,.7);f.rect(19,y+8,45,y+27,-.8,.5)
            for x in range(23,43,5):f.wire([(x,y+11),(x,y+24)],1,.1,-.8)


def authored_height(rgb,logical,detail):
    requested=detail['name'];n=ALIASES.get(requested,requested)
    h,w=rgb.shape[:2];scale=2 if max(w,h)<=128 else 1
    if requested=='FTUB3':
        a=authored_height(np.rot90(rgb,-1),logical,dict(name='FTUB2'))
        return np.rot90(a)
    f=Field(w,h,scale)
    if w>128 or h>128:
        return expanded_height(rgb,logical,requested)
    if n in ('ADEL_D11','ADEL_G02','ADEL_G03','ADEL_GXX','ADEL_S69','ADEL_W39','QWOOD1','QWOOD4','WOOD8'):_wood(f,n)
    elif n in ('IKCRATE1','IKCRATE6','IKTCR05B','QCRATE1'):_crate(f,n)
    elif n.startswith('QCOMP') or n=='QTWALL07':_computer(f,n)
    elif n in ('QTECH09','QTECH20','QTECH21','QTECH25','QTECH27','QTECH30','QTECH31','QTECH32','QTECH35'):_girder(f,n)
    elif n in ('FTUB2','QTECH01','QTECH02','QTECH05','TECHF1','QTWALL08'):_pipes(f,n)
    elif n in ('ADEL_M02','ADEL_M03','ADEL_M06','ADEL_R90'):
        pw=32 if n=='ADEL_M03' else (16 if n=='ADEL_R90' else 64)
        f.grid(pw,16 if n=='ADEL_R90' else 32,-1.0,.8)
        if n=='ADEL_M06':
            for y in range(16,h,32):f.rect(-2,y-1,66,y+2,-.45,.5)
    elif n=='ADEL_B15':
        for y,x in zip(range(0,h,16),[32,40,24,56,32,40,16,56]):
            f.groove([(-2,y),(66,y)],.9,-2)
            f.groove([(x,y),(x,y+16)],.8,-2)
    elif n in ('QCITY01','QWWALL'):
        f.grid(32,16 if n=='ADEL_B15' else (8 if n=='QCITY01' else 32),-2 if n!='QWWALL' else -3.5,1,True,4 if n=='QWWALL' else 1)
    elif n in ('CITYF14','CITYF20','ADEL_Q60','QCITY16'):
        return stone_height(rgb,logical,n,scale)
    elif n in ('IKWALL25','IKWALL26','IKWALL28','IKWALL30','IKWALL31','IKWALL86','OTECH2','QTECH28'):
        pw=64 if n in ('IKWALL25','IKWALL30','OTECH2','QTECH28') else 32
        ph=128 if n=='IKWALL86' else (64 if n in ('IKWALL31','QTECH28') else 32)
        f.grid(pw,ph,-1,.65)
        for y in range(0,h,ph):
            for x in range(0,w,pw):f.bolts([x+4,x+pw-5],list(range(y+6,y+ph-2,12)) if n=='QTECH28' else [y+4,y+ph-5],1.15,.65)
        if n=='IKWALL28':
            for y in range(0,h,64):
                for pts in [[(22,9),(9,9),(9,16),(22,16),(22,23),(9,23)],[(53,10),(45,10),(45,21),(53,21),(53,18)],[(11,54),(11,42)],[(11,48),(20,48),(20,42)],[(42,54),(42,42),(53,42),(53,54)],[(42,46),(53,46)]]:
                    f.groove([(x,yy+y) for x,yy in pts],1.05,-1.5)
    elif n=='IKWALL10':
        f.rect(15,-2,49,130,-.4,.7)
        for a,b in ((1,14),(50,63)):
            f.rect(a,-2,b,130,-2,.5)
            for y in range(2,h,8):f.rect(a,y,b,y+4,0,.5)
        f.bolts([19,45],range(6,h,32),1,.6)
    elif n=='TECHG':
        for oy in range(0,h,64):
            f.rect(3,oy+4,w-3,oy+61,-2.5,.7)
            for y in range(6,61,6):f.rect(4,oy+y,w-4,oy+y+1.7,0,.45)
    elif n=='IKWALL15':
        y0,y1=(16,112) if n=='IKWALL15' else (4,h-4)
        f.rect(4,y0,w-4,y1,-2.5,.7)
        for y in np.arange(y0+2,y1,4):f.rect(5,y,w-5,y+2.1,-.4,.5)
        if n=='IKWALL15':
            for a,b in ((1,14),(114,127)):
                f.rect(2,a,126,b,-1.8,.4)
                for x in range(5,127,5):f.rect(x,a,x+1.5,b,0,.3)
    elif n in ('IKWALL64','IKWALL69'):
        if n=='IKWALL64':
            for x in (0,64):f.rect(x+14,14,x+50,114,-4,1.7);f.bolts([x+6,x+58],[6,122],1.4,.7)
        else:
            f.poly([(48,24),(79,24),(103,49),(103,80),(78,104),(49,104),(24,79),(24,48)],-4,1.8)
            f.bolts([8,120],[8,120],1.5,.8)
    elif n in ('IKWALL21','IKWALL23','IKWALL50','IKWALL54','IKWALL55'):
        if n.startswith('IKWALL2'):
            ps=[[(-2,16),(24,16),(31,32),(10,79),(-2,79)],[(130,16),(104,16),(97,32),(118,79),(130,79)],[(56,46),(72,46),(95,96),(87,112),(40,112),(32,96)]]
            if n=='IKWALL23':ps=[[(19,16),(24,16),(31,32),(19,53)],[(109,16),(104,16),(97,32),(109,53)],ps[2]]
        else:ps=[[(49,13),(79,13),(116,82),(99,116),(29,116),(12,82)]]
        for p in ps:
            f.poly(p,-3,1);mask=f.z<-2.2;f.clip=mask
            if n=='IKWALL50':
                f.z=np.where(mask,-2.2,f.z)
                for y in (31,47,63):f.rect(-2,y,130,y+1.5,-2.8,.3)
            elif n=='IKWALL55':f.pipes([21,50,81,109],5,-1.1,-3)
            else:f.pipes(range(19,120,8),2.8,-1.1,-3)
            f.clip=1
        if n=='IKWALL54':
            f.rect(38,49,89,85,-.6,1);f.rect(42,54,85,79,-1.2,.6)
        f.bolts([7,121],[7,121],1.5,.7)
    elif n in ('QTECH07','QTECH08'):
        if n=='QTECH07':
            for y in range(0,h,16):f.bolts([8,24],[y+7],2.0,1)
        else:
            for y in range(0,h,32):
                for x in (7,19):f.rect(x,y+3,x+7,y+29,-2,1.2)
    elif n=='PLATF2':
        # Cut apertures first; cables belong to the cavity, under the lattice.
        for x in (7,53):
            for a,b in ((13,29),(31,49)):
                f.rect(x,a,x+6,b,-3.2,.55)
                f.clip=(f.x>x+.5)&(f.x<x+5.5)&(f.y>a+.5)&(f.y<b-.5)
                f.wire([(x+3,a),(x+3,b)],1.3,-1.1,-3.2);f.clip=1
                for yy in range(a+2,b,4):f.rect(x,yy,x+6,yy+1,0,.25)
        for x,ys in [(18,[6,14,19,24,33,42,47,56]),(31,[6,14,24,28,36,41,47]),(42,[5,10,18,24,32,43,54])]:
            for y in ys:f.rect(x,y,x+5,y+3,-2.2,.5)
    elif n in ('QFLAT09','SFLOOR2','SFLOOR3','SFLOOR5','SFLOOR6'):
        f.grid(64 if n=='SFLOOR5' else 32,64 if n=='SFLOOR5' else 32,-.9,.45)
        # Restrained complete stamped treads, no stone-like luminance crowns.
        for y in range(3,64,6):
            for x in range(2,64,6):
                xx=x+(3 if (y//6)%2 else 0)
                f.wire([(xx,y+2),(xx+2,y)],.5,.35,0,.2)
    elif n=='PANBOOK':
        f.rect(10,16,54,108,-4,1)
        for y in (44,57,70,83,95,107):f.rect(10,y-2,54,y,0,.5)
        for a,b in ((30,43),(46,55),(59,68),(72,81),(85,93),(97,105)):
            for x in range(13,51,5):f.rect(x,a,x+3.5,b,-1.3,.6)
        f.rect(2,2,62,15,0,.6);f.rect(2,109,62,126,0,.6)
    elif n in ('QTWALL10','QTWALL11','QTWALL12','TEKWALL4'):
        return technical_contours(rgb,logical,scale,n)
    else:raise ValueError('Missing authored geometry: '+requested)
    return f.z


def stone_height(rgb,logical,n,scale):
    h,w=rgb.shape[:2];f=Field(w,h,scale,base=-2.7)
    if n=='CITYF14':
        # The shared CITYF14/15/16 slab layout, including its branching cracks.
        rows=[(0,16,[-17,0,32,49,64]),(16,32,[-16,16,48,80]),(32,48,[-16,0,32,64]),(48,64,[-16,16,48,80])]
        for a,b,edges in rows:
            for l,r in zip(edges,edges[1:]):f.rect(l+.6,a+.7,r-.6,b-.5,0,1.1)
        for pts in [[(31,0),(32,6),(39,10),(42,16)],[(0,26),(8,29),(15,36),(14,45)],[(33,33),(39,37),(47,37),(52,43),(64,45)],[(1,50),(7,55),(6,63)],[(38,50),(33,54),(37,60),(36,64)]]:f.groove(pts,.55,-1.3)
    else:
        # Individually staggered rustic courses; flat cores and rounded shoulders.
        if n=='ADEL_Q60':
            courses=[(0,10,[-8,9,32,48,72]),(10,18,[-8,16,31,48,72]),(18,25,[-8,14,25,42,54,72]),(25,32,[-8,20,35,53,72]),(32,44,[-8,16,32,40,64,80]),(44,50,[-8,18,34,46,72]),(50,64,[-8,14,32,48,72]),(64,74,[-8,12,28,46,72]),(74,82,[-8,18,34,48,60,76]),(82,88,[-8,14,32,46,64,80]),(88,96,[-8,17,28,44,55,72]),(96,110,[-8,19,34,51,72]),(110,119,[-8,16,33,49,72]),(119,128,[-8,13,29,47,62,80])]
        else:
            courses=[(0,10,[-9,16,32,48,72]),(10,18,[-9,17,35,58,80]),(18,30,[-16,8,24,42,58,80]),(30,46,[-8,15,33,54,76]),(46,54,[-9,20,32,47,76]),(54,64,[-9,15,32,51,75])]
        for oy in range(0,h,128 if n=='ADEL_Q60' else 64):
            for row,(a,b,edges) in enumerate(courses):
                for j,(l,r) in enumerate(zip(edges,edges[1:])):
                    cut=1.2+(j+row)%2*.4
                    f.poly([(l+cut,oy+a+.5),(r-1.1,oy+a+.7),(r-.4,oy+a+2),(r-.8,oy+b-1),(l+1,oy+b-.5),(l+.4,oy+b-2)],0,2.0)
    return f.z


def technical_contours(rgb,logical,scale,n):
    h,w=rgb.shape[:2];f=Field(w,h,scale,base=-1.8)
    if n=='TEKWALL4':
        # Connected pipe runs, closed housings and inset wiring, traced in texels.
        paths=[(2,[(4,-2),(4,51),(10,57),(10,69)]),(2,[(24,-2),(24,16),(26,20),(26,78)]),(1.8,[(31,-2),(31,11),(37,15),(37,51),(41,58)]),(2,[(59,-2),(59,48),(54,57),(54,85),(58,92),(58,131)]),(2,[(84,-2),(84,39),(89,45),(89,76),(84,82),(84,111)]),(2,[(92,-2),(92,31),(97,36),(97,48)]),(2,[(112,-2),(112,35),(120,40),(120,49),(128,54)]),(2,[(128,85),(115,97),(115,108),(113,111),(113,131)]),(1.8,[(7,77),(7,106),(12,112),(34,112)]),(1.5,[(22,80),(22,119),(28,124),(39,124)]),(2,[(126,65),(123,65),(123,80),(115,88),(111,99)]),(1.5,[(66,105),(66,129)]),(1.5,[(99,87),(99,117),(103,122),(103,131)])]
        for r,pts in paths:f.wire(pts,r,.8,-1.8)
        for x0,y0,x1,y1 in [(6,38,21,73),(29,77,37,119),(60,65,73,90),(69,2,80,48),(98,6,108,35),(100,56,116,83),(67,108,77,127)]:
            f.rect(x0,y0,x1,y1,-.2,1);f.rect(x0+2,y0+2,x1-2,y1-2,-2.5,.7)
            for x in np.arange(x0+3,x1-2,3):f.wire([(x,y0+4),(x,y1-4)],.8,-.6,-2.5)
        f.poly([(40,75),(51,83),(51,116),(39,109)],0,.8)
        for y in range(81,111,7):f.wire([(41,y),(49,y+6)],.7,.45,0)
        f.rect(-1,-1,1,h+1,0,.35)
    else:
        for y in range(0,h,64):
            f.rect(-1,y-1,w+1,y+3,0,.6)
            if n in ('QTWALL11','QTWALL12'):
                for x0,x1 in ((3,17),(47,61)):
                    f.rect(x0,y+5,x1,y+16,0,.5);f.rect(x0+2,y+7,x1-2,y+14,-1,.4)
                    for yy in range(20,62,5):f.rect(x0,y+yy,x1,y+yy+2.5,-.15,.5)
                f.rect(19,y+8,45,y+63,-2.5,.7)
                for x in (23,39):f.wire([(x,y+12),(x,y+58)],2.0,.1,-2.5)
                if n=='QTWALL11':
                    f.rect(30,y+12,34,y+58,-.8,.5)
                    for yy in range(16,59,8):f.rect(30,y+yy,34,y+yy+3,-.25,.4)
                else:
                    for yy in range(14,60,9):f.rect(27,y+yy,37,y+yy+5,-.3,.5)
            else: # QTWALL10 has distinct rectangular assemblies across its width.
                for x0,y0,x1,y1 in [(4,9,32,32),(40,22,67,51),(91,9,123,33),(9,40,33,58),(74,35,87,61),(99,43,121,59)]:
                    f.rect(x0,y+y0,x1,y+y1,0,.7);f.rect(x0+2,y+y0+2,x1-2,y+y1-2,-1.4,.6)
                    for yy in range(y0+4,y1-2,4):f.rect(x0+3,y+yy,x1-3,y+yy+1.5,-.5,.3)
                for x in (36,70,92):f.wire([(x,y+6),(x,y+59)],1.3,-.1,-1.8)
    return f.z


def _mask_distance(mask,steps):
    d=np.where(mask,steps+1.,0).astype(np.float32)
    for _ in range(steps):
        d=np.minimum.reduce([d,np.roll(d,1,0)+1,np.roll(d,-1,0)+1,np.roll(d,1,1)+1,np.roll(d,-1,1)+1])
    return d


def expanded_height(rgb,logical,n):
    """Segment the additional artwork's component boundaries, not its shading.

    Closing reconnects lit and shadowed parts before the body gets a flat core.
    No independent contrast stretch and no illumination value becomes height.
    The small originals instead use explicit, reviewed construction geometry.
    """
    h,w=rgb.shape[:2]
    if n=='ADEL_B15':
        f=Field(w,h,1);f.grid(32,16,-2,1,True);return f.z
    lum=rgb.astype(np.float32)@np.array([.2126,.7152,.0722],np.float32)
    density=.5*(w/logical[0]+h/logical[1])
    stone=n in ('ADEL_Q60','CITYF20')
    # Dark continuous mortar/clearance networks separate complete components.
    cutoff=26 if n=='ADEL_Q60' else (23 if n=='CITYF20' else 22)
    mask=Image.fromarray(np.uint8(lum>cutoff)*255)
    radius=1 if stone else 2
    mask=mask.filter(ImageFilter.MaxFilter(radius*2+1)).filter(ImageFilter.MinFilter(radius*2+1))
    dist=_mask_distance(np.asarray(mask)>0,max(4,int(3*density)))
    bevel=max(1,1.5*density if stone else .65*density)
    t=np.clip(dist/bevel,0,1);t=t*t*(3-2*t)
    return (-2.4 if stone else -1.6)*(1-t)
