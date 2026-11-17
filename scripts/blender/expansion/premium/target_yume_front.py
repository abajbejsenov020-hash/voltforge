"""Apply bounded Y10/Osprey front-family correction to the premium generator."""
from pathlib import Path
import json
D=Path(__file__).parent;p=D/'build.py';s=p.read_text()
old="if kind=='nami':\n  for sy"
new="""if c.get('frontFamily') in ['y10','osprey']:
  # Both references fold behind a long twin telescopic fork. No sport C-arm neck.
  for sy in [-1,1]:
   p.profile('YUME low folding chassis cheek',[(dl*.27,dz-.025),(F-.13,dz+.055),(F-.09,dz+.18),(F-.15,dz+.18),(dl*.23,dz+.025)],.017,p.paint,y=sy*.065)
  p.rod('YUME low fold pivot',(F-.14,-.095,dz+.075),(F-.14,.095,dz+.075),.022,p.edge)
 elif kind=='nami':
  for sy"""
assert old in s;s=s.replace(old,new,1)
old="if kind=='wolf':\n  for sy in [-1,1]:\n   y=sy*.075"
new="""if c.get('frontFamily') in ['y10','osprey']:
  family=c['frontFamily'];forkTop=c['forkTop'];forkY=.067;topForkX=F-.085
  for sy in [-1,1]:
   yy=sy*forkY
   if family=='y10':
    # Y10: long exposed silver stanchions, short black lowers and bellows.
    p.rod('Y10 long polished front stanchion',(F-.035,yy,r+.16),(topForkX,yy,forkTop),.0155,p.silver,'Steering',32)
    p.rod('Y10 black lower fork leg',(F,yy,r),(F-.035,yy,r+.18),.0225,p.black,'Steering',32)
    for j in range(10):
     z=r+.10+j*.009;xx=F-.035*(z-r)/.18;p.rod('Y10 lower fork rubber bellows',(xx,yy,z-.003),(xx,yy,z+.003),.026,p.grip,'Steering',24)
   else:
    # Osprey: tall dark hydraulic housings, short exposed pistons and cast dropouts.
    p.rod('Osprey long black fork housing',(F-.045,yy,r+.19),(topForkX,yy,forkTop),.022,p.edge,'Steering',32)
    p.rod('Osprey exposed lower piston',(F-.045,yy,r+.055),(F-.045,yy,r+.23),.014,p.silver,'Steering',32)
    p.profile('Osprey short cast axle dropout',[(F-.075,r+.18),(F-.030,r+.15),(F+.018,r+.020),(F-.008,r-.022),(F-.055,r+.015)],.025,p.paint,'Steering',yy)
   for z in [r+.24,forkTop-.012]:
    xx=F-.035+(topForkX-F+.035)*(z-r-.16)/(forkTop-r-.16)
    p.rod('YUME fork collar',(xx,yy,z-.012),(xx,yy,z+.012),.027,p.black,'Steering',32)
   p.bolt('YUME fork top adjuster',(topForkX,yy,forkTop+.021),.009,'Steering',axis='Z')
  for z in [r+.24,forkTop-.005]:
   xx=F-.035+(topForkX-F+.035)*(z-r-.16)/(forkTop-r-.16);p.cube('YUME twin fork crown bridge',(xx,0,z),(.075,.20,.024),p.edge,'Steering',.005)
  p.rod('YUME central lower steering sleeve',(F-.11,0,dz+.08),(topForkX-.015,0,forkTop),.026,p.black,'Steering',32)
  if family=='y10':
   sx=topForkX-.01;topx=topForkX-.10;neck=forkTop
   mid=(forkTop+H)*.54;mx=sx+(topx-sx)*(mid-forkTop)/(H-forkTop)
   p.rod('Y10 lower branded upper mast',(sx,0,forkTop),(mx,0,mid),.025,p.paint,'Steering',32)
   p.rod('Y10 telescopic upper handlebar post',(mx,0,mid),(topx,0,H),.0175,p.black,'Steering',32)
   p.rod('Y10 upper mast telescopic collar',(mx,0,mid-.012),(mx,0,mid+.012),.031,p.edge,'Steering',32)
   p.label('Y10 vertical YUME marking','YUME',((sx+mx)/2,-.027,(forkTop+mid)/2),.025,p.white,'Steering',angle=pi/2+.15)
  else:
   sx=topForkX-.005;topx=F-.075;neck=forkTop
   a=(sx,forkTop+.015);b=(sx-.09,H-.45);d=(topx,H-.035)
   # Two joined, angular open box sections reproduce Osprey's kinked slotted mast.
   for title,u,v in [('Osprey lower reverse-rake mast',a,b),('Osprey upper windowed mast',b,d)]:
    p.window_arm(title,u,v,.087,p.paint,0);p.parts[-1].parent=p.groups['Steering']
   dx=d[0]-b[0];dzm=d[1]-b[1];ll=(dx*dx+dzm*dzm)**.5;nx=dzm/ll;nz=-dx/ll
   for j in range(1,7):
    t=j/7;xx=b[0]+dx*t;zz=b[1]+dzm*t
    p.profile('Osprey mast slot cross web',[(xx-nx*.022,zz-nz*.022-.004),(xx+nx*.022,zz+nz*.022-.004),(xx+nx*.022,zz+nz*.022+.004),(xx-nx*.022,zz-nz*.022+.004)],.087,p.paint,'Steering')
   p.rod('Osprey handlebar mast cap',(topx,0,H-.04),(topx,0,H),.024,p.edge,'Steering',32)
   p.label('Osprey diagonal YUME marking','YUME',((a[0]+b[0])/2,-.046,(a[1]+b[1])/2),.022,p.white,'Steering',angle=pi/2+.35)
  p.cube('YUME paired headlamp cross bracket',(F-.045,0,c['lampZ']-.025),(.11,.21,.020),p.edge,'Steering',.004)
 elif kind=='wolf':
  for sy in [-1,1]:
   y=sy*.075"""
assert old in s;s=s.replace(old,new,1)
s=s.replace("if kind!='wolf' and kind!='seated':", "if kind!='wolf' and kind!='seated' and not c.get('frontFamily'):",1)
old=" # Model-specific lamp placement, twin beam Wolf/X, high module others, no invented high lamps."
new=""" if c.get('mirrorRise'):
  for sy in [-1,1]:
   yy=sy*bar*.40;p.curve('Osprey mirror stalk',[(topx,sy*bar*.27,H+.025),(topx+.015,yy,H+.10),(topx,yy,H+c['mirrorRise']-.025)],.004,p.black,'Steering')
   p.cube('Osprey rectangular mirror housing',(topx,yy,H+c['mirrorRise']),(.018,.082,.048),p.black,'Steering',.007)
   p.cube('Osprey silver mirror glass',(topx-.010,yy,H+c['mirrorRise']),(.002,.068,.036),p.silver,'Steering',.004)
 # Model-specific lamp placement, twin beam Wolf/X, high module others, no invented high lamps."""
assert old in s;s=s.replace(old,new,1)
s=s.replace("lampR=c.get('lampRadius',.031)", "lampR=c.get('lampRadius',.031)\n if c.get('frontFamily'):lx=F+.005;lz=c['lampZ']")
old="p.rod('Headlight housing',(lx-.02,y,lz),(lx+.017,y,lz),lampR,p.black,'Steering',32);p.rod('Headlight optical lens',(lx+.018,y,lz),(lx+.020,y,lz),lampR*.84,p.lens,'Steering',32)"
new="""if c.get('lampShape')=='square':
   p.cube('Osprey square headlight enclosure',(lx,sy*.073 if False else y,lz),(.042,.050,.046),p.black,'Steering',.006)
   p.rod('Osprey square lamp circular optic',(lx+.022,y,lz),(lx+.024,y,lz),.017,p.lens,'Steering',32)
  else:
   p.rod('Headlight housing',(lx-.02,y,lz),(lx+.017,y,lz),lampR,p.black,'Steering',32)
   if c.get('lampShape')=='round-gold':p.rod('Y10 amber metal lamp bezel',(lx+.018,y,lz),(lx+.021,y,lz),lampR*.96,p.gold,'Steering',32)
   p.rod('Headlight optical lens',(lx+.022,y,lz),(lx+.024,y,lz),lampR*.80,p.lens,'Steering',32)"""
assert old in s;s=s.replace(old,new,1)
s=s.replace("cam.rotation_euler=(Vector((0,0,H*.49))-cam.location)", "cam.rotation_euler=(Vector((0,0,(H+c.get('mirrorRise',0))*.49))-cam.location)")
s=s.replace("max(H+.32,wb+r*2+.26)","max(H+c.get('mirrorRise',0)+.32,wb+r*2+.26)")
p.write_text(s)
p=D/'configs.json';c=json.load(open(p))
c['Yume Y10'].update(kind='yume-y10',frontFamily='y10',forkTop=.79,lampZ=.59,lampRadius=.034,lampShape='round-gold',notes='Exact Y10 front: tall polished paired telescopic fork stanchions with black lower bellows, three fork crown/collar levels, twin amber-rim round lamps mounted midway up the fork, and a separate slender telescopic YUME upper mast. Black box battery chassis retained.')
c['Yume Osprey'].update(frontFamily='osprey',forkTop=.77,lampZ=.78,lampShape='square',mirrorRise=.14,notes='Exact Osprey front: long dark twin hydraulic fork housings and short polished lower pistons with cast axle dropouts, paired square headlights at the upper fork crown, reverse-rake lower mast joined to a tall slotted angular upper mast, and two rectangular mirrors. Wide battery chassis retained.')
p.write_text(json.dumps(c,indent=2))
