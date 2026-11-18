"""Rebuild the Joyor catalog in Blender.

blender -b -t 3 --python scripts/blender/remodel/joyor/build.py -- --render s5-z
Use no keys to export every model. Visual approximations in metres, not supplier CAD.
"""

import argparse
import json
import math
import struct
import sys
from math import cos, pi, sin
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
from geometry import Assembly, color
from models import MODELS

GROUPS = ("Chassis", "Steering", "FrontWheel", "RearWheel", "Fork", "RearSuspension",
          "BatteryMount", "ControllerMount", "MotorMount")
ARTWORK = Path("assets/vehicles/expansion/commuter")
MODEL_URL = Path("models/expansion/commuter")
NATIVE = Path("assets/blender/expansion/commuter")
PUBLIC = ROOT / "apps/web/public"


class Joyor:
    def __init__(self, key, spec, ref):
        self.key, self.spec = key, spec
        self.a = Assembly(
            ref["name"], GROUPS,
            {"canonicalKey": "joyor-" + key, "frontAxis": "+X", "source": ref["source"],
             "reference": ref["image"], "accuracy": "Photo-guided approximation, including inferred internal mounts"},
        )
        self.r = spec.tire_radius
        self.w = spec.tire_width / 2
        self.front = spec.wheelbase / 2
        self.rear = -self.front
        self.front_deck = spec.deck_length * 0.5 - 0.004
        self.rear_deck = self.front_deck - spec.deck_length
        self.mast_x = self.front - (0.035 if spec.swingarm in ("telescopic", "commuter", "shortcoil") else 0.058)
        coat = color("Model powder coat", spec.body, 0.27, 0.43)
        self.mat = {
            "coat": coat, "trim": color("Extruded deck edge", spec.trim, 0.38, 0.42),
            "tread": color("Tire rubber", "1f1f22", 0, 0.9),
            "sipe": color("Tire tread rubber", "252529", 0, 0.88),
            "grip": color("Textured grip rubber", "303235", 0, 0.85),
            "mat": color("Deck traction rubber", "303133", 0, 0.86),
            "plastic": color("Molded fender polymer", "313437", 0, 0.64),
            "black": color("Black", "1f2225", 0.18, 0.54),
            "fastener": color("Brushed fastener", "969ca2", 0.73, 0.38),
            "rotor": color("Rotor", "a3a7aa", 0.73, 0.35),
            "rim": color("Dark anodized aluminium", "4b4e54", 0.52, 0.43),
            "arm": color("Orange" if spec.arm_color[:2] in ("d6", "ec", "ef", "d5") else "Grey",
                         spec.arm_color, 0.26, 0.38),
            "arm_shadow": color("Cast arm inset", "733820" if spec.arm_color[0] in "ed" else "45484d", 0.23, 0.54),
            "silver": color("Anodized fork slider", "959da3", 0.68, 0.26),
            "red": color("Tinted red optical lens", "941a1b", 0.14, 0.27),
            "stripe": color("C10 turquoise side molding", "289a9b", 0.17, 0.48),
            "amber": color("Honeycomb amber reflector", "d57926", 0.26, 0.39),
            "screen": color("Dark display glass", "172831", 0.28, 0.23),
            "lens": color("Optical diffuser", "d0d4d6", 0.36, 0.23),
            "white": color("Printed Joyor marking", "bec2c6", 0.17, 0.49),
            "hose": color("Brake and display hose", spec.cable_color, 0.03, 0.65),
        }

    def box(self, center, size, material, group="Chassis", radius=0.003):
        self.a.box(center, size, self.mat[material], group, radius)

    def rod(self, a, b, radius, material, group, steps=24, radius_end=None):
        self.a.rod(a, b, radius, self.mat[material], group, steps, radius_end)

    def profile(self, contour, y, width, material, group):
        self.a.profile(contour, y, width, self.mat[material], group)

    def fastener(self, x, y, z, side, size, group, cap="fastener"):
        along = y + side * 0.005
        self.rod((x, y, z), (x, along, z), size, cap, group, 16)
        self.rod((x, along, z), (x, along + side * 0.0008, z), size * 0.49, "black", group, 6)

    def text(self, text, point, size, group, angle=0):
        self.a.text(text, point, size, self.mat["white"], group, angle)

    def deck(self):
        s, a = self.spec, self.a
        xf, xr, z, w = self.front_deck, self.rear_deck, s.deck_top, s.deck_width / 2
        depth = s.deck_depth
        shaped = s.foot_rest == "molded"
        stations = [
            (xr - 0.023, w * 0.79, z - depth + 0.028, z + (0.039 if shaped else 0.003)),
            (xr + 0.022, w, z - depth + 0.004, z + (0.028 if shaped else 0)),
            (xr + 0.100, w, z - depth, z),
            (xf - 0.074, w, z - depth, z),
            (xf - 0.020, w * 0.96, z - depth + 0.004, z + (0.028 if shaped else 0)),
            (xf + 0.014, w * 0.79, z - depth + 0.023, z + (0.062 if shaped else -0.006)),
        ]
        a.deck(stations, self.mat["coat"], "Chassis", 0.010)
        mid_x = (xr + xf) / 2
        a.deck([(x, ww * 0.961, top - 0.0005, top + 0.004) for x, ww, _, top in stations[1:-1]],
               self.mat["mat"], "Chassis", 0.002)
        for side in (-1, 1):
            self.box((mid_x, side * (w + 0.0004), z - 0.047),
                     (s.deck_length * 0.83, 0.005, 0.011), "stripe" if shaped else "trim", radius=0.002)
            if s.lamps in ("signals", "corner", "turquoise"):
                for end, center in ((-1, xr + 0.042), (1, xf - 0.040)):
                    lens = "stripe" if shaped else "red"
                    contour = [(center - 0.023, z - 0.016), (center + 0.026, z - 0.020),
                               (center + end * 0.016, z - 0.052), (center - 0.019, z - 0.045)]
                    self.profile(contour, side * (w + 0.001), 0.003, lens, "Chassis")
            if s.reflectors and not shaped:
                self.box((xr + 0.22, side * (w + 0.004), z - 0.022), (0.041, 0.003, 0.016), "amber")
            for x in (xr + 0.071, xf - 0.071):
                self.fastener(x, side * w, z - 0.049, side, 0.0044, "Chassis", "black")
        for i in range(16):
            x = xr + 0.104 + i * (s.deck_length - 0.192) / 16
            for side in (-1, 1):
                a.tube([(x - 0.012, side * w * 0.11, z + 0.0047),
                        (x + 0.006, side * w * 0.52, z + 0.0047),
                        (x + 0.002, side * w * 0.82, z + 0.0047)],
                       0.00105, self.mat["plastic"], "Chassis")
        if s.foot_rest in ("hook", "wedge"):
            end = xr - (0.092 if s.foot_rest == "hook" else 0.077)
            contour = [(xr + 0.025, z + 0.004), (xr - 0.015, z + 0.024),
                       (end, z + 0.086), (end - 0.014, z + 0.081),
                       (xr - 0.014, z + 0.002)]
            self.profile(contour, 0, w * 1.48, "coat", "Chassis")
            for i in range(4):
                t = 0.2 + i * 0.16
                x = (1 - t) * (xr + 0.015) + t * end
                h = z + 0.008 + 0.078 * t
                self.rod((x, -w * .67, h), (x, w * .67, h), .0027, "mat", "Chassis", 12)
        if s.foot_rest == "arch" and self.key != "y10":
            # Compact Y6/Y8 molded bridge wraps into the wheel's forward quarter.
            xx = self.rear
            contour = [(xr + .028, z - .015), (xr + .028, z + .007),
                       (xx + self.r * .70, self.r * 1.77),
                       (xx + self.r * .33, self.r * 2.08),
                       (xx + self.r * .24, self.r * 2.04),
                       (xx + self.r * .55, self.r * 1.72), (xr - .016, z - .012)]
            self.profile(contour, 0, w * 1.56, "plastic", "Chassis")
        # Service geometry stays independently switchable inside the original enclosure.
        self.box((mid_x - .032, 0, z - depth * .49), (s.deck_length * .68, w * 1.68, depth * .68),
                 "black", "BatteryMount", 0.008)
        for y in (-w * .62, w * .62):
            self.box((mid_x - .032, y, z - depth * .18), (s.deck_length * .59, .008, .004),
                     "trim", "BatteryMount")
        self.box((xf - .071, 0, z - depth * .48), (.080, w * 1.53, depth * .55),
                 "silver", "ControllerMount")
        for i in range(7):
            y = (i - 3) * w * .20
            self.box((xf - .071, y, z - depth * .19), (.076, .004, .005), "fastener", "ControllerMount")
        # Side-charging cap and centre stand with a retracted spring.
        self.rod((xf - .095, -w, z - .039), (xf - .095, -w - .007, z - .039),
                 .008, "black", "Chassis", 24)
        if shaped:
            self.box((xr + .14, w * .85, z + .004), (.016, .018, .009), "black")
            # A visible recessed seam and latch identify the removable top cassette.
            for side in (-1, 1):
                self.rod((xr + .108, side * w * .87, z + .004), (xf - .092, side * w * .87, z + .004),
                         .0015, "black", "Chassis", 10)
            self.box((xf - .102, 0, z + .006), (.023, .046, .005), "plastic")
        x = xr + s.deck_length * .32
        self.a.cable([(x, -w * .87, z - depth + .01), (x - .019, -w * 1.25, .070),
                      (x - .022, -w * 1.37, .012)], .0052, self.mat["black"], "Chassis")
        self.box((x - .023, -w * 1.37, .010), (.024, .022, .010), "plastic")

    def tire(self, x, group):
        r, w, spec = self.r, self.w, self.spec
        a = self.a
        cross = [(-w * .72, r * .69), (-w * .91, r * .78), (-w, r * .87),
                 (-w * .94, r * .94), (-w * .71, r * .979), (-w * .34, r * .995),
                 (0, r), (w * .34, r * .995), (w * .71, r * .979), (w * .94, r * .94),
                 (w, r * .87), (w * .91, r * .78), (w * .72, r * .69)]
        a.hub(x, r, cross, self.mat["tread"], group, steps=84, closed=True)
        for side in (-1, 1):
            a.hub(x, r, [(side * w * .945, r * .810), (side * w * .967, r * .816),
                         (side * w * .966, r * .825)], self.mat["sipe"], group, steps=64, closed=True)
        if spec.tires in ("allterrain", "block"):
            rows = (-.78, -.40, 0, .40, .78)
            count = 36 if spec.tires == "block" else 40
            depth = .0037 if spec.tires == "block" else .0028
        else:
            rows, count, depth = (-.55, .55), 42, .0011
        for row, y_scale in enumerate(rows):
            y = y_scale * w
            maximum = r * (1 - .047 * abs(y_scale) ** 2)
            half_span = .011 if len(rows) > 2 else .007
            for n in range(count):
                angle = (n + (row % 2) * .48) * 2 * pi / count
                span = 2 * pi / count * (.29 if len(rows) > 2 else .24)
                sections = []
                for radius, bevel in ((maximum - .003, 1), (maximum + depth, .74)):
                    corners = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
                    sections.append([
                        (x + radius * cos(angle + bevel * (v * span + u * .016)),
                         y + u * half_span * bevel,
                         r + radius * sin(angle + bevel * (v * span + u * .016)))
                        for v, u in corners
                    ])
                a.loft(sections, self.mat["sipe"], group)

    def hub_wheels(self):
        a, r, w, spec = self.a, self.r, self.w, self.spec
        for x, group in ((self.front, "FrontWheel"), (self.rear, "RearWheel")):
            front = x > 0
            hub_group = "MotorMount" if not front or spec.motor_count == 2 else group
            self.tire(x, group)
            a.hub(x, r, [(-w * .80, r * .70), (-w * .70, r * .725), (w * .70, r * .725),
                         (w * .80, r * .70), (w * .79, r * .61), (-w * .79, r * .61)],
                  self.mat["rim"], group, closed=True)
            hub_radius = r * (.58 if hub_group == "MotorMount" else .29)
            a.hub(x, r, [(-w * .8, hub_radius * .89), (-w * .74, hub_radius),
                         (w * .74, hub_radius), (w * .83, hub_radius * .90)],
                  self.mat["black"], hub_group)
            for side in (-1, 1):
                y = side * w * .835
                a.hub(x, r, [(y, hub_radius * .83), (y + side * .004, hub_radius * .77),
                             (y + side * .006, hub_radius * .51)], self.mat["rim"], hub_group)
                for i in range(6):
                    t = i * pi / 3
                    if hub_group == group:
                        # Cast taper between the hub and separate wheel rim.
                        edge = r * .638
                        p0, p1 = r * .26, edge
                        points = [(x + v * cos(t + offset), r + v * sin(t + offset))
                                  for v, offset in ((p0, -.21), (p1, -.065), (p1, .085), (p0, .26))]
                        self.profile(points, side * w * .55, .011, "rim", group)
                    else:
                        self.fastener(x + hub_radius * .69 * cos(t), y + side * .005,
                                      r + hub_radius * .69 * sin(t), side, .0025, hub_group)
                self.fastener(x, side * (w + .014), r, side, .0094, hub_group)
            if self.key != "f5":
                side = -1 if front else 1
                y = side * (w + .0048)
                rotor_radius = min(.071, r * .57)
                a.hub(x, r, [(y - .0014, rotor_radius * .76), (y - .0014, rotor_radius),
                             (y + .0014, rotor_radius), (y + .0014, rotor_radius * .76)],
                      self.mat["rotor"], group, closed=True)
                for j in range(6):
                    theta = j * pi / 3
                    contour = [(x + v * cos(theta + angle), r + v * sin(theta + angle))
                               for v, angle in ((r * .20, -.21), (rotor_radius * .82, .01),
                                                (rotor_radius * .82, .15), (r * .20, .39))]
                    self.profile(contour, y, .0028, "rotor", group)
                self.box((x + (-1 if front else 1) * rotor_radius * .8, y + side * .007,
                          r + rotor_radius * .77), (.035, .027, .027), "black", group, .006)

    def rocker(self, axle, pivot, group, side):
        spec, r, w = self.spec, self.r, self.w
        a = Vector((pivot, r + (.055 if axle > 0 else .045)))
        b = Vector((axle, r))
        d = b - a
        n = Vector((-d.y, d.x)).normalized()
        if n.y < 0:
            n = -n
        y = side * (w + .0175)
        width = .021 if spec.swingarm == "silver" else .0185
        outline = [a - d * .13 + n * .014, a + n * .029, a + d * .44 + n * .020,
                   b + d * .10 + n * .014, b + d * .13 - n * .011, b - n * .023,
                   a + d * .39 - n * .029, a - d * .11 - n * .016]
        if spec.swingarm in ("windowed", "vented"):
            hole = [a + d * .18 + n * .006, a + d * .26 + n * .011, a + d * .49 + n * .009,
                    b - d * .23 + n * .008, b - d * .17 - n * .003, b - d * .22 - n * .008,
                    a + d * .47 - n * .010, a + d * .20 - n * .009]
            self.a.pierced(outline, hole, y, width, self.mat["arm"], group)
            for t in (.30, .575):
                p = a + d * t
                self.profile([p - n * .017, p + n * .017, p + d * .040 + n * .017,
                              p + d * .038 - n * .016], y, width, "arm", group)
        else:
            self.profile(outline, y, width, "arm", group)
            if spec.swingarm != "silver":
                p, q = a + d * .21, b - d * .13
                self.profile([p + n * .012, q + n * .010, q - n * .010, p - n * .012],
                             y + side * width * .53, .0028, "arm_shadow", group)
                for t in (.27, .44, .61, .77):
                    p = a + d * t
                    self.profile([p - n * .013, p + n * .012 + d * .045,
                                  p + n * .012 + d * .085, p - n * .013 + d * .040],
                                 y + side * width * .58, .0036, "arm", group)
            elif side == -1:
                p = a.lerp(b, .51)
                self.text("JOYOR", (p.x, y - width * .54, p.y), .012, group)
        self.fastener(a.x, y + side * width * .55, a.y, side, .013, group, "black")
        self.fastener(b.x, y + side * width * .55, b.y, side, .009, group)

    def suspension(self):
        s, r, w = self.spec, self.r, self.w
        classic = s.swingarm in ("telescopic", "commuter", "shortcoil")
        if classic:
            crown = self.mast_x, s.mast_base - .068
            for side in (-1, 1):
                y = side * (w + .010)
                x = self.front
                if s.swingarm == "shortcoil":
                    # Narrow 8-inch F5 fork, with an orange spring above the front crown.
                    self.rod((x, y, r), (crown[0] + .007, y, crown[1]), .011, "black", "Fork")
                else:
                    self.rod((x, y, r), (crown[0], y, crown[1] - .034), .014, "black", "Fork")
                    self.rod((x - .003, y, r + .074), (crown[0], y, crown[1]), .0094, "silver", "Fork")
                    if self.key == "y10":
                        coil_a = Vector((x - .012, y, r + .060))
                        coil_b = Vector((crown[0] + .004, y, crown[1] - .006))
                        axis = (coil_b - coil_a).normalized()
                        u = Vector((0, 1, 0))
                        v = axis.cross(u)
                        coil = [
                            coil_a.lerp(coil_b, i / 92)
                            + .012 * (u * cos(i * 12 * pi / 92) + v * sin(i * 12 * pi / 92))
                            for i in range(93)
                        ]
                        self.a.tube(coil, .0026, self.mat["black"], "Fork")
                    if s.lamps in ("abe", "turquoise"):
                        self.box((x + .008, y + side * .014, r + .043),
                                 (.017, .003, .042), "amber", "Fork")
                xx = self.rear + (s.rear_pivot if s.swingarm != "shortcoil" else .098)
                if s.swingarm == "shortcoil":
                    zz = s.deck_top - .038
                    self.profile([(xx, zz + .030), (self.rear - .018, r + .003),
                                  (self.rear - .014, r - .019), (xx + .023, zz - .004)],
                                 y, .013, "black", "RearSuspension")
                else:
                    zz = s.deck_top - .032
                    self.profile([(xx + .013, zz + .030), (xx - .021, zz + .044),
                                  (self.rear - .022, r + .021), (self.rear - .021, r - .017),
                                  (self.rear + .033, r - .024), (xx + .025, zz - .007)],
                                 y, .018, "arm", "RearSuspension")
                    self.fastener(self.rear, y + side * .012, r, side, .008, "RearSuspension")
            self.rod((crown[0], -w - .019, crown[1]), (crown[0], w + .019, crown[1]),
                     .016, "black", "Fork", 20)
            if s.swingarm == "shortcoil":
                center = Vector((self.front - .027, 0, .184))
                coil = [center + Vector((.021 * sin(i * pi / 9), .021 * cos(i * pi / 9), .039 * i / 65))
                        for i in range(66)]
                self.a.tube(coil, .0036, self.mat["arm"], "Fork")
        else:
            fx = self.front - s.front_pivot
            for side in (-1, 1):
                self.rocker(self.front, fx, "Fork", side)
                self.rocker(self.rear, self.rear + s.rear_pivot, "RearSuspension", side)
                y = side * (w + .016)
                self.profile([(fx - .022, r + .043), (fx - .026, r + .087),
                              (self.mast_x - .009, s.mast_base - .025),
                              (self.mast_x + .019, s.mast_base - .032), (fx + .023, r + .049)],
                             y, .018, "black", "Fork")
            self.rod((fx, -w - .018, r + .054), (fx, w + .018, r + .054),
                     .025, "black", "Fork", 38)
            if s.swingarm == "silver":
                for group, end, pivot in (
                    ("Fork", self.front, fx), ("RearSuspension", self.rear, self.rear + s.rear_pivot)
                ):
                    for side in (-1, 1):
                        y = side * (w + .001)
                        a = Vector((pivot, y, s.deck_top + .012))
                        b = Vector((end + (pivot - end) * .35, y, r + .027))
                        self.rod(a, a.lerp(b, .64), .011, "black", group)
                        self.rod(a.lerp(b, .57), b, .006, "silver", group)

    def guards(self):
        r, w, s = self.r, self.w, self.spec
        for front, x in ((True, self.front), (False, self.rear)):
            # Beaded moulded fenders follow the tire, with a drop at the tail.
            if front:
                start, end = (.15 * pi, .94 * pi)
            else:
                start, end = (.08 * pi, (1.02 if s.guard in ("molded", "full") else .92) * pi)
            width = w * (1.12 if front else 1.31)
            if s.guard == "compact":
                width *= .96
            shell = []
            for i in range(37):
                t = i / 36
                angle = start + (end - start) * t
                radius = r + (.012 if front else .014) + (.005 if s.guard == "lip" else .003) * sin(pi * t)
                half_w = width * (.94 + .06 * sin(pi * t))
                top = [(radius - .006 * abs(j / 4) ** 2, half_w * j / 4) for j in range(-4, 5)]
                bottom = [(rr - .0035, y) for rr, y in reversed(top)]
                shell.append([(x + rr * cos(angle), y, r + rr * sin(angle))
                              for rr, y in [*top, *bottom]])
            self.a.loft(shell, self.mat["plastic"], "Chassis", True)
            if not front:
                tail_x, tail_z = x - r * .93, r * 1.56
                lens = [(tail_x + .017, tail_z + .029), (tail_x + .007, tail_z + .034),
                        (tail_x - .014, tail_z + .008), (tail_x - .016, tail_z - .011),
                        (tail_x - .005, tail_z - .012)]
                self.profile(lens, 0, width * (1.42 if s.guard != "full" else .97), "red", "Chassis")
                for side in (-1, 1):
                    y = side * width * .88
                    self.rod((x - r * .72, y, r * 1.76), (x + .013, y * .91, r + .017),
                             .0052, "black", "Chassis", 16)

    def steering(self):
        s, a, group = self.spec, self.a, "Steering"
        z, x = s.mast_base, self.mast_x
        end_x, end_z = x - s.rake, s.height - .022
        anchor = self.front_deck - .01
        seat_z = s.deck_top + .010
        outer = [(anchor - .06, seat_z - .025), (anchor - .062, seat_z + .009),
                 (x - .029, z + .055), (x + .027, z + .031),
                 (x + .024, z - .035), (anchor + .065, seat_z - .038)]
        inside = [(anchor - .009, seat_z -.001), (anchor - .005, seat_z + .015),
                  (x - .026, z + .008), (x + .001, z - .005),
                  (x - .008, z - .024), (anchor + .029, seat_z - .012)]
        for side in (-1, 1):
            y = side * (.032 if s.hinge in ("lattice", "truss") else .0255)
            if s.hinge == "covered":
                self.profile(outer, y, .021, "coat", "Chassis")
                insert = [(anchor - .015, seat_z + .013), (x - .018, z + .038),
                          (x - .001, z + .027), (anchor + .014, seat_z + .001)]
                self.profile(insert, y + side * .013, .004, "trim", "Chassis")
            elif s.hinge == "lean":
                swept = [(anchor - .052, seat_z - .04), (anchor - .030, seat_z + .012),
                         (x - .078, z + .018), (x - .031, z + .054), (x + .024, z + .058),
                         (x + .030, z - .003), (x - .030, z - .021), (anchor + .04, seat_z - .037)]
                self.profile(swept, y, .042, "coat", "Chassis")
            else:
                a.pierced(outer, inside, y, .016, self.mat["coat"], "Chassis")
            self.fastener(anchor - .022, y + side * .011, seat_z + .005, side, .008, "Chassis")
            self.fastener(x - .017, y + side * .011, z + .024, side, .006, "Chassis", "black")
        lock = "black" if s.hinge != "lean" else "trim"
        self.rod((x - .006, -.040, z + .017), (x - .006, .040, z + .017),
                 .020, lock, "Chassis", 28)
        a.cable([(anchor + .002, -.041, seat_z + .018), (anchor - .034, -.041, seat_z + .051),
                 (x - .067, -.032, z + .046), (x - .037, -.024, z + .049)],
                .0048, self.mat["black"], "Chassis")
        if self.key.startswith("t") or s.hinge == "covered":
            self.box((x - .041, -.025, z + .002), (.027, .012, .026), "red", "Chassis")
        a.shaft((x, 0, z - .028), (end_x, 0, end_z),
                [(0, .022, .022), (.04, .027, .026), (.72, .021, .023),
                 (.75, .030, .028), (.776, .027, .026), (.78, .015, .016),
                 (.99, .0145, .0155), (1, .014, .015)],
                self.mat["coat"], group, 24 if s.hinge == "lean" else 16)
        clamp_x = x + (end_x - x) * .753
        clamp_z = z + (end_z - z) * .753
        self.box((clamp_x - .001, -.026, clamp_z), (.046, .015, .019), "black", group)
        self.rod((clamp_x + .02, -.028, clamp_z), (clamp_x + .043, -.035, clamp_z + .015),
                 .0075, "black", group, 14)
        angle = pi / 2 + math.atan2(s.rake, end_z - z)
        self.text("JOYOR", (x - s.rake * .42, -.026, z + (end_z - z) * .42), .024, group, angle)
        if self.key == "t12-ultra":
            self.text("T12 ULTRA", (x - s.rake * .29, -.027, z + (end_z - z) * .29), .011, group, angle)
        light_z = z + (.140 if self.key.startswith("t") else .044)
        light_x = x + .044 - s.rake * .1
        if s.lamps == "low":
            light_z, light_x = z + .015, x + .031
        self.box((light_x - .014, 0, light_z - .017), (.060, .026, .021), "black", group)
        if s.lamps == "turquoise":
            self.box((light_x, 0, light_z), (.048, .055, .031), "black", group, .008)
            self.box((light_x + .024, 0, light_z + .002), (.003, .044, .019), "lens", group)
        else:
            self.rod((light_x - .024, 0, light_z), (light_x + .021, 0, light_z),
                     .022 if s.lamps != "low" else .016, "black", group, 30)
            self.rod((light_x + .021, 0, light_z), (light_x + .024, 0, light_z),
                     .017 if s.lamps != "low" else .012, "lens", group, 30)
        self.cockpit(end_x, end_z)
        for side in (-1, 1):
            control_y = side * s.bars * .22
            a.cable([(end_x + .022, control_y, end_z - .014), (end_x + .069, side * .064, end_z - .081),
                     (end_x + .044, side * .041, end_z - .188), (clamp_x + .018, side * .024, clamp_z),
                     (x + .022, side * .015, z + .037), (anchor + .021, side * .066, seat_z + .017)],
                    .0028, self.mat["hose" if side < 0 else "black"], group)

    def cockpit(self, x, z):
        a, s, group = self.a, self.spec, "Steering"
        end = s.bars / 2
        a.cable([(x - .026, -end, z + .006), (x - .019, -end * .48, z + .010),
                 (x, -.038, z), (x, .038, z), (x - .019, end * .48, z + .010),
                 (x - .026, end, z + .006)], .011, self.mat["black"], group)
        for side in (-1, 1):
            inner = end - .113
            out = side * end
            a.shaft((x - .024, side * inner, z + .010), (x - .029, out, z + .007),
                    [(0, .016, .017), (.08, .0170, .018), (.48, .0178, .019),
                     (.93, .0168, .0175), (1, .015, .015)], self.mat["grip"], group, 32)
            for j in range(15):
                y = side * (inner + .009 + j * .0064)
                self.rod((x - .025, y, z + .011), (x - .025, y + side * .0014, z + .011),
                         .018 if j < 12 else .017, "grip", group, 32)
            terminal = "amber" if s.lamps == "bar" else "black"
            self.rod((x - .029, out, z + .007), (x - .029, out + side * .004, z + .007),
                     .0145, terminal, group, 28)
            if self.key == "f5" and side == 1:
                continue
            y = side * (inner - .023)
            self.box((x + .008, y, z + .013), (.032, .026, .032), "black", group, .005)
            a.cable([(x + .022, y, z + .013), (x + .070, side * (inner + .026), z + .006),
                     (x + .063, side * (end - .028), z + .002)],
                    .0049, self.mat["black"], group)
            self.rod((x + .025, y, z + .024), (x + .025, y, z + .029),
                     .0045, "fastener", group, 14)
        ydisp = .095 if s.display == "side" else 0
        size = (.058, .051) if s.display == "side" else (.065, .082)
        self.box((x + .006, ydisp, z + .023), (size[0], size[1], .027), "black", group, .007)
        self.box((x + .008, ydisp, z + .037), (size[0] * .85, size[1] * .87, .003), "screen", group, .004)
        self.box((x -.016, -.084, z + .011), (.026, .032, .020), "plastic", group, .004)
        for i in range(3):
            self.box((x -.018, -.094 + i * .010, z + .022), (.012, .006, .004), "black", group)
        self.rod((x -.008, .101, z - .009), (x -.030, .110, z - .028),
                 .007, "black", group, 18)
        self.box((x - .035, .111, z - .027), (.015, .024, .008), "mat", group)

    def build(self):
        self.deck()
        self.hub_wheels()
        self.suspension()
        self.guards()
        self.steering()
        self.a.finalize()
        return self.a


def add_studio(max_height):
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.world = bpy.data.worlds.new("Studio ambient")
    scene.world.color = (0.27, 0.27, 0.27)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.006))
    plane = bpy.context.object
    plane.name = "Studio floor"
    plane.data.materials.append(color("Studio porcelain", "e7e8eb", 0, 0.84))
    target = Vector((0, 0, max_height * .48))
    for n, (location, energy, size) in enumerate((
        ((1.9, -2.8, 3.8), 590, 3.1), ((-1.7, 2.4, 2.7), 510, 2.2),
        ((-2.3, -0.7, 2.2), 180, 2.0),
    )):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"Studio panel {n + 1}"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.camera_add(location=(2.4, -4.8, 1.68))
    camera = bpy.context.object
    camera.name = "Studio camera"
    camera.data.type, camera.data.ortho_scale = "ORTHO", max(1.55, max_height + .28)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x = scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 8
    scene.cycles.use_denoising = True
    scene.render.threads_mode, scene.render.threads = "FIXED", 3
    scene.view_settings.view_transform = "AgX"
    return scene, camera, target


def glb_stats(path):
    with path.open("rb") as f:
        header = f.read(20)
        length, chunk_type = struct.unpack("<I4s", header[12:])
        assert header[:4] == b"glTF" and chunk_type == b"JSON"
        data = json.loads(f.read(length))
    triangles = sum(
        data["accessors"][p["indices"]]["count"] // 3
        for mesh in data["meshes"] for p in mesh["primitives"]
    )
    return len(data["meshes"]), triangles


def export(key, spec, ref, render_dir=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    asset_key = "joyor-" + key
    output = PUBLIC / MODEL_URL / (asset_key + ".glb")
    source = ROOT / NATIVE / (asset_key + ".blend")
    static_objects = Joyor(key, spec, ref).build()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in static_objects.objects():
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(output), export_format="GLB", use_selection=True, export_yup=True,
        export_extras=True, export_cameras=False, export_lights=False,
    )
    scene, camera, target = add_studio(spec.height)
    texture = bpy.data.images.load(str(PUBLIC / ref["image"].lstrip("/")))
    texture.pack()
    marker = bpy.data.objects.new("Manufacturer photo • hidden during studio rendering", None)
    bpy.context.collection.objects.link(marker)
    marker.empty_display_type, marker.data = "IMAGE", texture
    marker.hide_viewport, marker.hide_render = True, True
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(source), compress=True)
    if render_dir:
        render_dir.mkdir(exist_ok=True, parents=True)
        for label, location in (("three-quarter", (2.4, -4.8, 1.68)),
                                ("profile", (0, -6, target.z + .02))):
            camera.location = location
            camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
            scene.render.filepath = str(render_dir / f"{asset_key}-{label}.png")
            bpy.ops.render.render(write_still=True)
    mesh_count, triangle_count = glb_stats(output)
    entry = {**ref, "model": {"key": asset_key, "url": "/" + str(output.relative_to(PUBLIC)),
                              "nativeSource": str(source.relative_to(ROOT)), "meshes": mesh_count,
                              "triangles": triangle_count, "bytes": output.stat().st_size,
                              "family": spec.family}}
    print(f"JOYOR_EXPORT {asset_key}: {mesh_count} meshes, {triangle_count} triangles", flush=True)
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", metavar="model-key", nargs="*", choices=None)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--evidence", type=Path, default=Path("/tmp/voltforge-joyor-renders"))
    parser.add_argument("--metadata", type=Path, default=Path("/tmp/voltforge-joyor-metadata.json"))
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    references = json.loads((HERE / "references.json").read_text())
    results = []
    for key in args.keys or MODELS:
        results.append(export(key, MODELS[key], references[key], args.evidence if args.render else None))
        args.metadata.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
