"""Build the twelve approved product reconstructions with Blender 4.5."""

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

from chassis import deck_shell, headstock, heel_brace, suspension
from equipment import cockpit, wheel
from profiles import PROFILES, REFERENCE_UPDATES


def load_primitives():
    path = ROOT / "scripts/blender/expansion/premium/primitives.py"
    spec = importlib.util.spec_from_file_location("scooter_primitives", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rgb(hex_color):
    channels = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055)**2.4 for v in channels)


def materials(p, c):
    choices = {
        "shell": ("Model powder coat", c["shell"], .32, .44, 0),
        "accent": ("Anodized factory trim", c["accent"], .34, .36, 0),
        "edge": ("Structural graphite casting", "#303338", .46, .31, 0),
        "steel": ("steel", "#656972", .67, .31, 0),
        "silver_dark": ("Dark satin forged aluminium", "#60656b", .59, .39, 0),
        "silver": ("Visible machined hardware", "#a6acb6", .76, .32, 0),
        "tire": ("tire rubber", "#29292b", 0, .86, 0),
        "pad": ("Molded traction mat", "#292d2f", 0, .74, 0),
        "grip_high": ("Traction mat tread", "#363839", 0, .81, 0),
        "grip": ("Textured rubber grips", "#252629", 0, .79, 0),
        "rim": ("Anodized gunmetal", "#24272a", .43, .34, 0),
        "rotor": ("rotor", "#999ea4", .82, .29, 0),
        "matte": ("Molded black polymer", "#232428", .03, .54, 0),
        "motor": ("Hub motor cast cap", "#2f2f31", .49, .41, 0),
        "coil": ("Coil spring steel", "#53565a", .57, .32, 0),
        "screen": ("Dashboard glass", "#202c39", .16, .17, 0),
        "mark": ("Factory print", "#9e9fa4", .12, .50, 0),
        "white": ("Pearl side strip", "#d3d5cf", .16, .40, 0),
        "diffuser": ("Pale lens diffuser", "#a5b1ba", .1, .33, .14),
        "white_lens": ("Projector clear white optic", "#ccddeb", .14, .26, .26),
        "red_lens": ("Molded red rear lens", "#bf211d", .16, .32, .25),
        "amber": ("Reflector amber lens", "#ea830b", .06, .35, .18),
    }
    result = {
        key: p.mat(name,rgb(color),metal,roughness,emission)
        for key,(name,color,metal,roughness,emission) in choices.items()
    }
    # Existing primitive helpers use these names for springs and fasteners.
    for key, material in result.items():
        setattr(p,key,material)
    p.black = result["matte"]
    return result


def flatten(p):
    for part in list(p.parts):
        bpy.ops.object.select_all(action="DESELECT")
        part.select_set(True)
        bpy.context.view_layer.objects.active = part
        if part.type != "MESH":
            bpy.ops.object.convert(target="MESH")
        part = bpy.context.object
        for modifier in list(part.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)

    model = []
    for parent in p.groups.values():
        by_material = {}
        for part in list(parent.children):
            by_material.setdefault(part.data.materials[0].name, []).append(part)
        for material, parts in by_material.items():
            bpy.ops.object.select_all(action="DESELECT")
            for part in parts:
                part.select_set(True)
            bpy.context.view_layer.objects.active = parts[0]
            if len(parts) > 1:
                bpy.ops.object.join()
            combined = bpy.context.object
            combined.name = f"{parent.name} | {material}"
            bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
            combined.data.calc_loop_triangles()
            model.append(combined)
    return model


def studio(p, c):
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 3
    scene.render.resolution_x = scene.render.resolution_y = 472
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = -.6
    scene.world = bpy.data.worlds.new("Studio ambient")
    scene.world.color = (.25,.25,.25)

    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003))
    floor = bpy.context.object
    floor.name = "STUDIO floor"
    floor.data.materials.append(p.mat("Warm gray studio",(.57,.59,.62),0,.92))
    target = Vector((0,0,c["height"]*.49))
    for name,loc,power,size in (
        ("softbox", (1.7,-3.2,3.1), 450, 3.2),
        ("bounce", (-2.1,-1.5,2.0), 300, 2.8),
        ("rim", (1.5,2.8,2.5), 420, 2.2),
    ):
        bpy.ops.object.light_add(type="AREA",location=loc)
        lamp=bpy.context.object
        lamp.name="STUDIO "+name
        lamp.data.energy=power
        lamp.data.shape="DISK"
        lamp.data.size=size
        lamp.rotation_euler=(target-lamp.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.camera_add(location=(2.18,-4.1,1.51))
    camera = bpy.context.object
    camera.name = "STUDIO camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(c["wheelbase"]+c["radius"]*2,c["height"])+.17
    camera.rotation_euler = (target-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=camera
    return scene, camera, target


def build(entry, key, output, render):
    c = {**PROFILES[key], "key": key}
    c["steering_x"] = c["wheelbase"]/2 - (.093 if c["layout"] in ("gt","zt","gt3") else .074)
    corrections = dict(REFERENCE_UPDATES.get(key, {}))
    version = corrections.pop("version", "")
    note = " ".join(s for s in (
        version, c["features"],
        "Photo-guided exterior reconstruction. Hidden assembly envelopes and dimensions are approximate.",
    ) if s)
    model = entry["model"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    p = load_primitives()
    p.groups = {}
    p.parts = []
    m = materials(p,c)
    root = bpy.data.objects.new(entry["name"],None)
    bpy.context.collection.objects.link(root)
    root["source"] = corrections.get("source",entry["source"])
    root["reference"] = entry["image"]
    root["accuracy"] = note
    root["frontAxis"] = "+X"
    root["units"] = "metres"
    root["reconstructionRevision"] = 3
    for name in ("Chassis","Steering","FrontWheel","RearWheel","BatteryMount","ControllerMount","MotorMount"):
        node=bpy.data.objects.new(name,None)
        bpy.context.collection.objects.link(node)
        node.parent=root
        p.groups[name]=node
    deck_shell(p,c,m)
    headstock(p,c,m)
    heel_brace(p,c,m)
    suspension(p,c,m)
    cockpit(p,c,m)
    wheel(p,c,m,True)
    wheel(p,c,m,False)

    parts = flatten(p)
    bpy.context.view_layer.update()
    triangles = sum(len(o.data.loop_triangles) for o in parts)
    coords = [obj.matrix_world @ Vector(corner) for obj in parts for corner in obj.bound_box]
    lo = [min(v[i] for v in coords) for i in range(3)]
    hi = [max(v[i] for v in coords) for i in range(3)]
    assert all(math.isfinite(v) for v in (*lo,*hi))
    assert -.003 <= lo[2] <= .003, (key,lo)
    assert 1 < hi[0]-lo[0] < 1.7 and 1.13 <= hi[2]-lo[2] < 1.45, (key,lo,hi)
    assert len(parts) < 65 and triangles < 98000, (key,len(parts),triangles)
    assert all(group.children for group in p.groups.values())

    bpy.ops.object.select_all(action="DESELECT")
    for o in [root,*p.groups.values(),*parts]:
        o.select_set(True)
    glb = ROOT/"apps/web/public"/model["url"].lstrip("/")
    draft_glb = output/f"{key}.draft.glb"
    bpy.ops.export_scene.gltf(filepath=str(draft_glb),export_format="GLB",use_selection=True,
        export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
    assert draft_glb.stat().st_size < 5_000_000

    photo_path = ROOT/"apps/web/public"/entry["image"].lstrip("/")
    photo = bpy.data.images.load(str(photo_path))
    photo.pack()
    corrections["dimensions"] = list(photo.size)
    corrections["bytes"] = photo_path.stat().st_size
    reference = bpy.data.objects.new("REFERENCE exact pictured product",None)
    bpy.context.collection.objects.link(reference)
    reference.empty_display_type = "IMAGE"
    reference.data=photo
    reference.hide_render=reference.hide_viewport=True
    reference["source"]=root["source"]
    scene,camera,target = studio(p,c)
    scene.render.filepath = f"//{key}-three-quarter.png"
    native = ROOT/model["nativeSource"]
    draft_native = output/f"{key}.draft.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(draft_native),compress=True)
    draft_native.replace(native)
    draft_glb.replace(glb)
    metadata = {
        "name":entry["name"],
        "model": {
            **model, "family":c["family"], "triangles":triangles, "meshes":len(parts),
            "bytes":glb.stat().st_size,
            "revision":hashlib.sha256(glb.read_bytes()).hexdigest()[:12],
        },
        "variantNote":note,
        **corrections,
    }
    (output/f"{key}.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(f"EXPORTED {key}: {triangles} triangles, {len(parts)} visible mesh groups",flush=True)
    if render:
        for angle,location in (("three-quarter",(2.18,-4.1,1.51)),("side",(0,-4.20,c["height"]*.49))):
            camera.location=location
            camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
            scene.render.filepath=str(output/f"{key}-{angle}.png")
            bpy.ops.render.render(write_still=True)
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("/tmp/voltforge-performance"))
    parser.add_argument("--render",action="store_true")
    parser.add_argument("keys",nargs="*")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    args.output.mkdir(parents=True,exist_ok=True)
    entries={}
    for batch in ("commuter","premium"):
        data=ROOT/f"apps/web/src/data/vehicle-expansion-{batch}.json"
        for entry in json.loads(data.read_text())["entries"]:
            if "model" in entry:
                entries[entry["model"]["key"]]=entry
    keys=args.keys or PROFILES
    rows=[build(entries[key],key,args.output,args.render) for key in keys]
    (args.output/"metadata.json").write_text(json.dumps(rows,indent=2)+"\n")


if __name__ == "__main__":
    main()
