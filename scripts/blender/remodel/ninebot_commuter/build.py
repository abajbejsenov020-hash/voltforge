"""Rebuild named commuter Ninebots from the exact model's catalog photographs.

Run Blender in background mode with --python this file and optional --output.
Hidden components are visual envelopes, not measurements or manufacturer CAD.
"""
import argparse
import importlib.util
import json
import sys
from dataclasses import replace
from math import cos, pi, sin
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT))
from configs import MODELS, PLATFORMS, appearance_note

primitive_spec = importlib.util.spec_from_file_location(
    'voltforge_ninebot_primitives', ROOT / 'scripts/blender/expansion/commuter/primitives.py'
)
geo = importlib.util.module_from_spec(primitive_spec)
primitive_spec.loader.exec_module(geo)

CHASSIS = 'Chassis'
STEERING = 'Steering'
FRONT_WHEEL = 'FrontWheel'
REAR_WHEEL = 'RearWheel'
MOUNTS = (CHASSIS, STEERING, FRONT_WHEEL, REAR_WHEEL,
          'BatteryMount', 'ControllerMount', 'MotorMount')


def from_hex(value):
    def linear(channel):
        n = channel / 255
        return n / 12.92 if n <= .04045 else ((n + .055) / 1.055) ** 2.4
    return tuple(linear(int(value[i:i+2], 16)) for i in (0, 2, 4))


def material(name, rgb, metal=.0, rough=.5, emit=.0):
    return geo.mat(name, from_hex(rgb), metal, rough, emit)


def materials(spec):
    return {
        'paint': material('Model powder coat', spec.paint, .28, .43),
        'rubber': material('Tire rubber', '262728', .0, .86),
        'tread': material('Tire rubber tread detail', '222325', .0, .89),
        'grip': material('Textured rubber grips', '303134', .0, .83),
        'mat': material('Deck traction rubber', '3a3d40', .0, .89),
        'plastic': material('Molded fender polymer', '25282b', .0, .63),
        'black': material('Black', '202225', .07, .66),
        'rim': material('Machined gunmetal', '232628', .27, .65),
        'cast': material('Anodized gunmetal', '434749', .30, .58),
        'steel': material('Axle hardware steel', '8e989c', .63, .31),
        'accent': material('Model accent', spec.accent, .25, .48),
        'reflector': material('Amber reflector', 'ea9b3a', .02, .32, .08),
        'rotor': material('Brake rotor', '9caaae', .74, .33),
        'red': material('Red optical lens', 'b62028', .0, .27, .32),
        'lens': material('Pearlescent optical lens', 'e5edef', .05, .31, .42),
        'glass': material('Smoked dashboard glass', '202b32', .18, .18),
        'markings': material('Printed markings', '9ea5a8', .04, .50),
        'screen': material('Display markings', '8bbdc7', .0, .31, .31),
    }


def deck_loft(name, sections, material, parent=CHASSIS):
    """Extrude changing rounded transverse sections rather than stack boxes."""
    contour = [(-.40, 0), (.40, 0), (.48, .12), (.50, .28), (.50, .78),
               (.46, .94), (.39, 1), (-.39, 1), (-.46, .94), (-.50, .78),
               (-.50, .28), (-.48, .12)]
    vertices = [(x, side * width, bottom + height * (top - bottom))
                for x, width, bottom, top in sections for side, height in contour]
    return loft(name, vertices, len(contour), len(sections), material, parent)


def loft(name, vertices, span, count, material, parent, smooth=False):
    faces = [tuple(reversed(range(span))), tuple(range((count-1)*span, count*span))]
    for step in range(count-1):
        for i in range(span):
            j = (i+1) % span
            faces.append((step*span+i, step*span+j, (step+1)*span+j, (step+1)*span+i))
    return geo.mesh(name, vertices, faces, material, parent, smooth=smooth)


def line_box(name, start, end, width, depth, mat, parent=CHASSIS, bevel=.004):
    a, b = Vector(start), Vector(end)
    part = geo.cube(name, (a+b)/2, (width, depth, (b-a).length), mat, parent, bevel)
    part.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return part


def ring_tire(x, radius, width, material, parent):
    section = [(-.48, .60), (-.50, .69), (-.49, .82), (-.39, .93),
               (-.23, .982), (0, 1), (.23, .982), (.39, .93),
               (.49, .82), (.50, .69), (.48, .60), (.41, .60), (-.41, .60)]
    count = 84
    verts = [(x+radius*rf*cos(i*2*pi/count), width*yf, radius+radius*rf*sin(i*2*pi/count))
             for yf, rf in section for i in range(count)]
    faces = []
    for row in range(len(section)):
        next_row = (row+1) % len(section)
        for i in range(count):
            j = (i+1) % count
            faces.append((row*count+i, row*count+j, next_row*count+j, next_row*count+i))
    geo.mesh('Crowned tire carcass with molded sidewalls', verts, faces, material, parent, smooth=True)


def tire_detail(x, radius, width, stock_solid, mats, parent):
    vertices, faces = [], []
    for i in range(48):
        a = i*pi/24
        for side in (-1, 1):
            count = len(vertices)
            for angle, lateral, rf in ((a, .05, 1.001), (a-.062, .34, .967),
                                       (a-.077, .38, .952), (a-.024, .08, 1.001)):
                vertices.append((x+radius*rf*cos(angle), side*width*lateral,
                                 radius+radius*rf*sin(angle)))
            faces.append(tuple(range(count, count+4)))
    geo.mesh('Directional tread relief', vertices, faces, mats['tread'], parent)
    if stock_solid:
        radial = radius * .783
        for side in (-1, 1):
            y = side*width*.503
            for i in range(10):
                a = i*pi/5
                cx, cz = x+radial*cos(a), radius+radial*sin(a)
                o = geo.cube('Solid tire pressure cavity', (cx, y, cz),
                             (.013, .0007, .005), mats['tread'], parent, .001)
                o.rotation_euler.y = -a - pi/2


def rotor(x, y, radius, mat, parent):
    geo.ring('Perforated stainless brake track', x, y, radius, radius*.58,
             radius*.46, .002, mat, parent, n=64)
    for i in range(6):
        a = i*pi/3
        geo.rod('Rotor forged spider',
                (x+cos(a)*radius*.20, y, radius+sin(a)*radius*.20),
                (x+cos(a+.14)*radius*.51, y, radius+sin(a+.14)*radius*.51),
                .0045, mat, parent, n=7)


def wheel(x, spec, mats, front):
    name = FRONT_WHEEL if front else REAR_WHEEL
    radius, width = spec.radius, spec.tire_width
    ring_tire(x, radius, width, mats['rubber'], name)
    tire_detail(x, radius, width, spec.platform == 'e2' and spec.motor == 'front', mats, name)
    driven = spec.motor == ('front' if front else 'rear')
    drum = spec.brakes == ('front-drum' if front else 'rear-drum')
    disc = spec.brakes == 'both-disc' or (front and spec.brakes == 'front-disc')
    vented_drum = front and drum
    solid = .62 if driven else .375 if vented_drum else .55 if drum else .24
    for side in (-1, 1):
        y = side*width*.43
        geo.ring('Recessed wheel rim', x, y, radius, radius*.657, radius*.605,
                 .0035, mats['rim'], name, n=56)
        if spec.accent_ring:
            geo.ring('Regional colored rim pinstripe', x, side*(width*.50+.0012),
                     radius, radius*.793, radius*.767, .0014, mats['pinstripe'], name, n=72)
        if not driven:
            geo.rod('Sealed brake hub' if drum else 'Bearing hub',
                    (x,side*.004,radius), (x,side*width*.45,radius),
                    radius*solid, mats['rim'], name, n=48)
        if not driven and (not drum or vented_drum):
            for i in range(5):
                a = i*2*pi/5
                geo.rod('Five curved wheel spokes',
                        (x+radius*.20*cos(a),y*.35,radius+radius*.20*sin(a)),
                        (x+radius*.625*cos(a+.19),y,radius+radius*.625*sin(a+.19)),
                        radius*.063,mats['cast'],name,n=9)
        geo.rod('Sealed axle bearing', (x, y, radius), (x, y+side*.007, radius),
                radius*.126, mats['steel'], name, n=24)
    if driven:
        geo.rod('Sealed hub motor housing', (x,-width*.44,radius), (x,width*.44,radius),
                radius*.602, mats['rim'], 'MotorMount', n=56)
        for side in (-1, 1):
            y = side*width*.456
            geo.rod('Recessed motor center disc', (x,y,radius), (x,y+side*.0015,radius),
                    radius*.541,mats['cast'],'MotorMount',n=56)
            for i in range(6):
                a = i*pi/3
                geo.rod('Motor cover screw',
                        (x+radius*.503*cos(a),y,radius+radius*.503*sin(a)),
                        (x+radius*.503*cos(a),y+side*.0024,radius+radius*.503*sin(a)),
                        .0018,mats['steel'],'MotorMount',n=6)
    if disc:
        y = -width*.505
        rotor(x, y, radius, mats['rotor'], name)
        p = STEERING if front else CHASSIS
        geo.cube('Brake caliper body', (x-radius*.42, y-.005, radius*1.38),
                 (.036,.017,.026), mats['accent'] if spec.platform in ('g3','f3')
                 else mats['black'], p, .004)
    for side in (-1, 1):
        y = side*(width*.72)
        geo.bolt('Axle nut', (x,y,radius), .007, STEERING if front else CHASSIS)


def mudguard(x, spec, mats, front):
    radius = spec.radius
    width = spec.tire_width + (.013 if front else .018)
    polymer = mats.get('fender',mats['plastic'])
    start = .28 if not front and spec.platform in ('g2','f3','g3') else .38
    end = 2.64 if front else 3.12
    arch = []
    n = 36
    for j in range(n+1):
        angle = start+(end-start)*j/n
        outer = radius+.009+(.010 if spec.platform in ('g3','f3') else .003)
        cap = outer-.004
        if not front and spec.platform in ('g3', 'f3', 'g2'):
            radius_top = min(outer*sin(angle), outer*.93)
        else:
            radius_top = outer*sin(angle)
        inner = cap
        px, pz = x+outer*cos(angle), radius+radius_top
        ix, iz = x+inner*cos(angle), radius+inner*sin(angle)
        arch.extend([(px,-width*.38,pz), (px,-width*.50,pz-.006), (ix,-width*.50,iz-.004),
                     (ix,width*.50,iz-.004), (px,width*.50,pz-.006), (px,width*.38,pz)])
    loft('Rolled molded mudguard shell', arch, 6, n+1, polymer,
         STEERING if front else CHASSIS, True)
    if front:
        return
    if spec.platform in ('g3','f3','g2'):
        geo.profile('Squared rear tail cowl',
                    [(x-radius*.91,radius*1.36),(x-radius*.96,radius*1.87),
                     (x-radius*.68,radius*2.10),(x+radius*.41,radius*2.11),
                     (x+radius*.61,radius*1.99),(x+radius*.01,radius*2.01),
                     (x-radius*.63,radius*1.98)],
                    width*.97,mats['plastic'],b=.004)
        top=spec.deck_top
        w=spec.deck_width
        deck_loft('Tapered rear footboard rise', [
            (spec.deck_start-.018,w*.72,top-.010,top+.018),
            (spec.deck_start+.018,w*.82,top-.008,top+.020),
            (spec.deck_start+.082,w*.87,top-.004,top+.005),
        ],mats['mat'])
    lx, lz = x-radius*.85, radius+.055
    geo.cube('Rear lamp molding', (lx,0,lz), (.026,width*.82,.022), mats['plastic'], b=.006)
    geo.cube('Central red stop and position lens', (lx-.014,0,lz+.001),
             (.005,width*.67,.013), mats['red'], b=.003)
    if spec.rear_plate:
        geo.profile('Rear plate and spray holder',
                    [(lx-.011,lz+.014), (lx-.026,lz-.009), (lx-.031,radius*.48),
                     (lx-.024,radius*.45), (lx-.013,lz-.01), (lx+.007,lz+.009)],
                    width*.60, mats['plastic'], b=.003)
        geo.cube('Rear flat reflector', (lx-.03,0,radius*.52),
                 (.003,width*.58,.012), mats['red'], b=.001)
    else:
        geo.cube('Rear fender grip latch', (x,0,radius*2+.013),
                 (.032,.025,.013),mats['black'],b=.004)


def chassis(spec, stem_foot, mats):
    a, b, w = spec.deck_start, spec.deck_end, spec.deck_width
    top = spec.deck_top
    bottom = top-spec.shell_height
    # Tapered cast tail, flat center extrusion, and two gradual transitions at the nose.
    deck_loft('Tapered Ninebot deck casting', [
        (a-.045, w*.55, bottom+.018, top-.013),
        (a-.021, w*.86, bottom+.006, top-.002),
        (a+.008, w, bottom, top),
        (b-.085, w, bottom, top),
        (b-.029, w*.94, bottom+.002, top+.002),
        (b, w*.70, bottom+.010, top+.012),
    ], mats['paint'])
    deck_loft('Rounded flush anti-slip top pad', [
        (a-.013, w*.66, top-.001, top+.004),
        (a+.017, w*.90, top-.001, top+.005),
        (b-.078, w*.89, top-.001, top+.005),
        (b-.031, w*.72, top+.003, top+.009),
    ], mats['mat'])
    if spec.platform in ('g3','f3'):
        neck = [
            (b-.070,w*.89,bottom+.004,top+.002),
            (b+.003,w*.72,bottom+.013,top+.041),
            (b+.053,w*.61,top+.045,top+.104),
            (stem_foot-.019,w*.48,top+.118,top+.185),
            (stem_foot+.035,w*.37,top+.155,top+.191),
        ]
    elif spec.platform == 'e2':
        neck = [
            (b-.15,w*.95,bottom,top+.001),
            (b-.09,w*.89,bottom+.001,top+.007),
            (b-.031,w*.79,bottom+.005,top+.027),
            (b+.016,w*.68,bottom+.018,top+.066),
            (b+.054,w*.59,bottom+.043,top+.107),
            (stem_foot-.017,w*.50,top+.032,top+.151),
            (stem_foot+.027,w*.42,top+.067,top+.171),
        ]
    elif spec.platform == 'es':
        neck = [
            (b-.090,w*.85,bottom,top), (b-.026,w*.75,bottom+.005,top+.008),
            (b+.028,w*.62,bottom+.025,top+.039), (b+.076,w*.49,top+.010,top+.086),
            (stem_foot-.012,w*.46,top+.078,top+.142),
            (stem_foot+.026,w*.39,top+.104,top+.161),
        ]
    else:
        neck = [
            (b-.059,w*.85,bottom+.003,top+.006),
            (b+.020,w*.71,bottom+.022,top+.042),
            (b+.053,w*.57,top+.035,top+.093),
            (stem_foot-.009,w*.47,top+.117,top+.180),
            (stem_foot+.026,w*.39,top+.142,top+.181),
        ]
    deck_loft('Swept monocoque steering neck', neck, mats['paint'])
    if spec.platform in ('g3','f3'):
        geo.profile('Integral lock loop backing casting',
                    [(b+.017,top+.057), (stem_foot-.028,top+.126),
                     (stem_foot-.013,top+.117), (b+.031,top+.048)],
                    .060,mats['paint'],b=.004)
        loop_path = [(b+.033,0,top+.076), (b+.062,0,top+.075),
                     (b+.084,0,top+.102), (b+.068,0,top+.129),
                     (b+.052,0,top+.117)]
        geo.curve('Integral locking rim loop', loop_path, .009, mats['cast'])
    # Molded seams run down each chassis edge and surround the charge door.
    for side in (-1,1):
        y=side*w*.478
        geo.curve('Continuous deck extrusion step joint',
                  [(a-.006,y*.90,bottom+.013), (a+.035,y,bottom+.011),
                   (b-.073,y,bottom+.011), (b-.019,y*.88,bottom+.014)],
                  .0014,mats['black'])
        if spec.platform == 'es' and spec.underglow:
            strip = material('ES floor ambient light', '704bb9', .04, .42, .22)
            geo.cube('Inset ambient light bar', ((a+b)/2,y,bottom+.006),
                     ((b-a)*.81,.003,.0045), strip, b=.001)
        if spec.platform in ('g3','f3','g2'):
            for j in range(3):
                geo.cube('Side panel cooling recess',
                         (a+.052+j*.023,y*1.037,bottom+.022),
                         (.013,.003,.013),mats['black'],b=.002)
    if spec.platform != 'es':
        charge_x = b-.119 if spec.platform == 'g30' else b-.077
        geo.cube('Recessed charge port surround', (charge_x,-w*.505,bottom+.027),
                 (.047,.008,.025),mats['black'],b=.005)
        geo.cube('Gasketed rubber charge cover', (charge_x,-w*.553,bottom+.027),
                 (.037,.005,.018),mats['plastic'],b=.004)
    for lane in (-.32,-.16,0,.16,.32):
        geo.rod('Fine anti-slip mat channels',(a+.028,lane*w,top+.0050),
                (b-.079,lane*w,top+.0050),.00055,mats['black'],n=7)
    for x in (a+.028,b-.09):
        for side in (-1,1):
            geo.bolt('Flush deck fastener',(x,side*w*.395,top+.004),.0029,axis='Z')
    for side in (-1,1):
        stamp = geo.label('Ninebot deck printing', 'ninebot',
                          ((a+b)/2,side*(w*.506),bottom+spec.shell_height*.61),
                          .013, mats['markings'])
        if side > 0:
            stamp.rotation_euler.z = pi
    geo.curve('Folded steel side stand',
              [(a+.18,-w*.43,bottom+.004), (a+.16,-w*.57,.055), (a+.13,-w*.77,.012)],
              .0047,mats['cast'])
    geo.cube('Rubber side stand foot',(a+.13,-w*.77,.009),(.023,.019,.008),mats['plastic'],b=.002)
    if spec.platform == 'es':
        geo.profile('Low step-to-fold pedal',
                    [(stem_foot-.089,top+.078), (stem_foot-.104,top+.117),
                     (stem_foot-.089,top+.125), (stem_foot-.067,top+.073)],
                    .033,mats['black'],b=.004)
        geo.cube('ES folding pedal red insert',(stem_foot-.096,-.021,top+.093),
                 (.025,.007,.009),mats['accent'],b=.003)


def fork(spec, front, foot, hinge_z, mats):
    r = spec.radius
    if spec.front == 'dual-hydraulic':
        for side in (-1,1):
            y = side*(spec.tire_width*.72+.008)
            end = (front-.077,y,hinge_z+.048)
            geo.rod('Twin hydraulic fork lower shell',(front,y,r),(front-.037,y,r+.161),
                    .0183,mats['paint'],STEERING,26,r2=.0205)
            geo.rod('Twin exposed stanchion',(front-.035,y,r+.148),end,
                    .0102,mats['steel'],STEERING,28)
            geo.rod('Hydraulic fork dust collar',(front-.034,y,r+.146),
                    (front-.039,y,r+.173),.019,mats['black'],STEERING,24)
            geo.profile('Tapered dropout casting',
                        [(front-.011,r-.020),(front+.020,r-.009),(front+.018,r+.052),
                         (front-.033,r+.064),(front-.035,r+.011)], .022,
                        mats['cast'],STEERING,y=y,b=.004)
            if spec.platform == 'g3':
                geo.profile('MAX G3 wide tapered lower fork shroud',
                            [(front+.013,r-.015),(front+.026,r+.036),
                             (front+.011,r+.123),(front-.012,r+.186),
                             (front-.069,r+.180),(front-.062,r+.129),
                             (front-.038,r+.039),(front-.032,r-.009)],
                            .028,mats['paint'],STEERING,y=y*1.31,b=.008)
                pivot = (front-.045, side*(abs(y)*1.31+.013), r+.157)
                cap = (pivot[0],pivot[1]+side*.005,pivot[2])
                geo.rod('Red hydraulic shroud pivot trim',pivot,cap,.0155,
                        mats['accent'],STEERING,28)
                geo.rod('Recessed shroud fastener',cap,(cap[0],cap[1]+side*.0015,cap[2]),
                        .0098,mats['black'],STEERING,18)
            else:
                geo.profile('Flat lower fork armor',
                            [(front+.004,r-.002),(front-.010,r+.109),
                             (front-.029,r+.172),(front-.056,r+.163),
                             (front-.040,r+.110),(front-.027,r+.017)],
                            .019,mats['paint'],STEERING,y=y*1.185,b=.006)
        geo.rod('Hydraulic fork top bridge',(front-.080,-.067,hinge_z+.019),
                (front-.080,.067,hinge_z+.019),.022,mats['paint'],STEERING,n=24)
        px=front+.018
        geo.curve('Protective front fork crown loop',
                  [(px,-.064,r+.150),(px,-.057,r+.211),
                   (px,0,r+.233),(px,.057,r+.211),(px,.064,r+.150)],
                  .0095,mats['paint'],STEERING)
    else:
        for side in (-1,1):
            yc=side*(spec.tire_width*.72+.004)
            end=(front-.069,yc*.82,hinge_z-.037)
            r1=.019 if spec.platform in ('g30','g2') else .016 if spec.platform=='e2' else .0127
            geo.rod('Sculpted fork leg',(front,yc,r-.007),end,r1,
                    mats['paint'],STEERING,24,r2=r1*.88)
        upper=(foot,0,hinge_z+.002)
        lower=(front-.052,0,max(r+.12,hinge_z-.115))
        if spec.front in ('single-spring','single-hydraulic','es-spring'):
            shell=.028 if spec.platform in ('g2','es') else .024
            geo.rod('Enclosed coaxial front damper',lower,upper,
                    shell,mats['paint'],STEERING,36)
            collar=Vector(lower).lerp(Vector(upper),.22)
            tail=Vector(lower)-Vector(upper)
            geo.rod('Front suspension gaiter',collar+tail*.20,collar-tail*.18,
                    shell*1.06,mats['black'],STEERING,36)
            for i in range(4 if spec.platform == 'es' else 3):
                a=collar+tail*(.19-i*.08)
                geo.rod('Gaiter seam',a,a+tail*.025,shell*1.11,
                        mats['steel'] if spec.platform=='es' else mats['plastic'],STEERING,24)
        else:
            geo.rod('Tapered sealed fork crown',lower,upper,.025,
                    mats['paint'],STEERING,28,r2=.030)
    for side in (-1,1):
        y=side*(spec.tire_width*.74+.012)
        piece=geo.cube('Regulatory side reflector',(front-.023,y,r+.068),
                        (.012,.004,.039),mats['reflector'],STEERING,.004)
        piece.rotation_euler.y=-.20


def rear_axle(spec, rear, mats):
    z=spec.radius
    top=spec.deck_top
    start=spec.deck_start
    for side in (-1,1):
        y=side*(spec.tire_width*.8+.013)
        if spec.rear == 'fixed':
            geo.profile('Cast tapered rear axle support',
                        [(start+.055,top-.027),(start+.019,top+.015),
                         (rear-.008,z+.022),(rear-.018,z-.012),
                         (start-.005,top-.049)],.019,mats['paint'],y=y,b=.004)
            if spec.platform == 'e2' and spec.motor == 'rear':
                geo.profile('E2 Pro longer rear hub-side cover',
                            [(rear-.039,z-.019),(rear-.028,z+.015),
                             (rear+.053,z+.030),(start+.050,top-.010),
                             (start+.069,top-.040),(rear+.076,z-.025)],
                            .020,mats['plastic'],y=y+side*.005,b=.006)
        else:
            geo.profile('Pivoting rear swingarm',
                        [(start+.069,top-.031),(start+.039,top+.012),(rear-.008,z+.020),
                         (rear-.016,z-.018),(start+.012,top-.057)],
                        .021,mats['cast'],y=y,b=.004)
            geo.bolt('Rear linkage pivot',(start+.036,side*(abs(y)+.013),top-.019),.008)
            if spec.rear in ('twin-spring','twin-hydraulic'):
                low=(rear+.017,y,z+.018)
                high=(start+.007,y,top+.068)
                if spec.rear == 'twin-spring':
                    geo.rod('Capped rear twin spring cartridge',low,high,.015,mats['black'])
                    a=Vector(low).lerp(Vector(high),.12)
                    b=Vector(low).lerp(Vector(high),.36)
                    geo.rod('Rear cartridge warning sleeve',a,b,.0155,mats['accent'])
                    geo.rod('Twin rear piston',b,high,.008,mats['steel'])
                else:
                    geo.shock('Rear hydraulic spring', low, high, .010, coil=mats['accent'])
            elif side < 0:
                geo.cube('Rear suspension elastomer block',
                         (start+.038,y*.85,top-.048),(.055,.041,.027),mats['black'],b=.004)
        piece=geo.cube('Independent rear axle reflector',
                        (rear+.042,side*(abs(y)+.014),z+.008),
                        (.043,.0045,.011),mats['accent'] if spec.accent_ring or spec.platform=='es'
                        else mats['reflector'],b=.0035)
        piece.rotation_euler.y=.12


def cockpit(spec, name, foot, hinge_z, mats):
    root = Vector((foot,0,hinge_z + .037))
    tx = foot-spec.rake
    top = Vector((tx,0,spec.height-.054))
    stem_finish=mats.get('stem',mats['paint'])
    if spec.platform == 'e2':
        stem_points = [root, root.lerp(top,.58), root.lerp(top,.88),
                       Vector((tx+.013,0,top.z-.028)), Vector((tx+.054,0,top.z+.010))]
        geo.curve('E2 swept stem with integrated bar rise',stem_points,.0175,mats['paint'],STEERING)
        top = stem_points[-1]
        geo.rod('E2 tubular lower folding pedestal',
                (foot+.004,0,hinge_z-.004),root,.025,mats['paint'],STEERING,32)
    elif spec.platform in ('g3','f3'):
        line_box('Flattened tapered steering mast',root,top,.040,.040,mats['paint'],STEERING,.008)
        lower=root.lerp(top,.016)
        upper=root.lerp(top,.27)
        line_box('Lower mast reinforcing rib',lower+Vector((-.008,0,0)),
                 upper+Vector((-.008,0,0)),.043,.046,mats['paint'],STEERING,.007)
    else:
        radius=.0275 if spec.platform=='es' else .021 if spec.platform in ('g2','g30') else .0183
        geo.rod('Round extruded steering mast',root,top,radius,stem_finish,STEERING,44,
                r2=radius*.95)
    geo.rod('Split folding headstock collar',(foot+.005,0,hinge_z-.019),root,
            .032 if spec.platform in ('g3','g2','g30','es') else .027,
            mats['paint'],STEERING,32)
    geo.rod('Steel folding pin',(foot+.011,-.031,hinge_z+.002),
            (foot+.011,.031,hinge_z+.002),.008,mats['steel'],STEERING,n=20)
    if spec.platform != 'es':
        geo.profile('Safety catch lever',
                    [(foot-.038,hinge_z-.016),(foot-.029,hinge_z+.048),
                     (foot-.017,hinge_z+.052),(foot-.018,hinge_z-.012)],.013,
                    mats['black'],STEERING,y=-.025,b=.003)
        geo.cube('Lever gland guard',(foot-.029,-.022,hinge_z+.027),(.010,.016,.026),
                 mats['plastic'],STEERING,.002)
    if spec.platform in ('g3','f3','g2'):
        loc = root.lerp(top,.86)
        geo.cube('Stowage hook clasp',(loc.x-.036,0,loc.z),
                 (.019,.025,.053),mats['black'],STEERING,.004)
    # Wide swept bars on F3/MAX; short, straight bar on the original ES.
    off = (.019 if spec.platform in ('g3','f3','g2') else .008)
    gz = spec.height-.018
    x = top.x-.019
    bar_x = x-.018 if spec.platform in ('g3','f3') else x
    half=spec.bar_width/2
    sweep=half*.48
    geo.curve('Handlebar bent tube',[(bar_x,-half*.92,gz),(x,-sweep,gz),
              (top.x,0,gz-.011),(x,sweep,gz),(bar_x,half*.92,gz)],
              .0105,stem_finish,STEERING)
    for side in (-1,1):
        grip_zone=.103 if spec.bar_width>.47 else .087
        near=side*(half-grip_zone)
        tip=side*(half-.004)
        geo.rod('Tapered fine-ribbed rubber grip',(bar_x,near,gz),(bar_x,tip,gz),
                .0163,mats['grip'],STEERING,40,r2=.0144)
        for j in range(9):
            gy=near+(tip-near)*(.11+.087*j)
            geo.rod('Grip finger recess ridge',(bar_x,gy-.0008,gz),(bar_x,gy+.0008,gz),
                    .0164-.00016*j,mats['grip'],STEERING,28)
        face=side*(half-.001)
        geo.rod('Bar end collar',(bar_x,tip,gz),(bar_x,face,gz),
                .0144,mats['black'],STEERING,36)
        if spec.indicators:
            geo.rod('Amber bar-end turn lamp',(bar_x,face,gz),(bar_x,side*half,gz),
                    .0121,mats['reflector'],STEERING,32)
        knob_y=near-side*.016
        geo.rod('Clamped handlebar switch module',(bar_x,knob_y-.010,gz),
                (bar_x,knob_y+.010,gz),.0175,mats['black'],STEERING,28)
        if spec.platform=='es' or side>0:
            geo.cube('Thumb paddle switch', (bar_x-.013,knob_y,gz-.013),
                     (.021,.019,.011), mats['accent'] if spec.platform=='es' and side>0
                     else mats['black'],STEERING,.004)
        else:
            geo.curve('Contoured brake hand lever',
                      [(bar_x+.018,knob_y,gz-.006),(bar_x+.039,near,gz-.009),
                       (bar_x+.035,tip*.95,gz-.010)],.0037,mats['cast'],STEERING)
            geo.rod('Brake lever pivot',(bar_x+.014,knob_y,gz-.014),
                    (bar_x+.014,knob_y,gz+.002),.0048,mats['steel'],STEERING,n=12)
    wide_screen=spec.platform in ('g3','f3')
    bw=.084 if wide_screen else .039 if spec.platform=='es' else .049
    geo.cube('Instrument pod',(top.x,0,gz-.01),(.064,bw,.036),
             mats['black'],STEERING,.012)
    geo.cube('Inset curved dashboard glass',(top.x-.006,0,gz+.008),
             (.038,bw*.78,.004),mats['glass'],STEERING,.002)
    for j in range(3):
        geo.cube('Dashboard graphic',(top.x-.013,j*.009-.009,gz+.0102),
                 (.012,.005,.0006),mats['screen'],STEERING,.00025)
    geo.rod('Rubber power control',(top.x+.021,0,gz+.008),
            (top.x+.021,0,gz+.012),.0058,mats['plastic'],STEERING,20)
    lens_x=top.x+.038
    if wide_screen:
        geo.cube('Under-console rounded headlamp shell',(lens_x-.021,0,gz-.061),
                 (.036,.035,.032),mats['black'],STEERING,.009)
        geo.cube('Integrated headlamp lens',(lens_x-.002,0,gz-.061),
                 (.004,.024,.021),mats['lens'],STEERING,.005)
    elif spec.platform=='es':
        geo.rod('Stem headlamp glass',(lens_x-.006,0,gz-.039),(lens_x,0,gz-.039),
                .0111,mats['lens'],STEERING,32)
    else:
        geo.cube('Headlight lens inset',(lens_x-.002,0,gz-.020),
                 (.003,.026,.011),mats['lens'],STEERING,.0025)
    if spec.platform != 'es':
        cable_material= mats['accent'] if spec.platform in ('f3','g3','f2','e2') else mats['black']
        mid=root.lerp(top,.65)
        high=root.lerp(top,.88)
        geo.curve('Brake and loom service loop',
                  [(bar_x+.022,-sweep*.94,gz-.015),(top.x+.075,-.035,gz-.091),
                   (high.x-.002,-.027,high.z-.046),(mid.x+.002,-.025,mid.z),
                   (root.x+.022,-.023,root.z+.045),
                   (root.x+.037,-.025,root.z-.011)],.0020,cable_material,STEERING)
    stem_mark=root.lerp(top,.43)
    if spec.platform in ('g30','g2','g3','f3','es'):
        geo.label('Small model trim marking', name,
                  (stem_mark.x,-(.0287 if spec.platform=='es' else .0235),stem_mark.z),
                  .011,mats['markings'],STEERING,angle=pi/2+.185)
    if spec.platform=='es':
        internal_a=root.lerp(top,.18)
        internal_b=root.lerp(top,.69)
        geo.rod('In-stem cell cartridge',internal_a,internal_b,.019,
                mats['black'],'BatteryMount',28)
        control_a=root.lerp(top,.76)
        control_b=root.lerp(top,.9)
        geo.rod('In-stem control module',control_a,control_b,.018,
                mats['cast'],'ControllerMount',24)
        if spec.exterior_pack:
            a=root.lerp(top,.23)+Vector((-.039,0,.006))
            b=root.lerp(top,.72)+Vector((-.039,0,.006))
            line_box('ES4 clip-on external battery shell',a,b,.045,.047,
                     mats['plastic'],'BatteryMount',bevel=.010)
            y=-.025
            geo.curve('ES4 signature battery case surround',
                      [(a.x,y,a.z+.012),(a.x-.012,y,a.z+.05),
                       (b.x-.012,y,b.z-.020),(b.x,y,b.z-.006)],
                      .0018,mats['accent'],'BatteryMount')
        return
    a,b,w=spec.deck_start,spec.deck_end,spec.deck_width
    dz=spec.deck_top-spec.shell_height*.55
    geo.cube('Sealed underdeck pack',(a+(b-a)*.365,0,dz),
             ((b-a)*.64,w*.78,spec.shell_height*.63),mats['black'],'BatteryMount',.005)
    geo.cube('Small front underdeck controller',(a+(b-a)*.83,0,dz),
             ((b-a)*.16,w*.68,spec.shell_height*.61),mats['cast'],'ControllerMount',.004)


def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def compact(groups):
    for group in groups.values():
        buckets={}
        for original in list(group.children):
            select([original])
            if original.type!='MESH':
                bpy.ops.object.convert(target='MESH')
            obj=bpy.context.view_layer.objects.active
            for modifier in list(obj.modifiers):
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            buckets.setdefault(obj.data.materials[0].name, []).append(obj)
        for material, objects in buckets.items():
            select(objects)
            if len(objects)>1:
                bpy.ops.object.join()
            obj=bpy.context.view_layer.objects.active
            obj.name=f'{group.name} | {material}'
            bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)


def stage(spec, reference, folder, key, render):
    ref = bpy.data.objects.new('REFERENCE exact product photo',None)
    bpy.context.collection.objects.link(ref)
    ref.empty_display_type='IMAGE'
    ref.data=bpy.data.images.load(str(reference))
    ref.data.pack()
    ref.hide_render=True
    ref.hide_viewport=True

    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('Render studio')
    scene.world.color=(.38,.38,.38)
    scene.unit_settings.system='METRIC'
    scene.render.engine='CYCLES'
    scene.render.threads_mode='FIXED'
    scene.render.threads=3
    scene.render.resolution_x=480
    scene.render.resolution_y=480
    scene.render.resolution_percentage=100
    scene.cycles.samples=8
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.image_settings.file_format='PNG'
    floor=material('Studio floor','ececeb',.0,.78)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004))
    bpy.context.object.name='Studio floor'
    bpy.context.object.data.materials.append(floor)
    for spot,power,size in [((1,-2.4,3.6),490,2.7),((-2.5,-.4,1.5),160,2.1),
                            ((.3,2.6,3),480,2.5)]:
        bpy.ops.object.light_add(type='AREA',location=spot)
        light=bpy.context.object
        light.name='Studio area light'
        light.data.energy=power
        light.data.shape='DISK'
        light.data.size=size
        light.rotation_euler=(Vector((0,0,.55))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add()
    camera=bpy.context.object
    camera.name='Catalog camera'
    camera.data.type='ORTHO'
    camera.data.ortho_scale=max(spec.height+.11,spec.length+.19)
    scene.camera=camera

    for angle,position in [('side',(0,-4.2,.87)), ('three-quarter',(2.55,-4.75,1.5))]:
        camera.location=position
        camera.rotation_euler=(Vector((0,0,spec.height*.49))-camera.location).to_track_quat('-Z','Y').to_euler()
        if render:
            scene.render.filepath=str(folder/f'{key}-{angle}.png')
            bpy.ops.render.render(write_still=True)


def rebuild(entry, spec, folder, render):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats=materials(spec)
    if spec.accent_ring:
        mats['pinstripe']=material('Colored wheel pinstripe',spec.accent,.0,.70,.08)
    if entry['name'].endswith('G30LP'):
        mats['stem']=material('Model body finish','292c2e',.24,.53)
        mats['fender']=material('Light compact fender polymer','a2a7a9',.0,.68)
    root=bpy.data.objects.new(entry['name'],None)
    bpy.context.collection.objects.link(root)
    old=entry['model']
    root['canonicalKey']=old['key']
    root['frontAxis']='+X'
    root['source']=entry['source']
    root['reference']=entry['image']
    root['accuracy']='Exterior reconstructed from the named photograph; hidden components are visual envelopes.'
    groups={}
    for name in MOUNTS:
        obj=bpy.data.objects.new(name,None)
        bpy.context.collection.objects.link(obj)
        obj.parent=root
        groups[name]=obj
    geo.groups=groups
    geo.parts=[]
    geo.black=mats['black']
    geo.silver=mats['steel']
    geo.steel=mats['steel']
    name=entry['name'].removeprefix('Segway Ninebot ')
    rear_spec=replace(spec,radius=.0953) if spec.platform=='es' else spec
    front=(spec.length-spec.radius-rear_spec.radius)/2
    rear=-front
    foot=front- (.080 if spec.platform in ('g3','f3') else .071)
    hinge_z=spec.deck_top+(.170 if spec.platform in ('g3','f3') else .146 if spec.platform!='es' else .135)

    chassis(spec,foot,mats)
    wheel(front,spec,mats,True)
    wheel(rear,rear_spec,mats,False)
    fork(spec,front,foot,hinge_z,mats)
    rear_axle(rear_spec,rear,mats)
    mudguard(front,spec,mats,True)
    mudguard(rear,rear_spec,mats,False)
    cockpit(spec,name,foot,hinge_z,mats)

    compact(groups)
    objects=[obj for group in groups.values() for obj in group.children]
    triangles=0
    for obj in objects:
        obj.data.calc_loop_triangles()
        triangles+=len(obj.data.loop_triangles)
    select([root,*groups.values(),*objects])
    export=ROOT/'apps/web/public'/ old['url'].lstrip('/')
    export.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,
                             export_yup=True,export_extras=True,export_cameras=False,
                             export_lights=False)
    key=old['key']
    native=ROOT/old['nativeSource']
    reference=ROOT/'apps/web/public'/entry['image'].lstrip('/')
    stage(spec,reference,folder,key,render)
    bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
    model={**old,'family':PLATFORMS[spec.platform],'triangles':triangles,
           'meshes':len(objects),'bytes':export.stat().st_size}
    assert model['bytes']<5_000_000 and triangles<120000 and len(objects)<65,model
    note={
        'name':entry['name'],'model':model,
        'variantNote':appearance_note(name,spec)
    }
    (folder/f'{key}.json').write_text(json.dumps(note,indent=2)+'\n')
    print(f'NINEBOT COMPLETE {key}: {triangles} triangles, {len(objects)} meshes',flush=True)
    return note


def main():
    arguments = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser=argparse.ArgumentParser()
    parser.add_argument('models',nargs='*',help='Exact catalog variants, omitting Segway Ninebot')
    parser.add_argument('--output',type=Path,default=Path('/tmp/voltforge-ninebot'))
    parser.add_argument('--no-render',action='store_true')
    args=parser.parse_args(arguments)
    args.output.mkdir(parents=True,exist_ok=True)
    requested=args.models or list(MODELS)
    entries=json.loads((ROOT/'apps/web/src/data/vehicle-expansion-commuter.json').read_text())['entries']
    named={e['name']:e for e in entries}
    results=[rebuild(named[f'Segway Ninebot {name}'],MODELS[name],args.output,not args.no_render)
             for name in requested]
    (args.output/'metadata.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    main()
