"""Named wheel and cockpit geometry used by the configurator's part swaps."""

from math import atan2, cos, pi, sin


def wheel(p, c, m, front):
    group = "FrontWheel" if front else "RearWheel"
    x = (1 if front else -1)*c["wheelbase"]/2
    radius, half = c["radius"], c["half_tire"]
    layout = c["layout"]
    # A closed carcass gives continuous outer tread and rounded shoulders.
    cross = [(-1, .79),(-.99,.83),(-.96,.89),(-.87,.93),(-.71,.967),(-.46,.989),
             (-.22,.999),(0,1),(.22,.999),(.46,.989),(.71,.967),(.87,.93),
             (.96,.89),(.99,.83),(1,.79),(.88,.75),(-.88,.75)]
    n = 192
    vertices = []
    blocks = c.get("tread") == "block"
    for j, (width_fraction, radial) in enumerate(cross):
        for i in range(n):
            theta = i*2*pi/n
            lateral = abs(width_fraction)
            groove = (i/n*(39 if blocks else 34)+lateral*(.58 if blocks else 1.18))%1
            side = max(0, (1 - abs(groove-.5)/.16)*(1 - lateral)**.39) if radial>.87 else 0
            if blocks and .3 < lateral < .88:
                side = max(side,.70*max(0,1-abs(groove-.22)/.085))
            rr = radius*radial-side*(.0044 if blocks else .0024)
            vertices.append((x+rr*cos(theta),half*width_fraction,radius+rr*sin(theta)))
    faces = [
        (j*n+i,j*n+(i+1)%n,((j+1)%len(cross))*n+(i+1)%n,((j+1)%len(cross))*n+i)
        for j in range(len(cross)) for i in range(n)
    ]
    p.mesh(group+" sculpted "+("off-road" if blocks else "road")+" tire rubber",
           vertices,faces,m["tire"],group,True)
    rim = radius*.78
    driven = c["motor"] == "both" or c["motor"] == ("front" if front else "rear")
    for side in (-1,1):
        y = side*half*.965
        p.ring("Wheel bead alloy rim",x,y,radius,rim+.001,rim-.009,.012,m["rim"],group,n=72)
        p.ring("Outer shoulder lettering band",x,side*half*.98,radius,
               rim+.011,rim+.007,.002,m["tire"],group,n=72)
        if c["key"]=="segway-ninebot-gt2" and not front:
            p.ring("GT2 red machined rim stripe",x,side*(half*.965+.005),radius,
                   rim-.003,rim-.006,.002,m["accent"],group,n=72)
    if driven:
        p.rod("Hub motor core",(x,-half*.84,radius),(x,half*.84,radius),
              rim*.92,m["motor"],"MotorMount",n=72)
        for side in (-1,1):
            y = side*half*.87
            p.rod("Motor hub cast endplate",(x,y,radius),(x,y+side*.008,radius),
                  rim*.90,m["motor"],"MotorMount",n=64)
            p.ring("Circular seal seam",x,y+side*.009,radius,rim*.81,rim*.78,.003,
                   m["edge"],"MotorMount",n=64)
            p.rod("Motor axle dust seal",(x,y,radius),(x,y+side*.014,radius),
                  rim*.23,m["edge"],"MotorMount",n=28)
            for i in range(10):
                angle=i*2*pi/10
                p.bolt("Motor cover bolts",(x+rim*.70*cos(angle),y+side*.009,
                                           radius+rim*.70*sin(angle)),.0027,"MotorMount")
    elif layout=="gt":
        p.rod("GT front cast wheel face",(x,-half*.93,radius),(x,half*.93,radius),
              rim*.91,m["rim"],group,n=72)
        for side in (-1,1):
            p.ring("GT cast wheel face groove",x,side*half*.966,radius,rim*.85,rim*.80,.003,m["edge"],group)
    else:
        p.rod("Passenger axle hub",(x,-half*.89,radius),(x,half*.89,radius),rim*.35,m["rim"],group,n=48)
        spoke_count = 6 if layout == "p" else 10 if layout in ("gt3","zt") else 8
        for side in (-1,1):
            for i in range(spoke_count):
                theta=i*2*pi/spoke_count
                p.rod("Offset cast spoke",(x+rim*.32*cos(theta),side*half*.78,radius+rim*.32*sin(theta)),
                      (x+rim*.95*cos(theta+.25),side*half*.87,radius+rim*.95*sin(theta+.25)),
                      .008,m["rim"],group,n=10,r2=.005)
    if ("front" if front else "rear") in c["rotors"]:
        rotor(p,c,m,group,x,rim,half,radius,(-1 if front else 1))
    for side in (-1,1):
        p.rod("Machined axle spacer",(x,side*half*.89,radius),(x,side*(half+.017),radius),
              .013,m["edge"],group,n=28)


def rotor(p,c,m,group,x,rim,half,z,side):
    dy = side*(half + .008)
    disc = rim*.82
    p.ring("Brake rotor machined outer race",x,dy,z,disc,disc*.80,.0027,m["rotor"],group,n=72)
    p.ring("Brake rotor inner carrier",x,dy,z,disc*.52,disc*.41,.0028,m["rotor"],group,n=48)
    for i in range(12):
        angle=i*2*pi/12
        p.rod("Rotor carrier web",
              (x+disc*.47*cos(angle),dy,z+disc*.47*sin(angle)),
              (x+disc*.83*cos(angle+.14),dy,z+disc*.83*sin(angle+.14)),
              .0027,m["rotor"],group,n=8)
    for i in range(6):
        theta=i*2*pi/6
        p.bolt("Brake bolt star",(x+disc*.48*cos(theta),dy+side*.002,z+disc*.48*sin(theta)),.0025,group)
    color = m["accent"] if c["layout"] in ("gt3","zt") or c["key"].endswith("gt2") else m["matte"]
    p.cube("Hydraulic brake caliper", (x+.034,dy+side*.007,z+.053),(.037,.024,.042),color,
           b=.007)
    p.rod("Caliper banjo fitting",(x+.048,dy+side*.017,z+.064),(x+.034,dy+side*.017,z+.082),
          .005,m["silver"])


def cockpit(p,c,m):
    group = "Steering"
    layout, height, width = c["layout"],c["height"],c["bar"]
    x, z, rake = c["steering_x"], c["neck"], c["rake"]
    t = x-rake
    dia = c["stem_width"]/2
    if layout.startswith("fighter") or layout in ("blade-mini", "blade-gt","supreme"):
        # Rail-profile stem with wider lower clamp and embedded translucent accent.
        beam=p.cube("Extruded squared mast with round corners",
                    ((x+t)*.5,0,(height+z)*.5),(.054,dia*1.64,((height-z)**2+rake**2)**.5),
                    m["shell"],group,.008)
        beam.rotation_euler.y = atan2(-rake,height-z)
        p.curve("Inset vertical side light",[(x-.046,0,z+.11),(t+.008,0,height-.13)],
                .0023,m["diffuser"],group)
    else:
        p.rod("Ellipsoidal taper steering mast",(x,0,z+.01),(t,0,height-.025),
              dia,m["shell"],group,n=40,r2=dia*.70)
        for side in (-1,1):
            p.curve("Elliptical extrusion edge",[ (x-.005,side*dia*.74,z+.022),
                    ((x+t)*.5,side*dia*.75,(z+height)*.5),(t,side*dia*.54,height-.041)],
                    .0037,m["shell"],group)
    for cz, factor in [(z+.078,.85),(height-.042,.62)]:
        cx = x-rake*(cz-z)/(height-z)
        p.rod("Tapered split mast collar",(cx+.005,0,cz-.019),(cx-.003,0,cz+.024),
              dia*1.16*factor,m["edge"],group,n=28)
    if layout=="blade-gt":
        p.rod("Orange anodized mast clamp",(x-.022,0,z+.102),(x-.030,0,z+.139),
              dia*1.11,m["accent"],group,n=36)
    letter = "SEGWAY" if c["key"].startswith("segway") else ("BLADE" if layout.startswith("blade") else "TEVERUN")
    p.label("Stem branding",letter,((x+t)*.5,-dia-.002,(height+z)*.5),.019,
            m["accent"] if layout in ("gt3","zt","blade-mini") else m["mark"],group,
            angle=atan2(height-z,t-x))
    half=width/2
    sweep=.041 if layout in ("gt","gt3","zt","supreme") else .023
    raised=.045 if layout in ("zt","blade-gt","supreme") else .024
    zbar=height-.030
    p.curve("Swept cockpit handlebar",[(t-sweep,-half,zbar+raised),
        (t-sweep,-half*.50,zbar+raised*.79),(t+.004,0,zbar),
        (t-sweep,half*.50,zbar+raised*.79),(t-sweep,half,zbar+raised)],.0112,m["edge"],group)
    p.cube("Central handlebar bridge",(t+.001,0,zbar+.006),(.068,.096,.042),m["shell"],group,.009)
    for side in (-1,1):
        xx=t-sweep
        zz=zbar+raised
        inside=half-.126
        outside=half+.001
        p.rod("Factory molded grip sleeve",(xx,side*inside,zz),(xx,side*outside,zz),
              .0155,m["grip"],group,n=36)
        for index in range(16):
            y=side*(inside+.008+index*.0069)
            p.ring("Grip knurl ridges",xx,y,zz,.0165,.015,.0017,m["grip"],group,n=24)
        for y in (inside-.002,outside-.001):
            p.rod("Molded grip collar",(xx,side*(y-.003),zz),(xx,side*(y+.004),zz),
                  .017,m["accent"] if layout=="blade-gt" else m["edge"],group,n=32)
        p.cube("Low-profile bar-end turn signal",(xx,side*(outside+.006),zz),(.022,.008,.012),
               m["amber"],group,.002)
        yy=side*(inside-.027)
        p.cube("Hydraulic lever hinge and master reservoir",
               (xx+.023,yy,zz+.011),(.046,.027,.027),m["matte"],group,.004)
        p.curve("Curved reach-adjusted brake lever",[(xx+.027,yy,zz+.002),
                (xx+.061,side*(inside+.040),zz-.006),
                (xx+.045,side*(outside-.016),zz-.016)],.0044,m["edge"],group)
        p.rod("Lever hinge button",(xx+.025,yy,zz+.019),(xx+.025,yy,zz+.022),
              .005,m["silver"],group,n=18)
        p.curve("External brake harness from cockpit",[(xx+.023,yy,zz+.005),
                (t+.046,side*.055,height-.154),((x+t)*.5+.038,side*.029,(height+z)*.5),
                (x+.068,side*.040,z-.035)],.0022,m["matte"],group)
        p.cube("Switch cluster",(xx,side*(inside-.047),zz+.006),(.035,.029,.029),
               m["matte"],group,.006)
        for offset in (-.007,.003,.012):
            p.cube("Cockpit rubber rocker",(xx-.009,side*(inside-.047)+offset,zz+.021),
                   (.015,.006,.003),m["pad"],group,.002)
    panel_width = .129 if layout=="gt" else .124 if layout in ("gt3","supreme") else .097 if layout=="p" else .088 if layout in ("fighter-eleven","fighter-ten","zt") else .064
    screen_x = t-.009 if layout.startswith("gt") or layout=="p" else t+.014
    screen_z = height+.013
    dash=p.cube("Dashboard housing with rounded leading edge",(screen_x,0,screen_z),
               (.094,panel_width,.025),m["matte"],group,.007)
    dash.rotation_euler.y=.19
    glass=p.cube("Recessed anti-glare dashboard glass",(screen_x-.001,0,screen_z+.013),
                (.074,panel_width*.86,.003),m["screen"],group,.004)
    glass.rotation_euler.y=.19
    for y in (-.030,-.018,.022,.034):
        p.cube("Dashboard backlit icon",(screen_x+.002,y,screen_z+.016),(.013,.006,.001),
               m["diffuser"],group,.001)
    p.cube("Cockpit thumb throttle",(t-sweep,-half+.174,zbar+.003),(.033,.019,.037),
           m["matte"],group,.005)
    lamps(p,c,m,t,zbar)


def lamps(p,c,m,t,zbar):
    layout = c["layout"]
    x,z = c["steering_x"],c["neck"]
    if layout=="zt":
        # Four visible diagonal arms form the factory X light behind its bezel.
        cx=x+.079
        cy=.045
        cz=z-.082
        p.cube("ZT3 X light housing",(cx,0,cz),(.045,.125,.112),m["matte"],"Steering",.017)
        for side in (-1,1):
            for rise in (-1,1):
                p.curve("ZT X optical arm",[(cx+.027,side*.012,cz+rise*.007),
                        (cx+.028,side*cy*.68,cz+rise*.019),
                        (cx+.022,side*cy,cz+rise*.036)],.007,m["white_lens"],"Steering")
        p.cube("Elliptical main low projector",(cx+.018,0,cz-.082),(.055,.072,.039),
               m["matte"],"Steering",.009)
        p.cube("Low white lens",(cx+.048,0,cz-.083),(.008,.055,.017),
               m["white_lens"],"Steering",.004)
        p.rod("Handlebar projector body",(t+.031,0,zbar-.075),(t+.054,0,zbar-.075),
              .022,m["matte"],"Steering",n=36)
        p.rod("Handlebar projector clear lens",(t+.053,0,zbar-.075),(t+.059,0,zbar-.075),
              .016,m["white_lens"],"Steering",n=36)
    elif layout in ("gt","gt3","p"):
        xx=t+.046 if layout=="p" else x+.079
        zz=zbar-.058 if layout=="p" else z-(.102 if layout=="gt3" else .070)
        ww=.142 if layout=="gt" else .105 if layout=="gt3" else .081
        p.cube("Aero low-beam enclosure",(xx,0,zz),(.049,ww,.040),m["matte"],"Steering",.009)
        p.cube("Primary optical lens",(xx+.028,0,zz),(.009,ww*.84,.023),
               m["white_lens"],"Steering",.004)
        for side in (-1,1):
            p.cube("Side marker lens",(xx-.017,side*ww*.49,zz-.007),(.036,.006,.007),
                   m["amber"],"Steering",.002)
    else:
        height = zbar-.107 if layout in ("fighter-ten","fighter-eleven","fighter-mini","blade-mini","supreme") else z-.086
        loc_x = t+.030 if height > .8 else x+.074
        spacing = .016 if layout in ("fighter-ten","fighter-mini") else .0
        if spacing:
            p.cube("Shared twin projector molded shell",(loc_x+.015,0,height),
                   (.045,.076,.049),m["matte"],"Steering",.010)
        for y in (-spacing,spacing) if spacing else (0,):
            rr=.026 if spacing==0 else .014
            p.rod("Round waterproof projector housing",(loc_x-.005,y,height),(loc_x+.048,y,height),
                  rr,m["matte"],"Steering",n=40)
            p.rod("Round projector lens",(loc_x+.048,y,height),(loc_x+.053,y,height),
                  rr*.82,m["white_lens"],"Steering",n=40)
