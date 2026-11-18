"""Small mesh builders for editable, material-isolated scooter assemblies."""

from collections import defaultdict
from math import cos, pi, sin

import bpy
from mathutils import Matrix, Vector


def color(name, hex_color, metal=0.0, roughness=0.44):
    rgb = tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))
    linear = tuple(v / 12.92 if v < 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*linear, 1.0)
    shader = material.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = material.diffuse_color
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    return material


def rounded_rect(half_width, bottom, top, radius, steps=4):
    radius = min(radius, half_width * 0.95, (top - bottom) * 0.47)
    corners = (
        (half_width - radius, top - radius),
        (-half_width + radius, top - radius),
        (-half_width + radius, bottom + radius),
        (half_width - radius, bottom + radius),
    )
    return [
        (y + radius * cos(angle), z + radius * sin(angle))
        for i, (y, z) in enumerate(corners)
        for angle in (i * pi / 2 + j * pi / (2 * (steps - 1)) for j in range(steps))
    ]


class Assembly:
    def __init__(self, name, groups, attributes):
        self.root = bpy.data.objects.new(name, None)
        bpy.context.collection.objects.link(self.root)
        for key, value in attributes.items():
            self.root[key] = value
        self.groups = {}
        for name in groups:
            obj = bpy.data.objects.new(name, None)
            bpy.context.collection.objects.link(obj)
            obj.parent = self.root
            self.groups[name] = obj
        self.batches = defaultdict(lambda: ([], [], set()))

    def mesh(self, vertices, faces, material, group, smooth=False):
        v, f, smooth_faces = self.batches[(group, material)]
        offset = len(v)
        if smooth:
            smooth_faces.update(range(len(f), len(f) + len(faces)))
        v.extend(vertices)
        f.extend(tuple(offset + i for i in face) for face in faces)

    def loft(self, sections, material, group, smooth=False, caps=True):
        count = len(sections[0])
        verts = [p for section in sections for p in section]
        faces = []
        for ring in range(len(sections) - 1):
            for i in range(count):
                a = ring * count + i
                b = ring * count + (i + 1) % count
                faces.append((a, b, b + count, a + count))
        if caps:
            faces += [tuple(reversed(range(count))), tuple(range(len(verts) - count, len(verts)))]
        self.mesh(verts, faces, material, group, smooth)

    def deck(self, x_levels, material, group, radius=0.008, y_offset=0):
        sections = [
            [(x, y + y_offset, z) for y, z in rounded_rect(half_width, bottom, top, radius)]
            for x, half_width, bottom, top in x_levels
        ]
        self.loft(sections, material, group)

    def box(self, center, size, material, group, radius=0.003):
        x, y, z = center
        l, w, h = (value / 2 for value in size)
        bevel = min(radius, l * 0.45, w * 0.4, h * 0.45)
        levels = [
            (x - l, w - bevel, z - h + bevel, z + h - bevel),
            (x - l + bevel, w, z - h, z + h),
            (x + l - bevel, w, z - h, z + h),
            (x + l, w - bevel, z - h + bevel, z + h - bevel),
        ]
        self.deck(levels, material, group, radius, y_offset=y)

    def profile(self, contour, y, width, material, group):
        sections = [[(x, yy, z) for x, z in contour] for yy in (y + width / 2, y - width / 2)]
        self.loft(sections, material, group)

    def pierced(self, outer, inner, y, width, material, group):
        n = len(outer)
        vertices = [
            (x, side, z)
            for side in (y - width / 2, y + width / 2)
            for contour in (outer, inner)
            for x, z in contour
        ]
        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces += [
                (i, j, n + j, n + i),
                (2 * n + i, 3 * n + i, 3 * n + j, 2 * n + j),
                (i, 2 * n + i, 2 * n + j, j),
                (n + i, n + j, 3 * n + j, 3 * n + i),
            ]
        self.mesh(vertices, faces, material, group)

    def shaft(self, a, b, levels, material, group, steps=32):
        a = Vector(a)
        axis = Vector(b) - a
        direction = axis.normalized()
        u = direction.cross(Vector((0, 1, 0)))
        if u.length < 0.05:
            u = direction.cross(Vector((1, 0, 0)))
        u.normalize()
        v = direction.cross(u)
        # Ordering the ring in the reverse direction keeps longitudinal faces outward.
        sections = [
            [
                a + axis * position + u * rx * cos(-2 * pi * i / steps)
                + v * ry * sin(-2 * pi * i / steps)
                for i in range(steps)
            ]
            for position, rx, ry in levels
        ]
        self.loft(sections, material, group, True)

    def rod(self, a, b, radius, material, group, steps=24, radius_end=None):
        radius_end = radius if radius_end is None else radius_end
        self.shaft(a, b, [(0, radius, radius), (1, radius_end, radius_end)], material, group, steps)

    def hub(self, x, z, profile, material, group, steps=64, closed=False):
        sections = [
            [(x + r * cos(i * 2 * pi / steps), y, z + r * sin(i * 2 * pi / steps))
             for i in range(steps)]
            for y, r in profile
        ]
        if closed:
            sections.append(sections[0])
        self.loft(sections, material, group, True, caps=not closed)

    def tube(self, points, radius, material, group):
        points = [Vector(p) for p in points]
        rings = []
        for i, point in enumerate(points):
            d = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
            u = d.cross(Vector((0, 1, 0)))
            if u.length < 0.05:
                u = d.cross(Vector((1, 0, 0)))
            u.normalize()
            v = d.cross(u)
            rings.append(
                [point + radius * (u * cos(-2 * pi * j / 10) + v * sin(-2 * pi * j / 10))
                 for j in range(10)]
            )
        self.loft(rings, material, group, True)

    def cable(self, points, radius, material, group):
        # Smooth Hermite interpolation keeps external brake lines continuous.
        points = [Vector(p) for p in points]
        samples = []
        for i, a in enumerate(points[:-1]):
            b = points[i + 1]
            d0 = (b - points[max(0, i - 1)]) / 2
            d1 = (points[min(i + 2, len(points) - 1)] - a) / 2
            for j in range(7):
                t = j / 7
                samples.append(
                    a * (2*t**3 - 3*t*t + 1) + d0 * (t**3 - 2*t*t + t)
                    + b * (-2*t**3 + 3*t*t) + d1 * (t**3 - t*t)
                )
        self.tube([*samples, points[-1]], radius, material, group)

    def text(self, value, point, size, material, group, angle=0):
        data = bpy.data.curves.new(value, "FONT")
        data.body, data.size, data.extrude = value, size, 0.00015
        data.align_x, data.align_y = "CENTER", "CENTER"
        obj = bpy.data.objects.new(value, data)
        bpy.context.collection.objects.link(obj)
        obj.parent = self.groups[group]
        obj.location = point
        u = Vector((cos(angle), 0, sin(angle)))
        v = Vector((-sin(angle), 0, cos(angle)))
        obj.rotation_euler = Matrix((u, v, u.cross(v))).transposed().to_euler()
        obj.data.materials.append(material)
        return obj

    def finalize(self):
        import bmesh

        for (group, material), (vertices, faces, smooth) in self.batches.items():
            data = bpy.data.meshes.new(f"{group} | {material.name}")
            data.from_pydata(vertices, [], faces)
            data.update()
            for i in smooth:
                data.polygons[i].use_smooth = True
            # Correct normals while retaining deliberately flat, machined surfaces.
            editable = bmesh.new()
            editable.from_mesh(data)
            bmesh.ops.recalc_face_normals(editable, faces=list(editable.faces))
            editable.to_mesh(data)
            editable.free()
            obj = bpy.data.objects.new(data.name, data)
            bpy.context.collection.objects.link(obj)
            obj.parent = self.groups[group]
            obj.data.materials.append(material)
        bpy.context.view_layer.update()

    def objects(self):
        return [self.root, *self.groups.values(), *(obj for g in self.groups.values() for obj in g.children)]
