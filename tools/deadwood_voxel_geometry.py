"""Hand-authored branch networks: native x/right, y/back, z/down, radius.
Every limb is a tapered round solid swept along a 3D centerline. No silhouette
extrusion, distance-field inflation, or view-dependent geometry is used.
"""
import math
import numpy as np

# The native reference coordinates locate the major forks and trunk bends.
PLANS={}
TREE_PATHS={
'dry-tree-a':[
 [(42,0,117,13),(40,1,99,11),(35,0,78,9),(38,1,60,8),(44,2,40,6),(43,4,20,4),(49,5,2,.8)],
 [(36,0,72,7),(28,-3,55,5),(18,-7,40,3),(11,-10,23,.8)],
 [(40,1,53,6),(56,5,42,5),(73,9,35,3),(92,14,27,.7)],
 [(57,5,42,4),(66,5,28,2),(78,7,15,.7)],
 [(43,4,25,3),(32,8,15,2),(25,12,4,.65)],
 [(20,-6,44,2.5),(14,-15,37,1.5),(5,-23,31,.6)]],
'dry-tree-b':[
 [(80,0,117,16),(86,3,96,15),(76,5,74,14),(62,3,56,12),(50,0,47,10),(31,-2,54,8),(13,-4,44,6),(6,-6,31,.8)],
 [(13,-4,44,6),(26,-1,33,5),(49,6,28,4),(70,11,21,2),(85,16,22,.7)],
 [(56,7,26,2.8),(55,11,15,2),(46,12,3,.7)],
 [(26,-1,33,3),(28,-6,24,1),(20,-10,18,.6)],
 [(28,-2,53,5),(16,-9,61,2),(4,-13,68,.65)],
 [(77,5,78,5),(90,20,67,3),(103,31,59,.7)]],
'dry-tree-c':[
 [(66,0,116,19),(59,-2,99,16),(70,0,79,16),(70,4,60,17),(65,6,45,14),(58,7,35,10),(41,8,32,8),(32,7,23,5),(27,6,4,.8)],
 [(66,5,48,11),(80,10,35,8),(85,13,22,5),(88,14,9,3),(99,16,1,.7)],
 [(61,4,57,11),(43,-5,60,9),(29,-10,53,6),(24,-12,40,3),(10,-14,38,.7)],
 [(83,12,27,4),(99,17,25,2),(110,21,19,.6)],
 [(35,8,28,4),(44,14,18,2),(43,20,4,.6)],
 [(33,-9,57,4),(21,-19,54,2),(16,-25,45,.7)]],
'charred-tree-a':[
 [(43,0,117,16),(39,1,97,14),(39,0,77,12),(34,-1,55,10),(38,1,35,8),(34,2,19,5),(25,4,1,.8)],
 [(36,0,46,7),(48,9,31,6),(59,16,23,3),(68,22,11,.7)],
 [(35,0,64,7),(24,-6,49,5),(20,-11,37,2),(17,-12,31,.7)],
 [(24,-6,49,3),(12,-10,46,2),(7,-15,40,.6)],
 [(43,5,35,5),(52,1,19,3),(55,-3,8,.7)],
 [(52,12,28,3),(69,20,28,1.5),(78,24,32,.7)]],
'charred-tree-b':[
 [(68,0,116,21),(74,2,97,19),(89,3,80,18),(89,0,57,16),(77,-2,39,14),(57,-5,31,11),(42,-6,28,8),(29,-8,40,5),(12,-9,41,.7)],
 [(72,-3,37,8),(62,-1,24,6),(51,2,17,4),(41,4,3,.8)],
 [(54,1,19,4),(57,9,9,2),(66,14,1,.6)],
 [(90,1,61,6),(103,9,49,4),(111,14,38,1.5),(113,16,33,.6)],
 [(29,-8,40,3),(20,-16,43,2),(3,-22,46,.6)],
 [(73,1,96,8),(58,-7,90,5),(48,-15,80,.7)]],
'charred-tree-c':[
 [(65,0,116,18),(74,0,96,15),(77,-2,78,15),(70,-4,59,13),(57,-3,48,10),(44,-1,65,8),(36,1,76,6),(18,3,66,6),(5,5,56,4),(4,6,39,.7)],
 [(5,5,56,5),(19,11,45,4),(40,17,36,4),(61,21,25,4),(62,21,9,.7)],
 [(46,18,33,3),(31,26,25,2),(14,31,19,.6)],
 [(60,21,25,3),(80,24,23,2),(97,29,18,.65)],
 [(73,-3,73,6),(87,-15,64,3),(98,-22,49,.65)],
 [(20,3,67,3),(11,-7,76,2),(3,-13,82,.6)]],
'frozen-tree-a':[
 [(34,0,120,11),(34,1,101,10),(46,3,81,9),(39,3,67,9),(29,0,51,7),(23,-2,32,6),(29,-2,20,4),(39,0,8,2),(44,2,7,.65)],
 [(25,-2,30,4),(16,-6,16,3),(8,-9,4,.6)],
 [(24,-1,41,5),(17,-8,33,3),(7,-14,30,2),(1,-17,25,.6)],
 [(37,3,66,6),(45,10,55,5),(58,17,46,4),(63,20,37,2),(61,23,29,.65)],
 [(61,19,41,3),(72,25,37,2),(80,31,31,.65)],
 [(50,12,54,3),(64,2,55,2),(79,-8,59,.65)]],
'frozen-tree-b':[
 [(30,0,121,13),(38,0,104,12),(43,2,90,10),(57,4,77,11),(72,4,65,11),(85,4,54,10),(95,6,54,8),(111,9,58,6),(117,10,69,5),(129,11,74,4),(144,15,67,2),(153,16,63,.7)],
 [(80,4,59,8),(80,6,42,6),(77,7,31,5),(86,9,20,4),(78,10,15,3),(66,13,12,.7)],
 [(84,9,22,3),(96,13,10,2),(105,16,3,.65)],
 [(85,9,21,3),(105,6,19,2),(122,3,16,.65)],
 [(71,4,66,7),(62,-5,52,5),(42,-13,48,4),(30,-18,37,3),(16,-24,29,.7)],
 [(41,-13,48,3),(27,-24,52,2),(13,-31,50,.65)],
 [(62,4,75,6),(82,-9,79,5),(99,-15,86,3),(118,-23,84,.7)]],
'frozen-tree-c':[
 [(36,0,121,14),(34,1,105,12),(40,2,88,11),(49,2,74,10),(43,2,59,10),(39,0,45,9),(39,-1,35,7),(27,-2,28,5),(17,-3,16,3),(19,-3,2,.65)],
 [(44,2,69,7),(59,11,59,6),(68,15,46,4),(82,20,38,2),(91,25,31,.7)],
 [(64,13,51,4),(71,4,53,3),(84,-5,53,2),(92,-11,48,.65)],
 [(26,-2,27,4),(15,-10,32,3),(7,-15,29,2),(0,-18,26,.65)],
 [(38,0,45,4),(27,12,42,3),(16,25,49,.7)],
 [(18,-3,17,2),(27,-8,12,1),(31,-12,9,.6)]]}

def smooth(path):
 pts=np.array(path,dtype=float);out=[]
 for j in range(len(pts)-1):
  p0=pts[max(0,j-1)];p1=pts[j];p2=pts[j+1];p3=pts[min(len(pts)-1,j+2)]
  n=max(2,int(np.linalg.norm(p2[:3]-p1[:3])*1.7))
  for t in np.linspace(0,1,n,endpoint=False):
   p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
   p[3]=max(.6,p[3]);out.append(p)
 out.append(pts[-1]);return out

def geometry(p,w,h,left,name,palette):
 tree='tree' in name;variant=ord(name[-1])-97;frozen=name.startswith('frozen');charred=name.startswith('charred')
 pal=np.frombuffer(palette,dtype=np.uint8).reshape(256,3).astype(float)
 # A native bark strip from the lower trunk supplies every side of every limb.
 bark=[(x,z,c) for (x,z),c in p.items() if z>h*.5 and z<h*.93 and abs(x-left)<w*.19 and not (frozen and pal[c].max()-pal[c].min()<38 and pal[c].mean()>90)]
 if not bark:bark=[(x,z,c) for (x,z),c in p.items()]
 bcoords=np.array([(x,z) for x,z,c in bark]);bcolors=np.array([c for x,z,c in bark],dtype=np.uint8)
 x0=int(bcoords[:,0].min());x1=int(bcoords[:,0].max());z0=int(bcoords[:,1].min());z1=int(bcoords[:,1].max())
 # Continuous wrapping lookup, filled with nearest valid bark texels at holes.
 tile=np.zeros((z1-z0+1,x1-x0+1),dtype=np.uint8)
 for z in range(z0,z1+1):
  for x in range(x0,x1+1):tile[z-z0,x-x0]=bcolors[((bcoords-(x,z))**2).sum(1).argmin()]
 paths=[list(path) for path in TREE_PATHS[name]] if tree else []
 if tree:
  main=paths[0]
  # Independently placed front and back limbs share real junctions with the trunk.
  # They open up the silhouette when seen along the reference image plane.
  attach=main[min(3,len(main)-2)];x,y,z,r=attach
  paths += [[(x,y,z,r*.62),(x+8,y-20,z-10,r*.40),(x+13,y-37,z-26,2.5),(x+8,y-46,z-35,.65)],
            [(x,y,z,r*.58),(x-8,y+20,z-11,r*.36),(x-6,y+36,z-23,2),(x-13,y+44,z-39,.65)]]
  for path in list(paths[1:]):
   if len(path)<3:continue
   q=path[-2];end=path[-1]
   paths.append([q,(q[0]+(end[0]-q[0])*.15,q[1]-9,q[2]-6,max(.8,q[3]*.65)),(q[0]-4,q[1]-17,q[2]-10,.6)])
 else:
  if variant==0:
   paths=[[(left,0,h-7,11),(left-2,0,h-18,8),(left-4,0,12,6),(left-7,1,2,.8)],
          [(left-3,0,17,5),(left+3,6,10,2),(left+4,9,3,.6)]]
  elif variant==2:
   paths=[[(left,0,h-6,10),(left-3,0,h-18,7),(left-6,1,12,5),(left-9,2,1,.8)],
          [(left-3,0,19,5),(left+1,-5,11,2),(left+3,-7,5,.6)]]
 # Unequal buttress roots go all around each trunk and stay rooted on the floor.
 for i,angle in enumerate((8,55,103,155,203,252,302,342)):
  a=math.radians(angle+variant*11);length=min(w*.44,39 if tree else 28)*(0.76+.2*math.sin(i*2.3+variant))
  rr=(7 if tree else 4.5)*(1+.16*math.sin(i))
  paths.append([(left,0,h-(15 if tree else 9),rr+2),(left+math.cos(a)*length*.48,math.sin(a)*length*.48,h-7,rr*.7),
                (left+math.cos(a)*length*.85,math.sin(a)*length*.85,h-3,rr*.35),(left+math.cos(a)*length,math.sin(a)*length,h-1,.65)])
 PLANS[name]={'paths':paths,'tile':tile.tolist(),'w':w,'h':h,'left':left,'hollow':not tree and variant==1,'frozen':frozen,'indices':sorted(set(p.values()))}
 volume={};owner={}
 def stamp(cx,cy,cz,r,tag):
  x0=max(0,math.floor(cx-r-1));x1=min(w-1,math.ceil(cx+r+1));z0=max(0,math.floor(cz-r-1));z1=min(h-1,math.ceil(cz+r+1))
  if x1<x0 or z1<z0:return
  xx,yy,zz=np.mgrid[x0:x1+1,math.floor(cy-r-1):math.ceil(cy+r+1)+1,z0:z1+1]
  dx=xx-cx;dy=yy-cy;dz=zz-cz
  # Shallow longitudinal furrows, below one source pixel in amplitude.
  theta=np.arctan2(dy,dx);rough=.42*np.sin(theta*9+cz*.045+variant)+.22*np.sin(theta*19-cz*.075)
  valid=dx*dx+dy*dy+dz*dz<=(r+rough)**2
  for x,y,z in zip(xx[valid],yy[valid],zz[valid]):
   k=(int(x),int(y),int(z));volume[k]=1
   # Local cylindrical texture basis follows this limb, including the rear.
   owner[k]=(cx,cy,tag)
 for tag,path in enumerate(paths):
  for cx,cy,cz,r in smooth(path):stamp(cx,cy,cz,r,tag)
 if not tree and variant==1:
  # Hollow broken trunk: a continuous 360-degree wall, jagged rim and deep well.
  radius=min(w*.20,18);cx=left;cy=0
  for x in range(max(0,int(cx-radius-6)),min(w,int(cx+radius+7))):
   for y in range(-math.ceil(radius+5),math.ceil(radius+5)+1):
    theta=math.atan2(y-cy,x-cx);rad=math.hypot(x-cx,y-cy)
    lip=6+2*math.sin(theta*3+variant)+2*math.sin(theta*7)
    for z in range(max(0,int(lip)),h):
     outer=radius+max(0,(z/h-.6))*13+.6*math.sin(theta*11+z*.08)
     inner=radius-4.5-max(0,z/h-.30)*4
     if rad<=outer and (rad>=inner or z>h*.75):
      k=(x,y,z);volume[k]=1;owner[k]=(cx,cy,0)
 # Final material assignment uses a cylindrical bark coordinate per branch.
 vox={}
 snow=sorted({c for c in p.values() if pal[c].mean()>95 and pal[c].max()-pal[c].min()<45},key=lambda c:pal[c].mean())
 for (x,y,z) in volume:
  cx,cy,tag=owner[x,y,z];theta=math.atan2(y-cy,x-cx)
  u=round(theta/(2*math.pi)*max(16,tile.shape[1])+tag*7+math.sin(z*.08)*1.1)%tile.shape[1]
  vv=(z+tag*13)%tile.shape[0];c=int(tile[vv,u])
  # Snow rests on exposed upward-facing bark; the entire rear is still wood.
  if frozen and snow:
   exposed=(x,y,z-1) not in volume and (x,y,z+1) in volume
   broad=all((x+dx,y+dy,z+2) in volume for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
   if exposed and broad:c=snow[(x//3+y//4+z)%len(snow)]
  # Keep the tiny source ember as a narrow bark seam on charred broken stump C.
  if charred and not tree and variant==2 and abs(x-left+3)<=1 and y<0 and 10<z<23:
   candidates=[c for c in set(p.values()) if pal[c,0]>pal[c,1]*1.6 and pal[c,0]>110]
   if candidates:c=candidates[(z//2)%len(candidates)]
  vox[x,y,z]=c
 # No separately floating crumbs: retain the face/edge connected trunk mass.
 if vox:
  remaining=set(vox);components=[]
  while remaining:
   seed=remaining.pop();todo=[seed];comp=[seed]
   while todo:
    x,y,z=todo.pop()
    for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
     q=(x+dx,y+dy,z+dz)
     if q in remaining:remaining.remove(q);todo.append(q);comp.append(q)
   components.append(comp)
  keep=max(components,key=len);vox={k:vox[k] for k in keep}
 ymin=min(y for x,y,z in vox);ymax=max(y for x,y,z in vox)
 return {(x,y-ymin,z):c for (x,y,z),c in vox.items()},(w,ymax-ymin+1,h),(left,-ymin,h)
