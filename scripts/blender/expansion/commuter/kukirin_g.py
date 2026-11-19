"""Photo-guided exterior builders for the four KuKirin commuter expansion models."""

KUKIRIN_G = {
    'kukirin-g2-ultra': dict(
        wb=.961, r=.127, wide=.038, dl=.555, dw=.197, dz=.242, h=1.264, bar=.660,
        depth=.070, rake=.221, head=.425, deck_shift=-.016, heel=.080, guard=.032,
        body=(.071,.080,.088), arm_color=(.048,.054,.060), tread='block',
        stand=(-.107,.020,-.040), grip_style='dimples',
        reference='https://kukirinmobility.com/en-us/products/kukirin-g2-ultra-off-road-electric-scooter',
    ),
    'kukirin-g3': dict(
        wb=.947, r=.133, wide=.035, dl=.541, dw=.205, dz=.245, h=1.295, bar=.660,
        depth=.076, rake=.250, head=.425, deck_shift=-.016, heel=.083, guard=.022,
        body=(.008,.010,.012), arm_color=(.82,.204,.003), tread='block',
        stand=(-.134,.012,-.040), grip_style='diamond',
        reference='https://kukirin-escooter.com/products/kukirin-g3-electric-scooter',
    ),
    'kukirin-g4-max': dict(
        wb=1.115, r=.152, wide=.050, dl=.640, dw=.305, dz=.309, h=1.340, bar=.640,
        depth=.093, rake=.164, head=.574, deck_shift=-.011, heel=.075, guard=.027,
        body=(.011,.014,.017), arm_color=(.023,.029,.034), tread='block',
        stand=(.033,.020,-.051), grip_style='diamond',
        reference='https://www.kukirinfactory.com/kukirin-g4-max-specification',
    ),
    'kukirin-g2-vmp': dict(
        wb=.921, r=.127, wide=.037, dl=.545, dw=.181, dz=.230, h=1.250, bar=.625,
        depth=.069, rake=.191, head=.418, deck_shift=-.008, heel=.061, guard=.019,
        body=(.049,.057,.066), arm_color=(.039,.046,.054), tread='street',
        stand=(-.132,.015,-.038), grip_style='dimples',
        reference='https://kukirinmobility.com/es/products/kukirin-g2-vmp-spain-street-legal-dgt-approved',
    ),
}


def kukirin_planform(name, outline, bottom, top, material, parent='Chassis', radius=.004):
    count = len(outline)
    vertices = [(x, y, z) for z in (bottom, top) for x, y in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces.extend((i, (i+1) % count, (i+1) % count+count, i+count) for i in range(count))
    return mesh(name, vertices, faces, material, parent, b=radius)


def kukirin_deck_outline(center, length, width):
    front, rear, half = center + length/2, center - length/2, width/2
    return [
        (rear, -.72*half), (rear+.031, -half), (front-.037, -half), (front, -.69*half),
        (front, .69*half), (front-.037, half), (rear+.031, half), (rear, .72*half),
    ]


def kukirin_tag(obj, tag):
    obj['vfCockpit'] = tag
    return obj


def kukirin_anchor(name, loc):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = groups['Steering']
    obj.location = loc
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = .016


def kukirin_cockpit(c, stem_top, is_max):
    x, _, h = stem_top
    half, grip_length = c['bar']/2, .122 if is_max else .112
    inner, outer = half-grip_length, half-.005
    cent = (x-.013, 0, h)
    kukirin_anchor('VF_Cockpit_Center', cent)
    bar_pts = [(x-.024, -half, h+.016), (x-.016, -inner, h+.016),
               (x+.006, -half*.39, h+.006), cent, (x+.006, half*.39, h+.006),
               (x-.016, inner, h+.016), (x-.024, half, h+.016)]
    kukirin_tag(curve('Swept aluminum handlebar', bar_pts, .011, edge, 'Steering'), 'bar')
    rod('Cockpit central stem clamp', (x-.013, -.042, h), (x-.013, .042, h), .019, paint, 'Steering')
    for sy, side in [(-1, 'A'), (1, 'B')]:
        grip_tag, control_tag = 'grip'+side, 'control'+side
        start = Vector((x-.016, sy*inner, h+.016))
        end = Vector((x-.024, sy*outer, h+.016))
        kukirin_anchor('VF_Cockpit_Grip'+side, (start+end)/2)
        axis = (end-start).normalized()
        kukirin_tag(rod('Tapered molded rubber grip', start, end, .0155, grip, 'Steering', 32, r2=.0165), grip_tag)
        for p in (start, end):
            kukirin_tag(rod('Grip locking lip', p-axis*.002, p+axis*.003, .018, black, 'Steering', 28), grip_tag)
        kukirin_tag(rod('Textured bar-end cap', end+axis*.003, end+axis*.006, .0168, edge, 'Steering', 32, r2=.0153), grip_tag)
        # Real raised texture is baked into a single mesh per grip instead of one object per dimple.
        vertices, faces = [], []
        for row in range(12):
            p = start.lerp(end, (row+1)/13)
            for i in range(16):
                a = (i+(row % 2)*.5)*2*pi/16
                radial = Vector((cos(a), 0, sin(a)))
                tangent = Vector((-sin(a), 0, cos(a)))
                height, span = (.0021,.0031) if c['grip_style'] == 'diamond' else (.0016,.0024)
                base = p+radial*(.01535+row*.000095)
                n = len(vertices)
                vertices.extend([base+axis*.0028, base+tangent*span, base-axis*.0028,
                                 base-tangent*span, base+radial*height])
                faces.extend((n+j, n+(j+1) % 4, n+4) for j in range(4))
        kukirin_tag(mesh('Raised grip tread', vertices, faces, grip, 'Steering'), grip_tag)
        y = sy*(inner-.010)
        clamp = rod('Brake clamp', (x-.015, y-.008, h+.012), (x-.015, y+.008, h+.012), .017, black, 'Steering')
        kukirin_tag(clamp, control_tag)
        kukirin_tag(cube('Brake master housing', (x+.015,y,h+.006), (.043,.020,.024), black, 'Steering', .004), control_tag)
        kukirin_tag(curve('Forged reach brake lever', [(x+.03,y,h+.008),(x+.050,y+sy*.043,h),
                         (x+.037,y+sy*.092,h-.005)], .0047, edge, 'Steering'), control_tag)
        kukirin_tag(rod('Brake lever pivot pin', (x+.028,y,h-.004), (x+.028,y,h+.018), .0034, silver, 'Steering', 12), control_tag)
        control_y = sy*(inner-.041)
        kukirin_tag(cube('Handlebar switch housing', (x-.016,control_y,h+.023), (.036,.026,.035), black, 'Steering', .004), control_tag)
        kukirin_tag(cube('Control switch button', (x-.028,control_y,h+.043), (.014,.013,.005), accent if sy<0 else edge, 'Steering', .002), control_tag)
        if sy < 0:
            kukirin_tag(curve('Thumb throttle paddle', [(x-.019, control_y-.009,h+.023),
                             (x-.044,control_y-.008,h+.001),(x-.064,control_y-.008,h-.004)], .0065, black, 'Steering'), control_tag)
    if c['family'] == 'KuKirin G3 orange cast arms':
        dash = [(x-.062,-.047),(x-.020,-.061),(x+.040,-.048),(x+.066,-.024),
                (x+.066,.024),(x+.040,.048),(x-.020,.061),(x-.062,.047)]
        kukirin_planform('G3 faceted integrated instrument pod',dash,h-.016,h+.045,
                         black,'Steering',radius=.006)
        beam = [(x+.043,-.043),(x+.065,-.022),(x+.066,.022),(x+.043,.043),
                (x+.041,.041),(x+.061,.022),(x+.061,-.022),(x+.041,-.041)]
        kukirin_planform('G3 wraparound headlight lens',beam,h-.007,h+.004,
                         lens,'Steering',radius=.001)
    else:
        dash_size = (.111,.063,.026) if is_max else (.099,.078,.036)
        dashboard = cube('Central dashboard housing', (x-.012,0,h+.026), dash_size, black, 'Steering', .007)
        dashboard.rotation_euler.y = .14
    pane = cube('Central dashboard glass', (x-.012,0,h+.041 if is_max else h+.045),
                (.081,.046 if is_max else .060,.0034), screen, 'Steering', .002)
    pane.rotation_euler.y = .14
    rod('Central dashboard power button', (x+.039,0,h+.034), (x+.039,0,h+.039), .006, edge, 'Steering', 18)


def kukirin_side_stand(c):
    dz, dw = c['dz'], c['dw']
    x, trail, outboard = c['stand']
    y, z = -dw/2-.009, dz-c['depth']+.020
    mount = (x, y+.009, z+.005)
    pivot = Vector((x, y-.005, z))
    cube('Kickstand mounting plate',(x+.006,y+.005,z+.005),(.051,.019,.033),edge,b=.004)
    for dx in (-.015,.018):
        bolt('Kickstand mount fastener',(mount[0]+dx,y-.008,mount[2]),.0036)
    rod('Kickstand pivot barrel',pivot+Vector((0,-.012,0)),pivot+Vector((0,.011,0)),.010,black)
    bolt('Kickstand pivot retaining fastener',pivot+Vector((0,-.0135,0)),.0055)
    # The foot runs almost vertically in side profile, offset outward for support.
    # Keep the chassis baseline vertical so camera, ground and other assembly anchors stay aligned.
    end = Vector((x+trail,y+outboard,.011))
    neck = pivot.lerp(end,.22)+Vector((-.005,-.004,0))
    rod('Kickstand forged upper elbow', pivot, neck, .0095, black, n=20, r2=.0072)
    rod('Kickstand tapered arm', neck, end, .0072, black, n=20, r2=.0049)
    shoe = cube('Kickstand molded foot', (end.x,end.y,.0065), (.034,.023,.013), black, b=.005)
    shoe.rotation_euler.z = -.15
    for offset in (-.008,0,.008):
        cube('Kickstand foot texture', (end.x+offset,end.y,.0126),(.003,.018,.002), edge, b=.0008)
    top = pivot+Vector((.018,-.011,.006))
    lower = pivot.lerp(end,.28)+Vector((.003,-.011,.004))
    axis = lower-top
    radial = axis.normalized().cross(Vector((0,1,0))).normalized()
    wire = axis.normalized().cross(radial)
    points = [top+axis*(i/72)+.0034*(radial*cos(i*pi/6)+wire*sin(i*pi/6)) for i in range(73)]
    curve('Kickstand visible return spring',points,.00075,steel)


def kukirin_tread(x, c, parent):
    r, wide = c['r'], c['wide']
    street = c['tread'] == 'street'
    count, depth = (64,.0014) if street else (46,.0031)
    vertices, faces = [], []
    for i in range(count):
        angle = (i+.5*(i % 2))*2*pi/count
        for lane in (-.74,-.32,.32,.74):
            y = lane*wide
            radius = r-.026+.026*math.sqrt(1-lane*lane)
            twist = .034 if street else .040
            a = angle+twist*(1 if lane < 0 else -1)
            half_length, half_width = (.036,.0040) if street else (.045,.006 if abs(lane)<.5 else .005)
            n = len(vertices)
            for rr in (radius-.0028, radius+depth):
                for p,q in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                    u = a+p*half_length+q*twist*.37
                    vertices.append((x+rr*cos(u), y+q*half_width, r+rr*sin(u)))
            faces.extend(tuple(n+j for j in face) for face in
                         [(0,1,2,3),(4,5,6,7),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    mesh('Individual molded tire tread blocks',vertices,faces,rubber,parent,b=.00055)


def kukirin_g_body(e, c, front, rear):
    key = e['key']
    max_model, g3 = key == 'kukirin-g4-max', key == 'kukirin-g3'
    ultra, vmp = key == 'kukirin-g2-ultra', key == 'kukirin-g2-vmp'
    r, wide, dw = c['r'], c['wide'], c['dw']
    dl, dz, depth = c['dl'], c['dz'], c['depth']
    shift, h, head = c['deck_shift'], c['h'], c['head']
    f, b = shift+dl/2, shift-dl/2
    neck = front - (.063 if max_model else .032)
    arm = mat('KuKirin cast swingarm', c['arm_color'], .08 if g3 else .23, .41)
    dark_ink = mat('Graphite textured side graphics',(.048,.049,.049),.18,.36)
    gray_ink = mat('Satin dark silver details',(.285,.301,.314),.47,.33)
    deck_ink = accent if (vmp or g3) else (gray_ink if ultra else dark_ink)
    outline = kukirin_deck_outline(shift, dl, dw)
    kukirin_planform('Main cast battery deck', outline, dz-depth, dz-.006, paint, radius=.008)
    kukirin_planform('Rounded aluminum deck lid', kukirin_deck_outline(shift+.003,dl-.014,dw-.014),
                     dz-.011,dz+.001,edge,radius=.004)
    kukirin_planform('Sculpted rubber standing pad',kukirin_deck_outline(shift+.003,dl-.043,dw-.038),
                     dz-.002,dz+.0052,grip,radius=.003)
    cube('Removable battery pack' if max_model else 'Factory sealed battery pack',
         (shift-.045,0,dz-depth*.56),(dl*.72,dw*.79,depth*.60),black,'BatteryMount',.007)
    cube('Factory potted motor controller',(f-.097,0,dz-depth*.56),(.105,dw*.70,depth*.58),
         edge,'ControllerMount',.004)
    for i in range(17):
        xx = shift-.2 + i*.025
        for sy in (-1,1):
            for track in (.15,.29,.40):
                start = (xx-.007,sy*dw*track,dz+.0058)
                end = (xx+.005,sy*dw*(track+.035),dz+.0058)
                rod('Deck traction chevrons',start,end,.0013,black,n=6)
    for sy in (-1,1):
        yy = sy*(dw/2+.0006)
        for at in (b+.035,shift-.113,shift+.115,f-.045):
            bolt('Deck flush mounting screw',(at,sy*(dw/2-.014),dz+.002),.0034,axis='Z')
        for at in (b+.036,b+.098,f-.074,f-.040):
            bolt('Battery case side fastener',(at,yy,dz-depth*.76),.00265)
        if max_model:
            cube('G4 Max gold deck stripe',(shift,yy,dz-.041),(dl*.92,.002,.023),accent,b=.001)
            cube('G4 Max etched aluminum strip',(shift,yy+sy*.0018,dz-.039),(dl*.76,.002,.010),gray_ink,b=.0008)
            for i in range(16):
                t = shift-.202 + i*.026
                cube('G4 Max sidewall side perforation',(t,yy+sy*.0032,dz-.040),(.007,.0015,.006),dark_ink,b=.0004)
        elif g3:
            cube('G3 full orange deck flash',(shift-.011,yy,dz-.047),(dl*.78,.002,.025),accent,b=.0016)
        elif ultra:
            cube('G2 Ultra deck seam and wing',(b+.116,yy,dz-.056),(.092,.0020,.018),accent,b=.0018)
            cube('G2 Ultra brushed deck badge',(shift+.034,yy,dz-.043),(.178,.002,.019),gray_ink,b=.001)
        else:
            for i in range(6):
                at = f-.145-i*.022
                mark = cube('G2 VMP orange side graphic',(at,yy,dz-.043-(i % 2)*.01),(.017,.0018,.011),accent,b=.0011)
                mark.rotation_euler.y = -.41
    label('Deck model mark', 'G2 VMP' if vmp else 'KuKirin', (shift-.002,-dw/2-.004,dz-.042),
          .014 if max_model else .020, dark_ink if (max_model or ultra or g3) else deck_ink)
    socket_x = f-.115 if max_model else shift+.021
    rod('Charge socket rim',(socket_x,-dw/2,dz-.026),(socket_x,-dw/2-.006,dz-.026),.009,edge)
    rod('Weatherproof charging flap',(socket_x,-dw/2-.006,dz-.026),(socket_x,-dw/2-.009,dz-.026),.0073,black)
    if max_model:
        rod('Second factory charging flap',(socket_x-.031,-dw/2,dz-.026),(socket_x-.031,-dw/2-.009,dz-.026),.0073,black)
    pedal_back = b-(.137 if g3 else .106 if ultra else .094 if vmp else .114)
    pedal_front = b+.058
    hw = dw*(.90 if max_model else .84)
    profile('Raised angular rear heel brace',
            [(pedal_front,dz+.007),(b-.022,dz+.024),(pedal_back,dz+c['heel']),
             (pedal_back-.018,dz+c['heel']-.013),(b-.018,dz-.014),(pedal_front,dz-.018)],hw,paint,b=.007)
    for i in range(8):
        t = (i+1)/9
        xx = pedal_front+(pedal_back-pedal_front)*t
        zz = dz+.016+c['heel']*max(0,(t-.16)/.9)
        rod('Rear heel plate molded cross ribs',(xx,-hw*.43,zz),(xx,hw*.43,zz),.0023,grip,n=8)
    cube('Heel-mounted rear red lamp',(pedal_back-.013,0,dz+c['heel']-.011),(.014,hw*.85,.018),red,b=.003)
    for sy in (-1,1):
        yy = sy*(dw*.29 if max_model else dw*.235)
        thick = .040 if max_model else .033
        neck_top = head-.078 if max_model else head
        if max_model:
            profile('Twin fabricated lower headstock cheek',
                    [(f-.033,dz-.054),(f+.019,dz-.049),(neck+.035,neck_top-.012),
                     (neck+.020,neck_top+.020),(neck-.033,neck_top+.014),(f-.086,dz+.004)],
                    thick,paint,y=yy,b=.006)
        elif g3:
            profile('G3 rising triangular aluminum headstock',
                    [(f-.073,dz-.055),(f+.028,dz-.051),(neck+.024,head-.014),
                     (neck+.008,head+.047),(neck-.029,head+.032),(f-.047,dz+.022)],
                    thick,paint,y=yy,b=.008)
        else:
            profile('Wide sloping headstock side casting',
                    [(f-.069,dz-.051),(f+.027,dz-.052),(neck+.026,head-.014),
                     (neck+.014,head+.034),(neck-.038,head+.025),(f-.048,dz+.020)],
                    thick,paint,y=yy,b=.008)
            cube('Headstock orange identification tab',(neck-.069,yy+sy*.019,head-.105),(.026,.002,.014),accent,b=.001)
    cube('Central lower steering joint',(neck,0,head+.002),(.074,.081,.080),paint,'Steering',.009)
    for sy in (-1,1):
        y = sy*(wide+.024 if max_model else wide+.017)
        if max_model:
            top = Vector((neck+.021,y,.620))
            end = Vector((front,y,r))
            rod('G4 Max fork base casting',end,end.lerp(top,.58),.023,paint,'Steering',28)
            rod('G4 Max polished fork stanchion',end.lerp(top,.45),top,.0125,gray_ink,'Steering',28)
            rod('G4 Max stanchion seal',end.lerp(top,.52),end.lerp(top,.56),.024,edge,'Steering',28)
            rod('G4 Max upper fork barrel',top-Vector((0,0,.082)),top,.021,edge,'Steering',28)
        else:
            tip_y = y
            ax = front
            apex = neck-.043 if g3 else neck-.035
            pivot_z = r+.105 if g3 else r+.121
            center = (apex,tip_y,pivot_z)
            cast = [(apex-.030,pivot_z+.015),(apex+.020,pivot_z+.025),
                    (ax+.030,r+.026),(ax+.026,r-.016),(ax-.023,r-.023),
                    (apex-.037,pivot_z-.019)]
            profile('G3 upper orange curved front arm' if g3 else 'Swept front suspension arm',
                    cast,.024 if g3 else .027,arm,'Steering',y=tip_y,b=.007)
            rod('Cast front arm pivot bearing', (apex,tip_y-.016,pivot_z), (apex,tip_y+.017,pivot_z),.016,black,'Steering')
            bolt('Front arm pivot bolt',(center[0],tip_y+sy*.019,center[2]),.0064,'Steering')
            rod('Front steering upright',(neck,tip_y,head+.014),(apex+.006,tip_y,pivot_z+.006),.021,paint,'Steering')
            if ultra or vmp:
                for xx,zz in [(ax-.043,r+.024),(ax-.058,r+.034),(ax-.073,r+.044),(ax-.088,r+.054)]:
                    cube('Front arm cast inset',(xx,tip_y+sy*.014,zz),(.011,.0018,.008),accent if ultra else edge,'Steering',.001)
        rear_pivot = b+.002
        rear_z = dz-depth*.53
        end_x = rear
        rear_arm = [
            (rear_pivot+.035,rear_z+.029),(rear_pivot-.019,rear_z+.026),
            (end_x-.021,r+.025),(end_x-.026,r-.016),(end_x+.027,r-.024),
            (rear_pivot+.018,rear_z-.024),
        ]
        profile('G3 orange rear trailing arm' if g3 else 'Sculpted rear swingarm',
                rear_arm,.026 if not max_model else .030,arm,y=y,b=.007)
        rod('Rear swingarm pivot bearing',(rear_pivot,y-.018,rear_z),(rear_pivot,y+.017,rear_z),.016,edge)
        bolt('Rear swingarm pivot bolt',(rear_pivot,y+sy*.019,rear_z),.007)
        if max_model or ultra or vmp:
            shock('Protected rear coilover',(b-.081,y*.93,dz+c['heel']-.004),
                  (rear+.059,y*.93,r+.027),.011 if max_model else .0085,black)
        for i in range(5):
            xx = end_x+.025+i*.023
            zz = r-.002+i*.009
            decal = cube('Rear swingarm orange cast highlight',(xx,y+sy*.014,zz),
                         (.017,.0015,.011 if g3 else .015),edge if g3 else accent,b=.0012)
            decal.rotation_euler.y = -.42
    if max_model:
        for z in (.540,.627):
            cube('G4 Max structural fork bridge',(neck+.020,0,z),(.070,2*wide+.075,.039),paint,'Steering',.008)
        for sy in (-1,1):
            cube('G4 Max crown lock ring',(neck+.022,sy*(wide+.024),.647),(.036,.034,.010),accent,'Steering',.003)
        rod('G4 Max central circular lamp bucket',(neck+.047,0,.542),(neck+.104,0,.542),.040,black,'Steering',44)
        rod('G4 Max circular glass headlight',(neck+.103,0,.542),(neck+.108,0,.542),.032,lens,'Steering',44)
        for sy in (-1,1):
            cube('G4 Max low front marker light',(f+.013,sy*dw*.43,dz-.035),(.018,.021,.017),lens,b=.002)
    # Fender spans and flares differ for the round G3 and the wider angular models.
    fender('Contoured front mudguard',front,r+(c['guard'] if max_model else .013),
           wide*2+(.032 if max_model else .023),angular=max_model)
    fender('Close-fitting rear spray guard',rear,r+.014,wide*2+(.031 if max_model else .024),angular=True,rear=True)
    if vmp:
        profile('VMP rear license carrier',[(rear-.113,r+.081),(rear-.138,r+.026),
                (rear-.129,r+.024),(rear-.103,r+.080)],wide*1.9,black,b=.002)
        for sy in (-1,1):
            cube('VMP rear indicators',(pedal_back-.014,sy*dw*.440,dz+c['heel']-.013),
                 (.015,.019,.016),accent,b=.002)
    sx = neck; tx = sx-c['rake']
    stem_bottom = Vector((sx,0,head+.037))
    stem_top = Vector((tx,0,h-.041))
    stem = cube('Rectangular extruded steering mast', (stem_bottom+stem_top)/2,
                (.052,.046,(stem_top-stem_bottom).length), paint, 'Steering', .005)
    stem.rotation_euler = (stem_top-stem_bottom).to_track_quat('Z','Y').to_euler()
    inset_a, inset_b = stem_bottom.lerp(stem_top,.17), stem_bottom.lerp(stem_top,.88)
    inset_a.y = inset_b.y = -.024
    inset = cube('Steering mast inset front face', (inset_a+inset_b)/2,
                 (.023,.0024,(inset_b-inset_a).length),edge,'Steering',.0013)
    inset.rotation_euler = (inset_b-inset_a).to_track_quat('Z','Y').to_euler()
    if max_model:
        for y in (-.031,.031):
            rail = cube('G4 Max parallel stem side extrusion', (stem_bottom+stem_top)/2+Vector((.004,y,0)),
                        (.018,.012,(stem_top-stem_bottom).length*.86),edge,'Steering',.003)
            rail.rotation_euler = stem.rotation_euler
    bolt('Folding hinge axle',(sx,-.043,head-.010),.010,'Steering')
    latch = cube('Machined folding safety lever',(sx-.039,-.008,head+.039),(.022,.042,.086),
                 black,'Steering',.004)
    latch.rotation_euler.y = -.19
    bolt('Secondary folding latch safety pin',(sx-.041,-.034,head+.068),.005,'Steering')
    label_center = stem_bottom.lerp(stem_top,.55)
    label('KuKirin manufacturer vertical stem decal', 'KuKirin', (label_center.x,-.026,label_center.z),
          .023, accent if ultra or vmp else gray_ink, 'Steering',angle=math.atan2(stem_top.z-stem_bottom.z,stem_top.x-stem_bottom.x))
    for sy, side in ((-1,'A'),(1,'B')):
        yy = sy*.022
        upper_cable_end = (tx+.085,sy*.050,h-.258)
        kukirin_anchor('VF_Cockpit_Cable'+side, upper_cable_end)
        brake = (tx+.025,sy*(c['bar']/2-(.122 if max_model else .112)-.010),h-.037)
        upper_cable = curve('Cockpit brake cable slack',
                            [brake,(tx+.072,sy*.112,h-.137),upper_cable_end],
                            .00265,black,'Steering')
        kukirin_tag(upper_cable,'cable')
        curve('Lower routed brake cable',
              [upper_cable_end,(sx+.036,yy,head+.225),(sx+.035,yy,head+.020),
               (f-.039,sy*(dw*.35),dz-.025)],.00265,black,'Steering')
    if not max_model and not g3:
        cube('Cockpit lamp lens housing',(tx+.063,0,h-.063),(.026,.063,.032),black,'Steering',.005)
        for yy in (-.016,.016):
            cube('Split high headlamp optical pane',(tx+.077,yy,h-.063),(.004,.025,.020),lens,'Steering',.003)
    kukirin_cockpit(c, stem_top, max_model)
    kukirin_side_stand(c)
