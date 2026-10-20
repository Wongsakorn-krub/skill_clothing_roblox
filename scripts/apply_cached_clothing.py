"""Apply the approved cached outfit in Blender. No image generation or network calls."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets"
REQUIRED = ("Torso", "Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg")


def _bpy():
    import bpy
    return bpy


def _key(value):
    return "".join(c.lower() for c in value if c.isalnum())


def _inputs(object_name, asset="blue-robe-v1"):
    bpy = _bpy()
    ob = bpy.data.objects.get(object_name)
    if ob is None or ob.type != "MESH":
        raise ValueError("Choose an existing mesh object.")
    if ob.mode != "OBJECT":
        raise ValueError("Switch the target mesh to Object Mode.")
    if ob.data.users != 1:
        raise ValueError("Target mesh is shared. Make an explicit single-user copy first.")
    folder = (ASSET_ROOT / asset).resolve()
    if ASSET_ROOT.resolve() not in folder.parents:
        raise ValueError("Asset must be inside the skill assets directory.")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    texture = (folder / manifest["texture"]).resolve()
    if folder not in texture.parents:
        raise ValueError("Texture path escapes the asset folder.")
    if hashlib.sha256(texture.read_bytes()).hexdigest() != manifest["texture_sha256"]:
        raise ValueError("Cached texture hash mismatch; do not overwrite or regenerate it.")
    if manifest["axes"] != {"horizontal": "X", "up": "Y", "front": "+Z"}:
        raise ValueError("This script requires local X-horizontal, Y-up, +Z-front axes.")
    canonical = {_key(n): n for n in REQUIRED}
    mapping = {g.index: canonical[_key(g.name)] for g in ob.vertex_groups
               if _key(g.name) in canonical}
    found = set(mapping.values())
    if found != set(REQUIRED):
        raise ValueError("Missing body groups: " + ", ".join(sorted(set(REQUIRED) - found)))
    verts = {n: [] for n in REQUIRED}
    for v in ob.data.vertices:
        weights = [(g.weight, mapping[g.group]) for g in v.groups if g.group in mapping]
        if not weights or max(weights)[0] <= 0.5:
            raise ValueError("Every vertex must have a dominant R6 body group.")
        verts[max(weights)[1]].append(v)
    bounds = {}
    for n, vs in verts.items():
        if not vs:
            raise ValueError("Empty body group: " + n)
        bounds[n] = [(min(v.co[k] for v in vs), max(v.co[k] for v in vs)) for k in range(3)]
        if any(hi - lo < 1e-6 for lo, hi in bounds[n]):
            raise ValueError("Degenerate body dimensions: " + n)
    def center(n, axis):
        return sum(bounds[n][axis]) / 2
    if not (center("Right Leg", 1) < center("Torso", 1) < center("Head", 1)
            and center("Left Leg", 1) < center("Torso", 1)
            and center("Right Arm", 0) < center("Torso", 0) < center("Left Arm", 0)):
        raise ValueError("Local orientation differs from the cached R6 layout.")
    face_groups = []
    for p in ob.data.polygons:
        names = set()
        for vi in p.vertices:
            v = ob.data.vertices[vi]
            weights = [(g.weight, mapping[g.group]) for g in v.groups if g.group in mapping]
            names.add(max(weights)[1])
        if len(names) != 1:
            raise ValueError("A face crosses body groups; this requires a different UV mapping.")
        face_groups.append(next(iter(names)))
    width, height = manifest["image_size"]
    rectangles = [r for part in manifest["panels"].values() for r in part.values()]
    rectangles += list(manifest["caps"].values())
    for x0, y0, x1, y1 in rectangles:
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError("Invalid cached panel bounds.")
    return bpy, ob, manifest, texture, bounds, face_groups


def inspect(object_name, asset="blue-robe-v1"):
    _, ob, manifest, texture, bounds, groups = _inputs(object_name, asset)
    return {
        "object": ob.name, "asset": manifest["id"], "texture": str(texture),
        "vertices": len(ob.data.vertices), "polygons": len(ob.data.polygons),
        "uv_layers": [u.name for u in ob.data.uv_layers],
        "modifiers": [(m.name, m.type) for m in ob.modifiers],
        "body_faces": {n: groups.count(n) for n in REQUIRED},
        "image_generation_required": False,
    }


def _linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _material(bpy, mesh, name, rgb):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        raise ValueError("Expected Principled BSDF in the skill-owned material.")
    rgba = tuple(_linear(c) for c in rgb) + (1,)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.85
    mat.diffuse_color = rgba
    if mat.name not in mesh.materials:
        mesh.materials.append(mat)
    return mat, mesh.materials.find(mat.name), bsdf


def apply(object_name, *, backup_path, output_path=None, preview_skin=False,
          asset="blue-robe-v1"):
    bpy, ob, manifest, texture, bounds, groups = _inputs(object_name, asset)
    backup = Path(backup_path).resolve()
    output = Path(output_path).resolve() if output_path else None
    protected = ASSET_ROOT.resolve()
    for path in (backup, output):
        if path is None:
            continue
        if path.suffix.lower() != ".blend" or path.exists():
            raise ValueError("Choose a new, non-existing .blend path: " + str(path))
        if protected == path or protected in path.parents:
            raise ValueError("Never save results over the skill's cached assets.")
        if not path.parent.is_dir():
            raise ValueError("Destination parent must already exist: " + str(path.parent))
    if output and output == backup:
        raise ValueError("Backup and output paths must be different.")
    # Validate image dimensions from PNG header before changing Blender data.
    payload = texture.read_bytes()
    actual = [int.from_bytes(payload[16:20], "big"), int.from_bytes(payload[20:24], "big")]
    if payload[:8] != b"\x89PNG\r\n\x1a\n" or actual != manifest["image_size"]:
        raise ValueError("Texture dimensions differ from the cached manifest.")
    before = inspect(object_name, asset)
    bpy.ops.wm.save_as_mainfile(filepath=str(backup), copy=True)
    mesh = ob.data
    original_uv = mesh.uv_layers.active.name if mesh.uv_layers.active else None
    if "r6_clothing_original_assignment" not in ob:
        ob["r6_clothing_original_assignment"] = json.dumps({
            "materials": [m.name if m else None for m in mesh.materials],
            "face_material_indices": [p.material_index for p in mesh.polygons],
            "active_uv": original_uv,
        })
    uv_name = "R6_Clothing_" + manifest["id"]
    uv = mesh.uv_layers.get(uv_name) or mesh.uv_layers.new(name=uv_name)
    mesh.uv_layers.active = uv
    uv.active_render = True
    image = bpy.data.images.load(str(texture), check_existing=True)
    image.name = "R6_Atlas_" + manifest["id"]
    image.pack()
    prefix = "R6Cache::" + manifest["id"] + "::"
    cloth, cloth_index, bsdf = _material(bpy, mesh, prefix + "Clothing", (0.14, 0.26, 0.55))
    _, sole_index, _ = _material(bpy, mesh, prefix + "Soles", (0.055, 0.06, 0.075))
    skin_index = None
    if preview_skin:
        _, skin_index, _ = _material(bpy, mesh, prefix + "NeutralSkin", (0.84, 0.69, 0.57))
    nodes, links = cloth.node_tree.nodes, cloth.node_tree.links
    tex = next((n for n in nodes if n.type == "TEX_IMAGE"), None) or nodes.new("ShaderNodeTexImage")
    tex.image = image
    uv_node = next((n for n in nodes if n.type == "UVMAP"), None) or nodes.new("ShaderNodeUVMap")
    uv_node.uv_map = uv_name
    links.new(uv_node.outputs["UV"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nodes.active = tex
    tex.select = True
    width, height = manifest["image_size"]
    def clamp(x):
        return max(0.0, min(1.0, x))
    for p, group in zip(mesh.polygons, groups):
        if group == "Head":
            if preview_skin:
                p.material_index = skin_index
            continue
        n, b = p.normal, bounds[group]
        if abs(n.y) > 0.9:
            side = "top" if n.y > 0 else "bottom"
        elif abs(n.z) >= abs(n.x) - 1e-5:
            side = "front" if n.z > 0 else "back"
        else:
            side = "left" if n.x > 0 else "right"
        if side == "bottom" and "Arm" in group:
            if preview_skin:
                p.material_index = skin_index
            continue
        if side == "bottom" or (side == "top" and "Leg" in group):
            p.material_index = sole_index
            continue
        table = manifest["panels"][group]
        if side == "top":
            rect = manifest["caps"]["arm_top" if "Arm" in group else "torso_top"]
        elif side in ("left", "right") and "Arm" in group:
            outer = ((group == "Right Arm" and side == "right") or
                     (group == "Left Arm" and side == "left"))
            rect = table["outer" if outer else "inner"]
        elif side in ("left", "right") and "Leg" in group:
            rect = table["side"]
        else:
            rect = table[side]
        p.material_index = cloth_index
        for li in p.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            xn, yn, zn = [clamp((co[k] - b[k][0]) / (b[k][1] - b[k][0])) for k in range(3)]
            if side == "front":
                u, v = xn, yn
            elif side == "back":
                u, v = 1 - xn, yn
            elif side == "right":
                u, v = 1 - zn, yn
            elif side == "left":
                u, v = zn, yn
            else:
                u, v = xn, zn
            x0, y0, x1, y1 = rect
            uv.data[li].uv = ((x0 + (x1 - x0) * u) / width,
                              1 - (y1 - (y1 - y0) * v) / height)
    ob.active_material_index = cloth_index
    ob["r6_clothing_cache"] = json.dumps({
        "id": manifest["id"], "sha256": manifest["texture_sha256"], "uv": uv_name,
    })
    mesh.update()
    after = inspect(object_name, asset)
    for key in ("vertices", "polygons", "modifiers"):
        if before[key] != after[key]:
            raise RuntimeError("Unexpected geometry or rig change: " + key)
    if output:
        bpy.ops.wm.save_as_mainfile(filepath=str(output))
    return {**after, "backup": str(backup), "output": str(output) if output else None,
            "texture_packed": bool(image.packed_file), "head_preserved": not preview_skin}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--object", required=True)
    parser.add_argument("--asset", default="blue-robe-v1")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup")
    parser.add_argument("--output")
    parser.add_argument("--preview-skin", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if args.apply:
        if not args.backup:
            parser.error("--apply requires a new --backup path")
        result = apply(args.object, asset=args.asset, backup_path=args.backup,
                       output_path=args.output, preview_skin=args.preview_skin)
    else:
        result = inspect(args.object, args.asset)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
