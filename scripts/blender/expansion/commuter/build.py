"""Exact-reference photo-guided catalog reconstructions, Blender4.5. Run background --threads2.
All dimensions are photographic approximations in meters; hidden internal surfaces inferred.
"""
import bpy,bmesh,math,json,sys,os
from pathlib import Path
from mathutils import Vector,Matrix
from math import sin,cos,pi
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'scripts/blender/expansion/commuter';exec((HERE/'primitives.py').read_text())
exec((HERE/'kukirin_g.py').read_text())
O=ROOT/'artifacts/blender/expansion/commuter';OUT=ROOT/'apps/web/public/models/expansion/commuter';BL=ROOT/'assets/blender/expansion/commuter'

def config(e):
 n=e['name'];m=n.split(' ',1)[1];c=dict(family='rigid commuter',r=.127,wide=.028,wb=.91,dl=.49,dw=.17,dz=.17,h=1.20,bar=.52,stem='round',fork='rigid',rear='rigid',motor='rear',disc='rear',lamp='high',halo=False,body=(.065,.073,.08),accent=(.95,.25,.015),seat=False,kick=False,signal=False)
 if n.startswith('Xiaomi'):
  c.update(family='Xiaomi curved-neck commuter',motor='front',r=.108,wide=.024,wb=.86,dl=.50,dw=.15,dz=.14,h=1.14,bar=.43,body=(.075,.085,.09),accent=(.68,.025,.015))
  if m in ['M365 Pro','Pro 2']:c.update(wb=.90,dl=.55,h=1.18)
  if m=='Mi 3':c.update(accent=(.015,.36,.74),h=1.14)
  if m in ['4','4 Pro','4 Ultra','5','5 Pro','5 Max']:c.update(r=.127,wb=.96,dl=.55,dw=.17,h=1.24,bar=.52)
  if m=='4 Lite':c.update(wb=.89,h=1.14)
  if m=='4 Pro':c.update(r=.127,wb=.94,dw=.18,dz=.17,h=1.24)
  if m in ['4 Ultra','5','5 Pro','5 Max']:c.update(family='Xiaomi suspension commuter',motor='rear',disc='none',fork='telescopic',dz=.21,wb=.97)
  if m in ['4 Ultra','5 Pro','5 Max']:c.update(rear='shortarm',h=1.27,dw=.195,dl=.56)
  if m=='4 Ultra':c.update(fork='swing',wb=1.01,r=.127,accent=(.87,.58,.025))
  if m=='5 Max':c.update(body=(.13,.15,.17),accent=(.68,.36,.09),signal=True)
 elif n.startswith('Segway Ninebot'):
  m=n.removeprefix('Segway Ninebot ');c.update(family='Ninebot rigid commuter',accent=(.98,.56,.015),disc='none',signal=m.startswith(('F2','F3','Max G3')))
  if m.startswith('Max G30'):c.update(wb=.91,dl=.51,dw=.18,dz=.19,h=1.20)
  if m=='Max G30LP':c.update(wb=.86,h=1.13,body=(.38,.42,.44))
  if m=='Max G2':c.update(family='Ninebot MAX hydraulic suspension',fork='telescopic',rear='twinshock',h=1.26,wb=.96,dz=.22,bar=.57,signal=True)
  if m=='Max G3':c.update(family='Ninebot MAX G3 dual hydraulic',fork='twinfork',rear='shortarm',h=1.38,wb=1.01,r=.14,dz=.24,bar=.59,disc='both',accent=(.63,.025,.01),body=(.055,.065,.07),signal=True)
  if m.startswith('F2'):c.update(wb=.92,dl=.50,dw=.17,dz=.18,h=1.21,bar=.57,disc='front')
  if m=='F2 Pro':c.update(fork='telescopic',dz=.19)
  if m.startswith('F3'):c.update(family='Ninebot F3 suspension',fork='twinfork',rear='shortarm',wb=.98,dl=.52,dw=.18,dz=.21,h=1.31,bar=.59,disc='front',accent=(.18,.26,.36))
  if m.startswith('E2'):c.update(r=.108,wb=.86,dl=.46,dw=.15,dz=.15,h=1.14,bar=.45,motor='front',body=(.07,.085,.11),accent=(.45,.6,.8))
  if m=='E2 Pro':c.update(r=.127,motor='rear',wb=.88,h=1.2)
  if m.startswith('ES'):c.update(family='Ninebot ES stem-battery',r=.10,wb=.86,dl=.48,dw=.15,dz=.14,h=1.13,fork='telescopic',rear='shortarm' if m!='ES1' else 'rigid',motor='front',accent=(.7,.025,.02),stem='battery')
  if m in ['P65','P100S']:c.update(family='Segway P wide-deck',r=.133,wide=.035,wb=1.02,dl=.58,dw=.22,dz=.23,h=1.28,bar=.64,stem='wide',kick=True,disc='front' if m=='P65' else 'both',signal=True,accent=(.9,.31,.025))
  if m=='P100S':c.update(fork='swing',rear='swing',h=1.28,dz=.28,wb=1.08)
  if m in ['GT1','GT2','GT3']:c.update(family='Segway GT double-wishbone superscooter',r=.14,wide=.046,wb=1.23,dl=.62,dw=.28,dz=.32,h=1.31,bar=.66,stem='wide',fork='wishbone',rear='swing',disc='both',motor='both' if m=='GT2' else 'rear',kick=True,signal=True,body=(.19,.22,.24),accent=(.72,.025,.018))
  if m=='GT3':c.update(wb=1.17,r=.14,dz=.29,h=1.38,body=(.045,.055,.07),accent=(.76,.06,.025))
  if m=='ZT3 Pro':c.update(family='Segway ZT offroad X-headlight',r=.14,wide=.042,wb=1.04,dl=.56,dw=.23,dz=.27,h=1.34,bar=.64,stem='wide',fork='twinfork',rear='shortarm',disc='both',kick=True,signal=True,body=(.075,.085,.075),accent=(.8,.035,.012),lamp='x')
 elif n.startswith('NIU'):
  c.update(family='NIU curved-neck halo commuter',halo=True,disc='both',kick=True,wb=.91,dl=.51,dw=.18,dz=.17,h=1.2,bar=.54,body=(.06,.068,.075),accent=(.9,.35,.01))
  if m=='KQi1 Pro':c.update(halo=False,disc='none',kick=False,r=.115,dw=.16,bar=.48,wb=.88,lamp='console')
  if m=='KQi2 Pro':c.update(disc='none',kick=False,body=(.065,.075,.085),wb=.89,dw=.17)
  if m=='KQi3 Sport':c.update(body=(.55,.59,.61),r=.121)
  if m=='KQi3 Pro':c.update(r=.121)
  if m=='KQi3 Max':c.update(r=.127,wb=.95,dl=.55,accent=(.65,.025,.015),body=(.035,.04,.045))
  if m=='KQi Air':c.update(family='NIU Air carbon frame',halo=False,kick=False,dw=.17,dl=.49,wb=.88,dz=.15,bar=.54,disc='front',body=(.26,.28,.29))
  if '300' in m:c.update(family='NIU 300 hydraulic fork',fork='twinfork',r=.133,wb=.96,dl=.54,dw=.20,dz=.19,h=1.26,halo=False,accent=(.66,.025,.016) if m.endswith('X') else (.9,.38,.015))
 elif n.startswith(('KuKirin','Kugoo','Ausom','Joyor','iENYRID','Bogist')) or 'iX' in n:
  c.update(family='telescopic suspension scooter',wb=1.0,dl=.55,dw=.21,dz=.26,h=1.27,bar=.62,wide=.04,stem='telescopic',fork='twinfork',rear='twinshock',disc='both',kick=True,lamp='lowround',accent=(.84,.045,.012))
  if n.startswith('KuKirin'):
   c['accent']=(.98,.26,.008)
   if m=='G2 VMP':c.update(family='KuKirin G2 open headstock',stem='square',fork='swing',rear='swing',h=1.22,wb=.94,body=(.19,.22,.24),lamp='console')
   if m=='G2 Ultra':c.update(family='KuKirin Ultra gray swingarms',stem='square',fork='swing',rear='swing',wb=.96,dl=.57,motor='both',body=(.22,.24,.25),lamp='console')
   if m=='G3':c.update(family='KuKirin G3 orange cast arms',stem='square',fork='swing',rear='swing',wb=1.03,dl=.58,body=(.025,.035,.038),lamp='console')
   if m=='G4 Max':c.update(family='KuKirin G4 Max twin stanchion',r=.152,wide=.049,wb=1.11,dw=.25,dl=.66,dz=.31,h=1.36,bar=.70,motor='both',stem='telescopic',fork='longfork',lamp='lowround',body=(.035,.04,.045),seat=False)
   if m=='M4':c.update(seat=True,lamp='lowround',accent=(.70,.025,.015),r=.127,dl=.55,h=1.20)
   if m=='M4 Pro':c.update(accent=(.75,.025,.015),dl=.58,h=1.24)
   if m in ['S1 Max','S3 Pro']:c.update(family='KuKirin compact commuter',r=.105,wide=.023,wb=.83,dl=.46,dw=.145,dz=.15,h=1.10,bar=.45,stem='telescopic' if m=='S3 Pro' else 'round',fork='rigid',rear='rigid',disc='none',lamp='console',motor='front' if m=='S3 Pro' else 'rear',kick=False,accent=(.93,.56,.02) if m=='S1 Max' else (.4,.4,.38))
   if m=='A1':c.update(family='KuKirin A1 silver chassis',body=(.52,.57,.59),stem='square',fork='shortarm',rear='shortarm',wb=.90,dz=.22,h=1.30,bar=.58,lamp='console')
   if m=='T3':c.update(family='KuKirin T3 compact swingarms',stem='square',fork='swing',rear='swing',wb=.95,h=1.25,body=(.18,.20,.21),lamp='console')
   if m=='C1 Pro':c.update(family='KuKirin seated C1 transport',r=.178,wide=.04,wb=1.16,seat=True,h=1.28,dl=.65,dw=.23,body=(.15,.17,.19))
  elif n.startswith('Ausom'):
   c.update(family='Ausom angular swingarm',fork='swing',rear='swing',stem='square',lamp='highsquare',body=(.11,.13,.16),accent=(.92,.52,.03),bar=.69,h=1.38,wb=1.0)
   if m=='L1':c.update(family='Ausom L1 steel open headstock',wb=.99,dw=.19,dl=.515,h=1.415,body=(.17,.19,.20),lamp='stem',stem='telescopic')
   if m=='L2':c.update(family='Ausom L2 solid gray arms',wb=1.01,dw=.20,dl=.54,body=(.18,.20,.22),stem='square')
   if m=='L2 Max':c.update(family='Ausom L2 Max adjustable stem',wb=1.02,dl=.55,dw=.20,body=(.14,.16,.18),stem='telescopic',h=1.43)
   if 'Gosoul' in m:c.update(family='Ausom Gosoul ribbed deck',motor='both' if 'Pro' in m else 'rear',body=(.14,.17,.21),wb=1.02,lamp='highsquare',dw=.23)
   if 'K20' in m:c.update(family='Ausom K20 gold rims',motor='both',wb=1.02,dw=.23,body=(.10,.12,.14))
   if m=='SR1':c.update(family='Ausom SR1 open wishbone',motor='both',wb=1.02,dw=.22,dl=.55,h=1.36,stem='telescopic',lamp='highsquare')
   if m in ['Leopard','Gallop','DT1','DT1 Pro']:c.update(family='Ausom legacy twin swingarms',motor='both' if m in ['Gallop','DT1 Pro'] else 'rear',stem='telescopic',lamp='lowround',body=(.07,.09,.11))
  elif n.startswith('Joyor'):c.update(family='Joyor orange swingarm',fork='swing',rear='swing',body=(.05,.06,.065),accent=(.96,.25,.025),wb=1.01,lamp='lowround')
  elif n.startswith('iENYRID'):
   c.update(family='iENYRID M4 fork and red coil',seat=True,lamp='lowround',body=(.055,.065,.07),accent=(.93,.23,.025),wb=.96,h=1.23)
   if m=='ES1':c.update(family='iENYRID ES1 yellow swingarm',seat=False,stem='telescopic',fork='swing',rear='swing',wb=1.03,motor='both',accent=(.98,.72,.015),lamp='highsquare',h=1.31)
   if m=='ES10':c.update(motor='both',wb=1.03,seat=True)
  elif n.startswith('Bogist'):c.update(family='Bogist seated full suspension',seat=True,wb=1.02,h=1.20,lamp='lowround',body=(.07,.08,.085),accent=(.72,.025,.015))
  elif n.startswith('Kugoo'):
   if m=='G-Booster':c.update(family='Kugoo G-Booster wishbone',fork='swing',rear='swing',stem='round',motor='both',wb=1.05,h=1.30,lamp='twinsquare',accent=(.65,.02,.01),body=(.02,.025,.028))
   elif m in ['S1','S1 Pro','S3','S3 Pro']:c.update(family='Kugoo compact stem-battery',r=.10,wide=.024,wb=.83,dl=.44,dw=.15,dz=.145,h=1.1,bar=.43,fork='telescopic',rear='shortarm',motor='front',disc='none',lamp='console',kick=False)
   elif m=='M2 Pro':c.update(family='Kugoo M2 Pro commuter',r=.108,wide=.027,wb=.87,dl=.48,dw=.17,dz=.17,h=1.11,bar=.50,fork='rigid',rear='rigid',motor='front',disc='rear',stem='round',lamp='high',kick=False)
   elif m=='G-Max':c.update(family='Kugoo G-Max wide neck',fork='rigid',rear='rigid',stem='wide',r=.127,wb=.94,h=1.15,dz=.18,dl=.50,dw=.15,lamp='high',disc='rear',motor='front',kick=False)
  else:c.update(family='iScooter iX double coil',wb=.96,dz=.25,h=1.25,accent=(.75,.02,.015),seat=False,stem='telescopic',lamp='lowround')
  if n=='iScooter iX6':c.update(family='iScooter iX6 cast gel suspension',fork='shortarm',rear='shortarm',wb=1.05,h=1.32,r=.14,body=(.15,.17,.19),accent=(.8,.57,.015))
 if n=='Kugoo G1':c.update(family='Kugoo G1 dual red swingarm',motor='both',fork='swing',rear='swing',stem='telescopic',lamp='lowround',body=(.035,.045,.05),accent=(.70,.015,.015),seat=False)
 if n=='Kugoo G2 Pro':c.update(seat=True,wb=.96,r=.114,h=1.23,accent=(.7,.02,.015))
 if n in ['Kugoo S1','Kugoo S1 Pro']:c['motor']='rear'
 if n=='Kugoo S1 Pro':c.update(family='Kugoo S1 Pro rear hub honeycomb',fork='telescopic',rear='rigid',accent=(.95,.40,.01))
 if n=='Bogist M5 Pro':c.update(family='Bogist M5 Pro teal seated carrier',r=.152,wide=.03,wb=.94,dl=.52,dw=.21,dz=.19,h=1.15,bar=.60,stem='round',fork='twinfork',rear='rigid',motor='rear',disc='both',lamp='midround',body=(.035,.045,.05),accent=(.015,.62,.45),seat=True,kick=False)
 if n=='iENYRID ES10':c.update(family='iENYRID ES10 blue long fork',fork='longfork',accent=(.015,.22,.62),lamp='twinround',wb=1.03,h=1.30,seat=True,motor='both')
 if n=='Joyor Y8-S':c.update(family='Joyor Y8-S twin telescopic fork',fork='twinfork',rear='twinshock',accent=(.09,.10,.12),wb=.96,h=1.19,dw=.18,dl=.52,kick=False,stem='telescopic')
 if n in ['Ausom K20 Pro','Ausom Gosoul 2 Pro']:c['motor']='rear'
 if n=='Ausom DT1 Pro':c.update(family='Ausom DT1 Pro yellow C-arm dual motor',motor='both',stem='square',fork='shortarm',rear='shortarm',lamp='stem',body=(.035,.045,.055),accent=(.98,.65,.005),h=1.30,bar=.63,wb=1.08,dl=.61,dw=.23,dz=.24)
 if n=='Ausom Gallop':c.update(family='Ausom Gallop yellow mast dual motor',motor='both',stem='square',fork='shortarm',rear='shortarm',lamp='highsquare',body=(.035,.045,.055),accent=(.98,.66,.005),h=1.30,wb=1.07,dl=.59,dw=.23)
 if n=='Ausom Leopard':c.update(family='Ausom Leopard yellow headstock',motor='rear',stem='telescopic',fork='swing',rear='swing',lamp='highsquare',body=(.045,.055,.065),accent=(.98,.65,.01),h=1.30,bar=.63,wb=1.0)
 c['solidArm']=(n in ['KuKirin G2 VMP','KuKirin G2 Ultra','KuKirin T3','KuKirin G3','Joyor S5','Joyor S8','Ausom Gallop','Ausom DT1 Pro'])
 if n in ['KuKirin G2 VMP','KuKirin G2 Ultra','KuKirin T3','KuKirin A1']:c.update(fork='shortarm',rear='shortarm')
 if n=='iScooter iX5':c.update(family='iScooter original iX5 twin fork red coil',r=.127,wide=.038,wb=.93,dl=.54,dw=.20,dz=.23,h=1.23,bar=.60,stem='telescopic',fork='twinfork',rear='twinshock',motor='rear',lamp='lowsquare',kick=False,body=(.035,.045,.055),accent=(.85,.015,.04))
 if n=='iScooter i9':c.update(family='iScooter i9 rigid commuter',r=.108,wide=.025,wb=.85,dl=.48,dw=.15,dz=.14,h=1.14,bar=.44,motor='front',disc='rear',accent=(.72,.015,.018))
 if n=='iScooter i10':c.update(family='iScooter i10 suspension commuter',fork='telescopic',rear='twinshock',wb=.90,dl=.51,dw=.18,dz=.19,h=1.22,accent=(.75,.02,.02))
 # Exterior wheel castings are independent of motor location. These references
 # have enclosed drums or narrow rim vents, not generic open alloy spokes.
 if n in ['Segway Ninebot E2','Segway Ninebot E2 Plus']:c.update(rearcover='vented',rearspokes=5)
 if n in ['Segway Ninebot E2 Pro','NIU KQi1 Pro']:c.update(frontcover='vented',frontspokes=8)
 if n in ['Segway Ninebot ES1','Segway Ninebot ES2','Segway Ninebot ES4']:c.update(rearcover='cast',rearspokes=3)
 if n in ['Segway Ninebot P65','Segway Ninebot P100S','Segway Ninebot GT1','Segway Ninebot GT3']:c['frontcover']='closed'
 c.update(KUKIRIN_G.get(e['key'],{}))
 return c

def wheel(x,parent,c):
 r=c['r'];wide=c['wide'];na=112;nb=18;v=[];f=[]
 for j in range(nb+1):
  t=-pi/2+pi*j/nb;y=wide*sin(t);rr=r-.026+.026*cos(t)
  for i in range(na):
   a=i*2*pi/na;phase=(i/na*(34 if c['fork']=='rigid' else 40)+.45*abs(sin(t)))%1;cut=.0025*max(0,1-abs(phase-.5)/.16)*cos(t);v.append((x+(rr-cut)*cos(a),y,r+(rr-cut)*sin(a)))
 for j in range(nb):
  for i in range(na):a=j*na+i;f.append((a,j*na+(i+1)%na,(j+1)*na+(i+1)%na,a+na))
 mesh(parent+' rubber tread',v,f,rubber,parent,True)
 if entry['key'] in KUKIRIN_G:
  kukirin_tread(x,c,parent)
 motor=c['motor']=='both' or c['motor']==('front' if parent=='FrontWheel' else 'rear');rim=r-.032
 rim_finish=steel if entry['key'] in KUKIRIN_G and entry['key']!='kukirin-g4-max' else silver
 for sy in [-1,1]:
  ring('Rim bead',x,sy*wide*.95,r,rim,rim-.007,.005,rim_finish,parent,n=40)
  if c['family'] in ['Ausom K20 gold rims','KuKirin G3 orange cast arms'] or 'KQi 300X' in entry['name']:ring('Rim color pinstripe',x,sy*(wide+.001),r,rim-.001,rim-.004,.001,accent,parent,n=56)
 if motor:
  rod('Enclosed hub motor',(x,-wide*.9,r),(x,wide*.9,r),rim*.88,black,'MotorMount',48)
  for sy in [-1,1]:
   ring('Motor circular seam',x,sy*(wide+.001),r,rim*.82,rim*.76,.003,steel,'MotorMount',40)
   for i in range(7):
    a=i*2*pi/7;bolt('Hub fastener',(x+rim*.7*cos(a),sy*(wide+.003),r+rim*.7*sin(a)),.0025,'MotorMount')
 elif c.get('frontcover' if parent=='FrontWheel' else 'rearcover') in ['closed','vented','cast']:
  style=c.get('frontcover' if parent=='FrontWheel' else 'rearcover');count=c.get('frontspokes' if parent=='FrontWheel' else 'rearspokes',5)
  if style in ['closed','vented']:
   radius=rim*(.98 if style=='closed' else .76)
   rod('Nonmotor sealed drum casting',(x,-wide*.91,r),(x,wide*.91,r),radius,black,parent,64)
   for sy in [-1,1]:ring('Drum molded circular seam',x,sy*(wide*.92),r,radius*.88,radius*.85,.002,edge,parent,56)
  if style in ['vented','cast']:
   rod('Nonmotor cast hub',(x,-wide*.92,r),(x,wide*.92,r),rim*.24,black,parent,32)
   for sy in [-1,1]:
    for i in range(count):
     a=i*2*pi/count
     rod('Broad black cast wheel rib',(x+rim*.18*cos(a),sy*wide*.75,r+rim*.18*sin(a)),(x+rim*.98*cos(a+.09),sy*wide*.85,r+rim*.98*sin(a+.09)),rim*(.11 if style=='cast' else .065),black,parent,12)
 elif entry['name']=='KuKirin G3':
  rod('Unpowered front enclosed alloy wheel cover',(x,-wide*.9,r),(x,wide*.9,r),rim*.98,black,parent,48)
  for sy in [-1,1]:ring('Front sealed wheel cover seam',x,sy*(wide+.001),r,rim*.82,rim*.75,.003,steel,parent,40)
 else:
  rod('Wheel hub',(x,-wide*.8,r),(x,wide*.8,r),.022,steel,parent,24)
  for sy in [-1,1]:
   for i in range(5 if entry['name'].startswith('NIU') else 6):
    a=i*2*pi/(5 if entry['name'].startswith('NIU') else 6);rod('Alloy open spoke',(x+.018*cos(a),sy*wide*.7,r+.018*sin(a)),(x+(rim-.008)*cos(a+.15),sy*wide*.83,r+(rim-.008)*sin(a+.15)),.010 if entry['name'].startswith('NIU') else .005,paint if entry['name'].startswith('NIU') else steel,parent,10)
 disc=c['disc']=='both' or c['disc']==('front' if parent=='FrontWheel' else 'rear')
 if disc:
  y=-wide-.014;ro=r*.61
  ring('Vented disc braking band',x,y,r,ro,ro*.78,.002,silver,parent,56)
  ring('Disc bolt carrier',x,y,r,ro*.43,ro*.31,.002,silver,parent,32)
  for i in range(6):
   a=i*2*pi/6;rod('Rotor open spider',(x+ro*.38*cos(a),y,r+ro*.38*sin(a)),(x+ro*.80*cos(a+.22),y,r+ro*.80*sin(a+.22)),.0028,silver,parent,8)
  cube('Disc caliper',(x-.037,y-.009,r+.04),(.027,.023,.038),black,parent,.004)
 for sy in [-1,1]:bolt('Axle nut',(x,sy*(wide+.025),r),.008,parent)


def generic_body(e,c,front,rear,R,dz,dl,dw,H,sx,tx,bar,lo,wide,offroad):
 profile('Battery enclosure silhouette',[(-dl/2-.03,dz-.065),(dl/2-.01,dz-.065),(dl/2+.03,dz-.017),(dl/2,dz+.006),(-dl/2,dz+.006),(-dl/2-.035,dz-.015)],dw,paint,b=.008)
 cube('Battery sealed tray',(-.03,0,dz-.035),(dl*.77,dw*.81,.045),black,'BatteryMount',.004);cube('Controller enclosure',(dl*.34,0,dz-.035),(.07,dw*.7,.035),edge,'ControllerMount',.003)
 cube('Deck traction mat',(-.01,0,dz+.012),(dl*.93,dw*.92,.013),grip,b=.009)
 for j in range(-4,5):curve('Deck grip channels',[(-dl*.45,j*dw*.09,dz+.019),(dl*.43,j*dw*.09,dz+.019)],.0008,black)
 for x in [-dl*.44,dl*.42]:
  for sy in [-1,1]:bolt('Deck flush screw',(x,sy*dw*.38,dz+.020),.003,axis='Z')
 # Neck geometry ranges from low curved Xiaomi/NIU tubes to open cast offroad headstocks.
 if e['name']=='Ausom Leopard':
  profile('Leopard signature yellow steering neck',[(dl*.35,dz-.025),(sx-.07,lo+.06),(sx+.025,lo+.04),(sx-.015,lo-.065),(dl*.40,dz-.05)],dw*.42,accent,b=.008)
 elif offroad:
  for sy in [-1,1]:
   window_arm('Open triangular steering headstock',(dl*.40,dz-.015),(sx-.012,lo+.04),.014,paint,sy*dw*.27)
  profile('Lower steering yoke',[(sx-.075,lo+.02),(sx+.025,lo+.04),(sx+.055,lo-.035),(sx-.035,lo-.07)],dw*.50,paint,b=.005)
 else:
  curve('Swept monocoque headstock',[(dl*.28,0,dz-.025),(dl*.45,0,dz-.013),(dl*.55,0,dz+.035),(sx-.015,0,dz+.14),(sx,0,lo+.02)],.038 if c['stem']!='wide' else .05,paint)
  if e['name'].startswith('NIU'):curve('NIU swept neck upper edge',[(dl*.25,0,dz+.008),(dl*.44,0,dz+.022),(sx-.05,0,dz+.13),(sx,0,lo+.025)],.030,paint)
 # Front suspension: physical distinct topology, not renamed components.
 fork=c['fork']
 if fork in ['rigid','telescopic','twinfork','longfork']:
  top=lo+.05 if fork!='longfork' else .66
  for sy in [-1,1]:
   y=sy*(wide+.024);rod('Front fork leg',(front,y,R),(sx+.02,y,top),.015 if fork=='rigid' else .020,paint,'Steering',20)
   if fork!='rigid':
    rod('Polished fork stanchion',(front+.003,y,R+.09),(sx+.02,y,top-.02),.010,silver,'Steering',20)
    if offroad:shock('Front fork coil',(front+.006,y,R+.05),(sx+.015,y,top-.03),.016,accent)
  rod('Fork crown',(sx+.02,-wide-.04,top),(sx+.02,wide+.04,top),.024,paint,'Steering')
 elif fork in ['swing','shortarm','wishbone']:
  pivot=(sx-.045,R+.145);end=(front,R)
  for sy in [-1,1]:
   y=sy*(wide+.028);
   if c['solidArm']:
    pts=[(sx-.095,R+.19),(sx-.055,R+.20),(front+.022,R+.037),(front+.017,R-.014),(front-.040,R-.028),(sx-.115,R+.105)]
    profile('G3 solid orange C-shaped front suspension',pts,.022,accent if e['name'] in ['KuKirin G3','Joyor S5','Joyor S8','Ausom Gallop','Ausom DT1 Pro'] else paint,y=y,b=.009)
   else:window_arm('Front cast suspension arm',pivot,end,.017,accent if ('Joyor' in e['name'] or 'ES1' in e['name']) else paint,y)
   rod('Front suspension upright',(sx,y,lo+.05),(pivot[0],y,pivot[1]),.020,paint,'Steering')
   if fork!='shortarm' and not c['solidArm'] and not e['name'].startswith('Ausom'):shock('Front shock',(sx-.045,sy*.028,lo-.015),(front-.02,sy*.028,R+.055),.016,accent if offroad else steel)
   if fork=='wishbone':window_arm('Upper wishbone',(sx-.02,R+.23),(front-.005,R+.13),.014,paint,y)
 # Rear stays / trailing suspension; paired springs only where visible.
 for sy in [-1,1]:
  y=sy*(wide+.025)
  if c['rear'] in ['swing','shortarm','twinshock']:
   start=(-dl*.42,dz-.035);end=(rear,R)
   if c['solidArm']:
    pts=[(-dl*.40,dz+.015),(-dl*.40-.025,dz+.033),(rear-.015,R+.026),(rear-.025,R-.017),(rear+.035,R-.030),(-dl*.38,dz-.055)]
    profile('G3 solid orange C-shaped rear suspension',pts,.022,accent if e['name'] in ['KuKirin G3','Joyor S5','Joyor S8','Ausom Gallop','Ausom DT1 Pro'] else paint,y=y,b=.009)
   else:window_arm('Rear cast trailing arm',start,end,.018,accent if e['name'].startswith(('Joyor','iENYRID')) else paint,y)
   if c['rear']!='shortarm' and not c['solidArm']:shock('Rear suspension',(-dl*.46,y,dz+.005),(rear+.04,y,R+.045),.016,accent if c['rear']=='twinshock' else steel)
  else:rod('Rigid rear axle stay',(-dl*.42,y,dz-.035),(rear,y,R),.013,paint)
 fender('Front molded mudguard',front,R+.012,(wide*2)+.017,angular=offroad and e['name']!='KuKirin G3')
 fender('Rear molded mudguard',rear,R+.014,(wide*2)+.021,angular=offroad and e['name']!='KuKirin G3',rear=True)
 if c['kick']:
  profile('Raised rear heel support',[(-dl*.45,dz+.015),(-dl*.62,dz+.105),(-dl*.59,dz+.122),(-dl*.37,dz+.04)],dw*.68,paint,b=.007)
  for j in range(5):rod('Heel grip rib',(-dl*.41-j*.014,-dw*.24,dz+.045+j*.014),(-dl*.41-j*.014,dw*.24,dz+.045+j*.014),.0025,grip,n=8)
 # Folding joint, stem and clamp. +X is front; stem top slopes rearward.
 cube('Folding hinge housing',(sx,0,lo+.025),(.075,.075,.11),paint,'Steering',.007)
 rod('Folding hinge pivot',(sx,-.045,lo),(sx,.045,lo),.014,silver,'Steering')
 cube('Folding latch handle',(sx-.037,-.042,lo+.055),(.025,.012,.078),black,'Steering',.004)
 bolt('Hinge axle nut',(sx,-.051,lo),.01,'Steering')
 st=c['stem'];a=Vector((sx,0,lo+.065));b=Vector((tx,0,H-.055))
 if st in ['square','wide']:
  o=cube('Extruded main steering stem',(a+b)/2,(.047 if st=='square' else .074,.048 if st=='square' else .065,(b-a).length),paint,'Steering',.006);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
  if e['name']=='Ausom Gallop':
   mid=a.lerp(b,.35);o=cube('Gallop yellow upper mast',(mid+b)/2,(.049,.05,(b-mid).length),accent,'Steering',.005);o.rotation_euler=(b-mid).to_track_quat('Z','Y').to_euler()
 else:
  rod('Main steering tube',a,b,.020 if st!='battery' else .035,black if e['name'].startswith('NIU') else paint,'Steering',40)
  if st=='telescopic':
   mid=a.lerp(b,.59);rod('Telescopic inner tube',mid,b,.016,silver,'Steering',24);cube('Stem quick clamp',(mid.x,0,mid.z),(.061,.057,.025),accent,'Steering',.003)
 if st=='battery':
  o=cube('Stem enclosed battery pack',(sx-.065,-.014,lo+.43),(.075,.085,.40),paint,'BatteryMount',.012)
  if e['name'].endswith('ES4'):cube('External ES4 auxiliary battery',(sx-.10,.065,lo+.44),(.085,.065,.40),black,'BatteryMount',.01)
 rod('Handlebar central rise',(tx,0,H-.055),(tx-.016,0,H-.005),.016,paint,'Steering')
 curve('Swept handlebar',[(tx, -bar/2,H),(tx+.01,-bar*.28,H-.014),(tx-.016,0,H-.015),(tx+.01,bar*.28,H-.014),(tx,bar/2,H)],.0115,paint,'Steering')
 for sy in [-1,1]:
  rod('Rubber handle grip',(tx,sy*(bar/2-.105),H),(tx,sy*bar/2,H),.019,grip,'Steering',24)
  for j in range(12):
   y=sy*(bar/2-.099+j*.0076);rod('Grip molded rib',(tx,y-.001,H),(tx,y+.001,H),.0197,black,'Steering',16)
  rod('Brake lever clamp',(tx,sy*(bar/2-.115),H-.005),(tx+.026,sy*(bar/2-.115),H-.012),.012,black,'Steering',16)
  curve('Brake lever',[(tx+.025,sy*(bar/2-.12),H-.01),(tx+.065,sy*(bar/2-.10),H-.023),(tx+.075,sy*(bar/2-.035),H-.027)],.0045,black,'Steering')
  if c['signal']:rod('Handlebar turn indicator',(tx,sy*(bar/2+.002),H),(tx,sy*(bar/2+.015),H),.018,accent,'Steering',20)
 cube('Dashboard enclosure',(tx+.006,0,H+.004),(.075,.095,.026),black,'Steering',.006);cube('Dashboard display glass',(tx+.009,0,H+.018),(.059,.075,.003),screen,'Steering',.003)
 # Dashboard numeral plate faces upward, actual geometry at real display scale.
 for j in [-1,0,1]:cube('Display LED segments',(tx+.014,j*.014,H+.020),(.022,.002,.0006),lens,'Steering',.0002)
 rod('Thumb throttle body',(tx,-bar*.23,H-.01),(tx,-bar*.23,H+.014),.014,black,'Steering',20);cube('Thumb throttle paddle',(tx+.027,-bar*.23,H-.025),(.035,.027,.008),black,'Steering',.004)
 # Visible brake/electric cables follow slack loops into the chassis.
 for sy in [-1,1]:curve('External control cable',[(tx+.04,sy*bar*.27,H-.02),(tx+.10,sy*.09,H-.15),(sx+.06,sy*.035,lo+.20),(sx+.025,sy*.04,lo-.03),(dl*.35,sy*dw*.43,dz-.015)],.0032,black,'Steering')
 lamp=c['lamp'];lx=tx+.044;lz=H-.085
 if lamp.startswith('low') or lamp=='twinsquare':lx=sx+.065;lz=lo-.03
 if lamp=='stem':lx=sx+.04;lz=lo+.18
 if lamp=='midround':lx=sx+.07;lz=lo+.40
 if lamp=='console':lx=tx+.050;lz=H-.046
 if lamp=='twinround':
  for sy in [-1,1]:
   rod('Twin ES10 lamp shell',(sx+.05,sy*.035,lo+.23),(sx+.10,sy*.035,lo+.23),.026,black,'Steering',28)
   rod('Twin ES10 lamp lens',(sx+.101,sy*.035,lo+.23),(sx+.104,sy*.035,lo+.23),.021,lens,'Steering',28)
 elif lamp in ['highround','lowround','midround'] or c['halo']:
  rod('Headlight cylindrical body',(lx-.026,0,lz),(lx+.020,0,lz),.027,black,'Steering',32);rod('Headlight optical lens',(lx+.020,0,lz),(lx+.023,0,lz),.021,lens,'Steering',32)
  if c['halo']:
   for i in range(32):
    a=i*2*pi/32;rod('NIU halo LED ring',(lx+.024,.026*cos(a),lz+.026*sin(a)),(lx+.026,.026*cos(a),lz+.026*sin(a)),.003,lens,'Steering',6)
 elif lamp=='twinsquare':
  for sy in [-1,1]:cube('Twin headlamp',(lx,sy*.042,lz),(.038,.048,.045),black,'Steering',.004);cube('Twin optical lens',(lx+.021,sy*.042,lz),(.003,.036,.033),lens,'Steering',.002)
 else:
  cube('Headlamp body',(lx,0,lz),(.035,.050 if lamp!='x' else .08,.025 if lamp!='x' else .052),black,'Steering',.004)
  if lamp=='x':
   for sy in [-1,1]:rod('ZT3 X lamp signature',(lx+.02,sy*.028,lz-.017),(lx+.02,-sy*.028,lz+.017),.004,lens,'Steering',12)
  else:cube('Headlamp optical pane',(lx+.019,0,lz),(.003,.041,.016),lens,'Steering',.002)
 # Reflectors and manufacturer lettering mounted on stem/deck faces.
 for x in [rear+.025,front-.02]:
  for sy in [-1,1]:cube('Amber side reflector',(x,sy*(wide+.043),R+.035),(.04,.003,.012),accent,b=.003)
 label('Deck manufacturer',e['name'].split()[0].upper(),(-.01,-dw/2-.002,dz-.026),.023,white)
 label('Stem model marking',e['name'].replace('Segway Ninebot ','NINEBOT '),((sx+tx)/2,-.029,(lo+H)/2),.023,white,'Steering',angle=pi/2-.18)
 if c['seat']:
  bx=-.17
  for sy in ([] if e['name']=='Bogist M5 Pro' else [-1,1]):
   curve('Seat pedestal side frame',[(bx-.04,sy*.045,dz+.02),(bx+.02,sy*.045,.49),(bx+.01,sy*.045,.71)],.0075,paint)
   for z in [.33,.41,.49,.57,.65]:rod('Seat pedestal rung',(bx-.035,sy*.045,z),(bx+.033,sy*.045,z),.006,paint)
  rod('Seat post',(bx,0,dz+.025),(bx+.015,0,.81),.018,paint);rod('Seat exposed inner post',(bx+.01,0,.65),(bx+.015,0,.83),.012,silver)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(bx-.025,0,.85));o=bpy.context.object;o.scale=(.145,.10,.04);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,'Padded seat saddle',grip,smooth=True)
  cube('Seat clamp',(bx+.005,0,.62),(.05,.05,.02),accent,b=.003)
 if e['name']=='Bogist M5 Pro':
  bx=rear-.015;bz=.59;bl=.24;bw=.24
  for sy in [-1,1]:
   for zz in [bz,bz+.17]:rod('Rear cargo basket side rail',(bx-bl/2,sy*bw/2,zz),(bx+bl/2,sy*bw/2,zz),.004,black)
   for j in range(8):
    xx=bx-bl/2+j*bl/7;rod('Rear basket wire',(xx,sy*bw/2,bz),(xx,sy*bw/2,bz+.17),.0017,black,n=6)
   rod('Carrier rack support',(rear+.03,sy*.07,R),(bx+.05,sy*.07,bz),.007,paint)
  for xx in [bx-bl/2,bx+bl/2]:
   for zz in [bz,bz+.17]:rod('Rear basket end rail',(xx,-bw/2,zz),(xx,bw/2,zz),.004,black)
   for j in range(8):
    yy=-bw/2+j*bw/7;rod('Rear basket end wire',(xx,yy,bz),(xx,yy,bz+.17),.0017,black,n=6)
  for sy in [-1,1]:cube('M5 teal deck accent',(-.015,sy*(dw/2+.002),dz-.028),(dl*.85,.002,.01),accent,b=.001)
 if e['name']=='KuKirin C1 Pro':
  # Basket mounted forward of headstock; open tube grid with bottom and four raised walls.
  bx=front+.025;bz=.70;bw=.28;bl=.26
  for sy in [-1,1]:
   rod('Cargo basket upper side',(bx-bl/2,sy*bw/2,bz+.15),(bx+bl/2,sy*bw/2,bz+.15),.004,black)
   rod('Basket lower side',(bx-bl/2,sy*bw/2,bz),(bx+bl/2,sy*bw/2,bz),.004,black)
   for j in range(9):
    xx=bx-bl/2+j*bl/8;rod('Basket grid vertical',(xx,sy*bw/2,bz),(xx,sy*bw/2,bz+.15),.0018,black,n=6)
  for xx in [bx-bl/2,bx+bl/2]:
   for zz in [bz,bz+.15]:rod('Basket cross rail',(xx,-bw/2,zz),(xx,bw/2,zz),.004,black)
   for j in range(10):
    yy=-bw/2+j*bw/9;rod('Basket end grid',(xx,yy,bz),(xx,yy,bz+.15),.0018,black,n=6)
  for j in range(7):
   xx=bx-bl/2+j*bl/6;rod('Basket bottom slat',(xx,-bw/2,bz),(xx,bw/2,bz),.002,black,n=6)
  for sy in [-1,1]:
   rod('Basket support',(sx,sy*.06,.47),(bx,sy*.07,bz),.007,paint)
   rod('Rear passenger rack leg',(rear+.03,sy*.07,R),(rear+.02,sy*.07,.64),.008,paint)
   rod('Passenger backrest support',(rear-.06,sy*.08,.64),(rear-.06,sy*.08,.89),.008,paint)
   rod('Mirror stalk',(tx,sy*bar*.32,H),(tx+.005,sy*bar*.42,H+.18),.004,black,'Steering')
   bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(tx+.005,sy*bar*.42,H+.2));o=bpy.context.object;o.scale=(.025,.05,.07);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,'Oval mirror housing',black,'Steering',True)
  cube('Passenger rear seat cushion',(rear+.035,0,.66),(.29,.20,.045),grip,b=.015)
  cube('Passenger padded backrest',(rear-.065,0,.86),(.045,.18,.17),grip,b=.015)
 # Charge socket, side stand, real rear optical lens.
 rod('Charging port',(dl*.26,-dw/2-.003,dz-.030),(dl*.26,-dw/2-.009,dz-.030),.008,black)
 curve('Side stand',[(-.13,-dw*.45,dz-.06),(-.18,-dw*.70,.04),(-.19,-dw*.73,.008)],.0055,steel)
 cube('Stand foot',(-.19,-dw*.73,.007),(.025,.020,.012),black,b=.002)


def build(e):
 global groups,parts,black,edge,paint,rubber,grip,silver,steel,orange,gold,red,rotor,lens,screen,white,purple,R,accent,entry
 entry=e;c=config(e);key=e['key'];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 revised=key in KUKIRIN_G
 black=mat('Black molded polymer',(.007,.009,.011) if revised else (.018,.022,.026),.08 if revised else .15,.45)
 edge=mat('Anodized dark metal',(.018,.023,.029) if revised else (.047,.057,.066),.60 if revised else .70,.38)
 steel=mat('Steel',(.035,.042,.048) if revised else (.12,.15,.17),.75 if revised else .80,.37 if revised else .32)
 silver=mat('Silver machining',(.19,.22,.25) if revised else (.23,.27,.31),.75,.34)
 rubber=mat('Tire rubber',(.008,.010,.012) if revised else (.022,.026,.03),0,.80)
 grip=mat('Textured grip rubber',(.012,.014,.016) if revised else (.035,.04,.045),0,.75)
 orange=mat('Safety orange',(.98,.27,.01),.2,.4);gold=mat('Gold',(.92,.50,.02),.55,.3)
 accent=mat('Model accents',tuple(v**2.2 for v in c['accent']),.08 if revised else .25,.45)
 red=mat('Red optical lens',(.60,.008,.005),.3,.27);rotor=silver;lens=mat('Headlamp diffuser',(.78,.88,.96),.2,.2)
 screen=mat('Display glass',(.009,.03,.045),.25,.16);white=mat('Printed markings',(.64,.69,.71),.1,.5)
 purple=mat('Deck LED',(.12,.02,.70),.2,.3)
 paint=mat('Model powder coat',c['body'] if revised else tuple(v*.24 for v in c['body']),.18 if revised else .30,.39 if revised else .48)
 for m in [rubber,grip]:
  nt=m.node_tree;ns=nt.nodes.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=240;bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.15;bp.inputs['Distance'].default_value=.0004;nt.links.new(ns.outputs['Fac'],bp.inputs['Height']);nt.links.new(bp.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
 root_reference=c['reference'] if revised else e['source']
 root=bpy.data.objects.new(e['name'],None);bpy.context.collection.objects.link(root);root['canonicalKey']=key;root['frontAxis']='+X';root['source']=root_reference;root['reference']=e['image'];root['accuracy']='Photographic proportions, inferred hidden/internal surfaces. Not measured CAD.'
 groups={};parts=[]
 for n in ['Chassis','Steering','FrontWheel','RearWheel','BatteryMount','ControllerMount','MotorMount']:
  o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=root;groups[n]=o
 R=c['r'];front=c['wb']/2;rear=-front;dz=c['dz'];dl=c['dl'];dw=c['dw'];H=c['h'];sx=front-.09;tx=sx-.15;bar=c['bar'];lo=dz+.18;wide=c['wide'];offroad=c['family'] not in ['rigid commuter','Xiaomi curved-neck commuter','Ninebot rigid commuter','NIU curved-neck halo commuter','iScooter i9 rigid commuter','Kugoo M2 Pro commuter'] and dz>.22
 wheel(front,'FrontWheel',c);wheel(rear,'RearWheel',c)
 if revised:
  kukirin_g_body(e,c,front,rear)
 else:
  generic_body(e,c,front,rear,R,dz,dl,dw,H,sx,tx,bar,lo,wide,offroad)
 # Convert and compact by assembly/material for a small editable/exportable asset.
 for o in list(parts):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  if o.type!='MESH':bpy.ops.object.convert(target='MESH')
  for md in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=md.name)
   except RuntimeError:pass
 for p in groups.values():
  buckets={}
  for o in list(p.children):
   if o.type=='MESH':buckets.setdefault((o.data.materials[0].name,o.get('vfCockpit','')),[]).append(o)
  for (mn,cockpit),objs in buckets.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in objs:o.select_set(True)
   bpy.context.view_layer.objects.active=objs[0]
   if len(objs)>1:bpy.ops.object.join()
   objs[0].name=' | '.join(filter(None,(p.name,mn,cockpit)));bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 model=[o for p in groups.values() for o in p.children if o.type=='MESH'];tri=0
 for o in model:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 bpy.context.view_layer.update();minz=min((o.matrix_world@Vector(v)).z for o in model for v in o.bound_box)
 if minz<-.001:
  for o in groups['Steering'].children:
   if o.name.startswith('VF_Cockpit_'):o.location.z-=minz
  for o in model:o.location.z-=minz
  for o in model:
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for p in groups.values():
  p.select_set(True)
  for o in p.children:o.select_set(True)
 export=OUT/(key+'.glb');bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 im=bpy.data.images.load(str(ROOT/'apps/web/public'/e['image'].lstrip('/')));im.pack();ref=bpy.data.objects.new('REFERENCE exact product photo - hidden from export',None);bpy.context.collection.objects.link(ref);ref.empty_display_type='IMAGE';ref.data=im;ref.hide_render=True;ref.hide_viewport=True
 sc=bpy.context.scene;sc.world=bpy.data.worlds.new('STUDIO world');sc.world.color=(.35,.35,.35);sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 gm=mat('STUDIO floor',(.79,.80,.81),0,.8);bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.name='STUDIO floor';bpy.context.object.data.materials.append(gm)
 for loc,power,size in [((1,-3,4),460,3),((-2,-1,2),240,2.5),((1.5,2,3),450,2.5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO light';o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.65))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(2.7,-4.8,2.1));cam=bpy.context.object;cam.name='STUDIO camera';cam.rotation_euler=(Vector((0,0,H*.48))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(H+.28,c['wb']+R*2+.24);sc.camera=cam;sc.render.filepath=str(O/(key+'.png'));bpy.ops.render.render(write_still=True)
 bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(BL/(key+'.blend')),compress=True)
 note=dict(key=key,name=e['name'],family=c['family'],parameters=c,triangles=tri,meshes=len(model),bytes=export.stat().st_size,source=e['source'],reference=e['image'],nativeSource='assets/blender/expansion/commuter/'+key+'.blend',url='/models/expansion/commuter/'+key+'.glb')
 if revised:
  note['manufacturerReference']=c['reference']
  note['geometryReview']='Model-specific deck, suspension, steering, grip molds and forged low-angle side stand.'
 assert tri<120000 and len(model)<65 and export.stat().st_size<5000000,note
 json.dump(note,open(O/(key+'.json'),'w'),indent=2);print('COMPLETE '+key,flush=True)
if __name__=='__main__':
 sel=json.load(open(O/'selected.json'));args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for e in sel:
  if args and e['key'] not in args:continue
  if (O/(e['key']+'.json')).exists() and not args and not os.getenv('COMMUTER_REBUILD'):continue
  build(e)
 print('COMMUTER_BATCH_COMPLETE',flush=True)
