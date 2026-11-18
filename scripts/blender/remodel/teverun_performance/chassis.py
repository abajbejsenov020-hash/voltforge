"""Photo-shaped deck, headstock, fenders and suspension assemblies."""

from math import cos, pi, radians, sin
from mathutils import Vector


def extrusion(p, name, polygon, width, material, parent="Chassis", y=0, radius=.003):
    obj = p.profile(name, polygon, width, material, parent=parent, y=y)
    return p.bevel(obj, radius)


def cast_link(p, name, start, end, y, width, height, material, window=.0, bend=.0):
    """Cast side path with a machined perimeter and, where visible, an opening."""
    a, b = Vector(start), Vector(end)
    travel = b - a
    up = travel.normalized().orthogonal()
    if up.y < 0:
        up.negate()
    points = [
        a + up * height * .39,
        a + travel * .23 + up * (height * .55 + bend),
        a + travel * .65 + up * (height * .3 + bend),
        b + up * height * .26,
        b - up * height * .29,
        a + travel * .62 - up * (height * .37 - bend),
        a + travel * .18 - up * height * .48,
        a - up * height * .31,
    ]
    if not window:
        return extrusion(p, name, points, width, material, y=y, radius=.004)

    center = a.lerp(b, .52) + up * bend
    direction = travel.normalized()
    opening = [
        center + direction * (point - center).dot(direction) * window
        + up * (point - center).dot(up) * .49
        for point in points
    ]
    n = len(points)
    vertices = [
        (x, yy, z)
        for yy in (y - width / 2, y + width / 2)
        for ring in (points, opening)
        for x, z in ring
    ]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend(
            [
                (i, j, n + j, n + i), (2 * n + i, 3 * n + i, 3 * n + j, 2 * n + j),
                (i, 2 * n + i, 2 * n + j, j), (n + i, n + j, 3 * n + j, 3 * n + i),
            ],
        )
    return p.mesh(name, vertices, faces, material, b=.0025)


def deck_shell(p, c, m):
    length, width, top, depth = (c[k] for k in ("deck_length", "deck_width", "deck_height", "deck_depth"))
    layout = c["layout"]
    x = length / 2
    # Longitudinal sections preserve the visible narrowing at the neck and rear casting.
    sections = {
        "p": [(-1.04, .75, .008, .73), (-.89, .97, 0, .98), (-.60, 1, 0, 1), (.65, 1, 0, 1),
              (.88, .83, .022, .91), (1.06, .57, .066, .73)],
        "gt": [(-1.03, .64, .018, .58), (-.85, .94, .023, .94), (-.58, 1, 0, 1), (.62, 1, 0, 1),
               (.90, .85, .012, .89), (1.04, .64, .055, .64)],
        "gt3": [(-1.03, .85, .028, .66), (-.74, 1, 0, .98), (-.52, .99, 0, 1), (.74, 1, 0, 1),
                (.94, .86, .013, .71), (1.05, .58, .068, .58)],
        "zt": [(-1.04, .74, .017, .69), (-.79, .97, 0, 1), (.62, 1, 0, 1),
               (.87, .96, .012, .94), (1.04, .63, .043, .67)],
        "fighter-mini": [(-1.02, .78, .006, .85), (-.87, .99, 0, 1), (.82, 1, 0, 1), (1.03, .72, .015, .92)],
        "fighter-ten": [(-1.00, .89, .004, .74), (-.81, 1, 0, 1), (.66, 1, 0, 1),
                        (.89, .91, .005, 1), (1.035, .69, .025, .73)],
        "fighter-eleven": [(-1.04, .85, .012, .87), (-.88, 1, 0, 1), (.83, 1, 0, 1), (1.06, .67, .023, .78)],
        "supreme": [(-1.05, .78, .016, .82), (-.82, 1, 0, .96), (-.57, 1, 0, 1),
                    (.87, 1, 0, 1), (1.04, .72, .020, .87)],
        "blade-mini": [(-1.01, .77, .014, .64), (-.83, 1, 0, 1), (.76, .98, 0, 1), (1.03, .65, .032, .66)],
        "blade-gt": [(-1.06, .77, .007, .78), (-.87, .98, 0, 1), (.83, 1, 0, 1), (1.055, .70, .023, .83)],
    }[layout]
    vertices = []
    for px, spread, dz, thick in sections:
        half = width * spread / 2
        upper = top + dz
        lower = upper - depth * thick
        chamfer = min(.018, width * .07) if layout != "blade-mini" else .009
        vertices.extend([
            (px*x, -half + chamfer, upper),
            (px*x, half - chamfer, upper),
            (px*x, half, upper - .014),
            (px*x, half, lower + .012),
            (px*x, half - chamfer, lower),
            (px*x, -half + chamfer, lower),
            (px*x, -half, lower + .012),
            (px*x, -half, upper - .014),
        ])
    stops = len(sections)
    faces = [tuple(range(7, -1, -1)), tuple(range((stops - 1)*8, stops*8))]
    faces.extend(
        (i*8 + j, i*8 + (j+1)%8, (i+1)*8 + (j+1)%8, (i+1)*8 + j)
        for i in range(stops-1) for j in range(8)
    )
    p.mesh("Chamfered battery tray with rolled edges", vertices, faces, m["shell"], b=.003)
    bottom = top - depth
    p.cube("Recessed lower service plate", (0, 0, bottom - .001), (length*.87, width*.82, .015),
           m["edge"], b=.005)
    p.cube("Protected cell-module envelope", (-length*.10, 0, bottom + depth*.48),
           (length*.65, width*.83, depth*.79), m["matte"], "BatteryMount", .007)
    p.cube("Controller cast housing", (length*.34, 0, bottom + depth*.44),
           (length*.19, width*.82, depth*.67), m["steel"], "ControllerMount", .004)
    for y in range(-5, 6):
        p.cube("Controller case raised cooling fin", (length*.34, y*width*.065, bottom + depth*.82),
               (length*.17, .004, .008), m["edge"], "ControllerMount", .001)

    rubber = m["pad"]
    station_pad = [
        (-x*.87, -width*.38), (-x*.69, -width*.445), (x*.74, -width*.438),
        (x*.88, -width*.31), (x*.88, width*.31), (x*.74, width*.438),
        (-x*.69, width*.445), (-x*.87, width*.38),
    ]
    n = len(station_pad)
    p.mesh("Inset contoured rider grip pad",
           [(xx, yy, top+zz) for zz in (.001, .008) for xx, yy in station_pad],
           [tuple(reversed(range(n))), tuple(range(n, 2*n))] +
           [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)],
           rubber, b=.002)
    for stripe in range(19):
        xx = length * (-.385 + stripe*.043)
        slope = .032 if layout in ("zt", "gt3", "fighter-ten", "supreme") else .012
        for sign in (-1, 1):
            p.rod("Molded chevron deck tread",
                  (xx, sign*width*.052, top+.0085),
                  (xx-slope, sign*width*.35, top+.0085), .0018,
                  m["grip_high"], n=6)
    serial = c["key"].removeprefix("segway-ninebot-").removeprefix("teverun-").upper().replace("-", " ")
    for s in (-1, 1):
        y = s * (width/2+.002)
        rail_at = top - depth*.47
        if layout == "p":
            p.curve("Swept P-series inlaid lower rail", [
                (-x*.99,s*(width*.39),top+.034), (-x*.82,y,rail_at),
                (0,y,rail_at-.003), (x*.83,s*(width*.46),rail_at+.005),
                (x*1.12,s*.073,top+.115)], .0055,
                m["white"] if c["suspension"] == "rigid" else m["edge"])
        elif layout in ("gt", "gt3", "zt"):
            p.curve("Continuous side frame tube and relief edge", [
                (-x*1.14,s*width*.365,top+.078),(-x*.85,y,top-.016),
                (x*.65,y,top-.012),(x*.97,s*width*.40,top+.016),
                (x*1.24,s*width*.242,c["neck"]-.025)],
                .012 if layout in ("gt3", "zt") else .006,
                m["accent"] if layout == "zt" else m["edge"])
        else:
            p.cube("Inset flank light rail gasket", (0, y, rail_at),
                   (length*.79, .006, .015), m["edge"], b=.003)
            p.cube("Narrow flank light diffuser", (0, y+s*.003, rail_at+.002),
                   (length*.72, .004, .005), m["diffuser"], b=.001)
            for xx in (-x*.78, x*.76):
                extrusion(p, "Flank panel corner cap", [
                    (xx-.030, rail_at-.020), (xx+.022, rail_at-.016),
                    (xx+.034, rail_at+.020), (xx-.021, rail_at+.019),
                ], .007, m["accent"], y=s*width*.472)
        p.label("Side emblem", serial, (-.023,y+s*.0015,top-depth*.29),
                .014 if layout != "supreme" else .018, m["mark"])
        for xx in (-x*.72, x*.67):
            p.bolt("Flank panel screw", (xx,y,top-depth*.73), .0028)
    port_y = -width/2 - .003
    p.cube("Charging port weather cap", (x*.55,port_y,top-depth*.72), (.040,.006,.022),m["matte"],b=.004)
    p.cube("Charging port hinge tab", (x*.55+.022,port_y,top-depth*.68), (.007,.012,.012),m["edge"],b=.002)
    # Keep the parked illustration upright with the side stand tucked along the deck.
    p.rod("Folded side stand", (-x*.59, -width*.48, bottom+.017),
          (-x*.18, -width*.52, bottom+.021), .007, m["edge"])
    p.cube("Stamped stand foot", (-x*.17, -width*.52, bottom+.021),
           (.024,.023,.008),m["matte"],b=.003)


def headstock(p, c, m):
    layout = c["layout"]
    h, top = c["neck"], c["deck_height"]
    x = c["deck_length"] / 2
    front = c["wheelbase"] / 2
    sx = c["steering_x"]
    s = "Steering"
    if layout == "gt":
        extrusion(p, "Tall angular alloy headstock with inset fairings", [
            (x*.77,top-.053),(front-.032,top-.053),(front-.017,h-.109),
            (sx+.049,h+.037),(sx-.047,h+.024),(x*.99,top+.023),
        ], .128, m["shell"], radius=.013)
        for y in (-.067, .067):
            extrusion(p, "Contrasting swept headstock cladding", [
                (x*.92,top-.019),(front-.035,top-.018),(front-.008,h-.135),
                (sx+.025,h-.011),(sx-.025,h-.009),(x*1.09,top+.007),
            ], .010, m["silver_dark"], y=y, radius=.006)
            p.curve("Angled GT fairing trim", [(x*1.01,y,top+.024),(sx+.016,y,h-.041),
                    (sx+.058,y,h-.12)], .004, m["accent"])
    elif layout in ("gt3", "zt"):
        # The open neck gives the newer GT and ZT a recognizable view through the frame.
        for y in (-.050, .050):
            cast_link(p,"Angular neck rails and open casting",
                      (x*.82,top-.009),(sx+.012,h-.036),y,.024,
                      .065 if layout=="gt3" else .075,m["shell"],
                      window=.64 if layout=="gt3" else 0,bend=.013)
            p.rod("Upper frame tube", (x*1.00,y,top+.011),(sx-.024,y,h-.030),
                  .009,m["edge"])
        p.rod("Short headstock bridge", (sx+.020,-.068,h-.023),(sx+.020,.068,h-.023),.023,m["edge"])
        if layout == "zt":
            extrusion(p, "ZT diagonally cut upper side shield", [
                (x*.70,top+.001),(sx+.055,top+.002),(sx+.054,h-.176),
                (sx+.013,h-.103),(sx-.014,h-.148),
            ], .145, m["shell"], radius=.006)
    elif layout == "p":
        extrusion(p, "Swooping P cast transition", [
            (x*.70,top-.061),(x*1.16,top-.046),(sx+.045,h-.087),
            (sx+.032,h+.001),(sx-.028,h+.018),(x*1.00,top+.015),(x*.81,top+.002),
        ], .126, m["shell"], radius=.011)
        for y in (-.061,.061):
            p.curve("Inset cast transition witness",[(x*.76,y,top-.021), (x*1.02,y,top+.003),
                    (sx-.017,y,h-.066)],.0027,m["silver_dark"])
    elif layout == "fighter-mini":
        for y in (-.040,.040):
            cast_link(p,"Fighter Mini recessed C-shaped fork bridge",
                      (x*.87,top-.014),(sx+.024,h-.025),y,.022,.079,
                      m["shell"],window=.73,bend=.009)
            p.rod("Hollow bridge diagonal cross rib",
                  (x*.89,y,top+.002),(sx+.019,y,h-.091),.009,m["edge"])
            p.bolt("Mini upper bridge screw",(sx+.020,y+.010,h-.056),.006)
        p.rod("Open lower bridge steering cross-pin",
              (sx+.024,-.052,h-.024),(sx+.024,.052,h-.024),.021,m["edge"])
    else:
        forge = .070 if layout == "blade-mini" else .100
        extrusion(p, "Swept formed lower neck", [
            (x*.76,top-.055),(front-.100,top-.041),(sx+.065,h-.100),
            (sx+.016,h+.018),(sx-.035,h+.010),(x*.98,top+.014),
        ], forge, m["shell"], radius=.008)
        for sign in (-1, 1):
            y = sign*(forge/2+.010)
            cast_link(p,"Open clamp gusset",(x*.90,top),(sx+.025,h-.034),y,.014,.054,
                      m["edge"],window=.68 if layout == "blade-gt" else 0)
            p.bolt("Cast gusset fastening point",(sx+.014,y+sign*.007,h-.058),.006)

    b = c["stem_width"]/2
    p.rod("Steering bearing surround",(sx+.009,0,h-.070),(sx-.009,0,h+.036),
          b*1.16,m["matte"],s,n=28)
    for z in (h-.064,h+.031):
        p.rod("Bearing collar",(sx,0,z-.005),(sx-.002,0,z+.005),b*1.23,m["edge"],s,n=32)
    p.cube("Folding safety lever",(sx-.046,0,h+.057),(.018,.041,.117),m["shell"],s,.005)
    p.cube("Folding latch release insert",(sx-.053,0,h+.088),(.013,.024,.033),
           m["accent"] if layout in ("blade-gt","blade-mini","gt2") else m["edge"],s,.003)
    p.rod("Folding transverse hinge pin",(sx,-b*1.5,h+.008),(sx,b*1.5,h+.008),
          .012,m["edge"],s,n=28)
    for sign in (-1, 1):
        p.bolt("Lock pivot socket",(sx,sign*b*1.54,h+.008),.008,s)


def heel_brace(p, c, m):
    layout = c["layout"]
    x, top, w = -c["deck_length"]/2, c["deck_height"], c["deck_width"]
    if layout == "p":
        tap = .105 if c["suspension"] == "rigid" else .119
        for sign in (-1,1):
            cast_link(p,"P-series color heel spoiler",(x+.053,top-.010),(x-.105,top+tap),
                      sign*w*.27,.047,.062,m["accent"],window=.67 if c["suspension"]=="p100" else 0)
        p.cube("Tail grip crown", (x-.100,0,top+tap), (.084,w*.70,.020),m["pad"],b=.008)
    elif layout in ("gt","gt3","zt"):
        pts = [
            (x+.092,top+.006),(x-.041,top+.050),
            (x-.180,top+.104),(x-.173,top+.125),(x-.107,top+.127),
            (x+.045,top+.050),(x+.119,top+.010),
        ]
        extrusion(p,"Extended tail heel contour",pts,w*.67,m["shell"],radius=.005)
        for y in (-w*.305,w*.305):
            p.curve("Tail perimeter tube",[(x+.09,y,top+.008),(x-.052,y,top+.061),
                   (x-.154,y,top+.117)],.007,m["edge"])
        p.cube("Tail panel grip badge",(x-.109,0,top+.120),(.068,w*.50,.012),m["pad"],b=.003)
    else:
        length, rise = {
            "fighter-mini":(.135,.100),"fighter-ten":(.128,.092),"fighter-eleven":(.131,.077),
            "supreme":(.167,.109),"blade-mini":(.100,.078),"blade-gt":(.166,.110),
        }[layout]
        for si in (-1,1):
            cast_link(p,"Cast foot brace upright",(x+.036,top+.004),(x-length,top+rise),
                      si*w*.30,.020,.048,m["edge"],window=.65 if "blade" in layout else .41)
        # Angle the top grip to sit exactly on the two casting end caps.
        tray = p.cube("Angled heel pad",(x-length*.52,0,top+rise*.64),(.92*length,w*.66,.018),
                      m["pad"],b=.006)
        tray.rotation_euler.y = .47
        for index in range(5):
            p.rod("Raised heel scallop",(x-length*.96+index*length*.15,-w*.28,top+rise*(1-index*.096)),
                  (x-length*.96+index*length*.15,w*.28,top+rise*(1-index*.096)),
                  .0028,m["grip_high"],n=12)
    taillight_x = x-.151 if layout in ("gt","gt3","zt") else x-.121
    height = top+.112 if layout in ("gt","gt3","zt","p") else top+.072
    p.cube("Sealed rear lamp enclosure",(taillight_x,0,height),(.031,w*.66,.028),m["edge"],b=.005)
    p.cube("Red rear lens",(taillight_x-.017,0,height),(.007,w*.59,.015),m["red_lens"],b=.003)
    for y in (-w*.319,w*.319):
        p.cube("Rear amber signal diffuser",(taillight_x-.006,y,height+.002),(.022,.018,.011),m["amber"],b=.003)


def fender(p, name, cx, z, tire, width, span, lift, material, angular=False):
    angles = [radians(span[0]+(span[1]-span[0])*i/24) for i in range(25)]
    vertices = []
    for shell in (0, 1):
        for j in range(7):
            u = (j-3)/3
            for i, theta in enumerate(angles):
                line = tire + lift + shell*.004 - .009*abs(u)**2.5
                rx, rz = line*cos(theta), line*sin(theta)
                if angular:
                    rz = min(rz, line*.94) + (i/24-.5)*.010
                vertices.append((cx+rx,u*width/2,z+rz))
    s = 25*7
    faces = []
    for k in (0, s):
        faces.extend((k+j*25+i,k+j*25+i+1,k+(j+1)*25+i+1,k+(j+1)*25+i)
                     for j in range(6) for i in range(24))
    for edge in (0,6*25):
        faces.extend((edge+i,edge+i+1,edge+i+1+s,edge+i+s) for i in range(24))
    for edge in (0,24):
        faces.extend((edge+i*25,edge+(i+1)*25,edge+(i+1)*25+s,edge+i*25+s) for i in range(6))
    return p.mesh(name, vertices, faces, material, smooth=True)


def suspension(p, c, m):
    style = c["suspension"]
    layout = c["layout"]
    front = c["wheelbase"]/2
    rear = -front
    r, half = c["radius"], c["half_tire"]
    top, length, sx = c["deck_height"], c["deck_length"], c["steering_x"]
    hx = c["neck"]
    for side in (-1, 1):
        y = side*(half+.021)
        if style == "rigid":
            cast_link(p, "Rigid molded P65 front fork",
                      (front,r),(sx+.007,hx-.044),y,.025,.058,m["shell"],bend=.011)
            cast_link(p, "Rigid P65 rear carrier",
                      (rear,r),(-length*.43,top-.017),y,.019,.047,m["edge"])
        elif style == "telescope":
            for zoff, material, dia in ((.009,m["shell"],.024),(.0,m["silver"],.014)):
                a = (front+.010,y,r+.008+zoff)
                b = (front-.075,y,hx-.060-zoff)
                if material is m["shell"]:
                    b = tuple(Vector(a).lerp(Vector(b), .58))
                else:
                    a = tuple(Vector(a).lerp(Vector(b), .44))
                p.rod("Offset stanchion and lower seal",a,b,dia,material,n=32)
            cast_link(p,"Front cast axle lug",(front,r),(front-.042,r+.151),y,.027,.046,m["edge"],bend=.008)
            cast_link(p,"ZT long rear lower arm",(rear,r),(-length*.49,top-.019),y,.022,.058,
                      m["shell"],window=.58)
            extrusion(p,"ZT gray diagonal front shroud",[
                (front-.055,hx-.163),(front-.109,hx-.149),(length*.38,top-.048),
                (length*.48,top-.075),(front-.040,hx-.195),
            ],.016,m["silver_dark"],y=side*.063,radius=.006)
            extrusion(p,"ZT raised rear heel fairing",[
                (-length*.34,top-.014),(rear+.038,top+.095),
                (rear+.020,top+.071),(-length*.43,top-.042),
            ],.017,m["silver_dark"],y=side*c["deck_width"]*.34,radius=.004)
        elif style in ("wishbone","gt3","p100"):
            fore_top = (sx+.025,hx-.083)
            low_bind = (front-.14,top-.010)
            armfinish = m["silver_dark"] if style in ("p100","gt3") else m["shell"]
            cast_link(p,"Offset long upper front casting",(front,r),fore_top,y,
                      .029,.057 if style!="gt3" else .081,armfinish,bend=.011)
            cast_link(p,"Independent front wishbone linkage",(front-.014,r+.018),low_bind,y,
                      .022,.042,m["edge"],window=.55 if style=="wishbone" else 0)
            cast_link(p,"Rear angled single casting",(rear,r),(-length*.45,top-.011),y,
                      .027,.061,armfinish,window=.57 if style=="gt3" else 0)
            if style=="wishbone":
                cast_link(p,"Rear upper stabilizer link",(rear+.007,r+.022),(-length*.46,top+.043),
                          y*.88,.017,.026,m["edge"])
            if style=="gt3":
                p.label("Raised front casting logo","SEGWAY",(front-.036,y+side*.019,r+.145),
                        .012,m["accent"],angle=1.77)
            p.bolt("Upper front linkage pitman screw",(fore_top[0],y+side*.015,fore_top[1]),.010)
        else:
            armfinish = m["accent"] if "blade" in style else m["accent"] if style == "c-heavy" else m["edge"]
            arm_height = .079 if style in ("blade-gt","c-heavy","c-braced") else .061
            aperture = {
                "blade-mini": .70, "blade-gt": .42, "c-open": .70,
                "c-braced": .53, "c-heavy": .37,
            }[style]
            for positive, axle in ((1,front),(-1,rear)):
                pivot = (positive*length*.515,top-.008)
                cast_link(p,"C-profile forged swingarm",(axle,r),pivot,y,.023,
                          arm_height,armfinish,window=aperture,bend=.016 if style!="blade-mini" else .008)
                if style in ("c-heavy","c-braced","blade-gt"):
                    cast_link(p,"Panel relief rib in cast arm",
                              (axle-positive*.014,r+.012),(pivot[0]+positive*.023,pivot[1]-.005),
                              y+side*.014,.009,.026,m["shell"],bend=.008)
                p.rod("Pivot sleeve seal",(pivot[0],y-side*.010,pivot[1]),(pivot[0],y+side*.015,pivot[1]),
                      .018,m["edge"],n=28)
                p.bolt("Swingarm pivot fastener",(pivot[0],y+side*.016,pivot[1]),.011)
        for axle, axle_tag in ((front,"front"),(rear,"rear")):
            p.rod("Splash shield "+axle_tag+" brace",(axle,y,r),(axle-.061,side*half*.77,r*1.77),
                  .0038,m["edge"],n=12)
            p.bolt("Outer axle fastening socket",(axle,y+side*.015,r),.011)
    if style != "rigid":
        # Central shocks keep the linked stock wheels independently swappable.
        if style != "telescope":
            p.shock("Front exposed damper",(front-.019,0,r+.072),(sx-.058,0,hx-.068),
                    .013 if style!="c-heavy" else .016,
                    m["accent"] if style in ("wishbone","gt3") and c["motor"]=="both" else m["coil"])
        p.shock("Rear exposed damper",(rear+.023,0,r+.032),(-length*.345,0,top+.030),
                .014 if style!="c-heavy" else .017,
                m["accent"] if style=="telescope" or (style=="wishbone" and c["motor"]=="both") else m["coil"])
    lift = .028 if layout=="zt" else .015 if layout in ("gt3","fighter-ten") else .009
    fender(p,"Front formed splash guard",front,r,r,half*2+.017,(30,154),lift,
           m["matte"], angular=layout in ("zt","gt3","fighter-ten"))
    fender(p,"Rear full-span spray shield",rear,r,r,half*2+.021,(13,211),.013,
           m["matte"], angular=layout in ("gt3","fighter-ten","supreme"))
    if layout in ("p","gt","zt","gt3","blade-gt"):
        extrusion(p,"Descending rear spray and license flap",
                  [(rear-r*.85,r+r*.68),(rear-r*1.11,r+r*.194),
                   (rear-r*1.065,r+r*.15),(rear-r*.71,r+r*.62)],
                  half*1.45,m["matte"],radius=.003)
