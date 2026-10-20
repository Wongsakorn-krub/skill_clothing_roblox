---
name: blender-r6-clothing
description: Paint and reuse clothing and optional faces on existing Roblox R6 models in Blender through Blender MCP. Use for R6 texture painting, UV clothing, face painting, original face design, applying supplied face artwork, or reusing saved textures without regenerating images. Includes cached outfit and face textures, previews, UV guidance and a tested clothing application script.
---

# Blender R6 Clothing and Face Painting

Use the approved cached outfit by default. For "same outfit", "ชุดเดิม", "ชุดสีน้ำเงินขาว", or "ไม่ต้องเจนใหม่", do not call an image generator. Apply `assets/blue-robe-v1/texture.png` with its measured manifest.

## Optional face painting

Resolve the face option from the user's request before painting. Treat explicit instructions such as "คิดขึ้นมาเอง" or "ออกแบบให้เลย" as choosing original design; do not ask again.

| Option | Action |
| --- | --- |
| Keep current face / ไม่เพ้นท์หน้า | Preserve the current head and face. Default for clothing-only requests. |
| Design a face / ให้ออกแบบหน้า | Design an original face suited to the outfit and stated personality; generate a transparent face decal and apply it. |
| Use supplied artwork / ใช้รูปที่ส่งให้ | Inspect and use the user's artwork; preserve the requested design. |
| Reuse saved face / ใช้หน้าเดิม | Apply the cached face texture without image generation. |

For a general face-painting request with no specified source, ask one short optional question: "อยากให้ผมออกแบบหน้าให้ หรือใช้รูป/หน้าเดิมที่มีอยู่ครับ?" If no answer is available, preserve the current face and continue other authorized work. Never generate a new face merely because the clothing skill was invoked. For a face-only request, skip clothing application entirely.

Read [Face workflow and prompts](references/face-painting.md) when a face option is selected. Reuse `assets/anime-face-v1/texture.png`, `preview.png`, and `manifest.json` for the saved blue-grey-eyed, confident-smile face. This is the completed original design from the session; do not claim approval of a new version without user feedback.

## Stored assets

- `assets/blue-robe-v1/painted.blend`: approved model with packed image.
- `assets/blue-robe-v1/original.blend`: original model and rig.
- `assets/blue-robe-v1/texture.png`: immutable approved base-color image.
- `assets/blue-robe-v1/preview.png`: approved appearance.
- `assets/blue-robe-v1/manifest.json`: hash, image dimensions, actual panel crops, axes and recovery identity.
- `scripts/apply_cached_clothing.py`: inspect and apply the atlas without adding geometry.
- [Texture prompts](references/texture-prompts.md): reuse prompt and improved generation prompt; read only for drafting prompts or a requested new outfit.
- [UV and quality rules](references/uv-and-quality.md): orientation, measured crops, preservation and verification.

Resolve all paths from this Skill's own directory. Do not rely on old conversation workspaces or hardcoded machine paths.

## Workflow

1. Inspect the current scene through Blender MCP. Use the user's actual current request verbatim in `user_prompt`. Read object names, mesh groups, modes, material slots, UV maps, modifiers and image availability. Use `look` to see the current model. Do not open a bundled blend over unsaved user work.
2. View the cached preview and confirm the intended outfit from the request. Use the cached image directly for the approved style. If the user requests a different style, inspect their real reference image and follow the new-style workflow below.
3. Run the script's inspection before modifying anything. Require a mesh with Torso, Head, Left Arm, Right Arm, Left Leg and Right Leg groups and compatible local axes. The script accepts underscore/space/case variations. For another layout, derive a new manifest; do not silently apply these rectangles or axes.
4. Choose a new backup path and a new output path. Save a copy before applying. Preserve topology, weights, armature modifiers, animation, original materials and original UVs. Keep the user's face/head unchanged by default. Use `preview_skin=True` only when a neutral skin preview is appropriate to the user's request.
5. Apply the cached atlas using the script. It adds an isolated clothing UV layer and named materials, packs the texture and can save the output blend. It is idempotent for repeated applications. Never replace the approved cached files with a new generation.
6. Inspect front, back and a three-quarter view with `look`. Check one-leg-per-face crops, sleeves, shoulder caps, belt height and UV seams. Compare mesh counts and rig state with inspection results. Keep materials visible in the user's viewport if requested.
7. Save deliverables using the Library workflow. The skill's own source/assets persist with its Git repository. State any saving or installation failure accurately.

## Invoke in live Blender

Load the bundled script into a namespace with its own `__file__`; this avoids rerunning its CLI and avoids guessed working directories.

```python
from pathlib import Path
script = Path(SKILL_ROOT) / "scripts" / "apply_cached_clothing.py"
ns = {"__name__": "r6_clothing_skill", "__file__": str(script)}
exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), ns)
print(ns["inspect"]("rig"))  # use the observed object name
# Choose absolute, writable, non-existing paths before applying.
result = ns["apply"](
    "rig",
    backup_path=BACKUP_PATH,
    output_path=OUTPUT_PATH,
    preview_skin=False,
)
print(result)
```

For isolated validation, use a separate background Blender process with a copy of `original.blend`. Never use the live scene as a test sandbox.

## Create a new outfit only when requested

Read the generation prompt reference. Use imagegen for image creation/editing. Include every real reference image using its supported image mechanism. Keep invisible areas a restrained continuation of the visible design, and label assumptions when relevant.

Inspect the returned artwork before mapping. A prompt cannot guarantee exact panel boundaries. Measure the actual panel rectangles and record them in a new versioned manifest. If a panel contains two legs, crop the intended single leg instead of stretching the pair onto one limb. Never hardcode a new result to the approved atlas's dimensions.

Cache the accepted texture, its hash, measured UV map, preview and packed blend as a new asset version. Reuse that exact version on later requests; do not regenerate merely to restore or reapply it.
