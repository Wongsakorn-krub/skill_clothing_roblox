# Face painting workflow

## Choose the source

Follow the face option in SKILL.md. Reuse saved textures exactly for "หน้าเดิม" or "ไม่ต้องเจนใหม่". Use imagegen for requested image creation or editing. Inspect any local reference before editing it, and supply every required reference through the tool's supported image input. Do not promise identical regenerated pixels from a prompt: the cached PNG is the repeatable source.

## Inspect and preserve

Inspect the live model, head vertex group, local axes, head bounds, existing head materials and UVs. Use the current user's request verbatim as Blender MCP's user_prompt. Save a new backup copy before modifying. Do not open the cached .blend over the user's scene.

The cached model has local X horizontal, Y up and +Z front; the object transform makes its front world -Y. Its Head bounds are approximately X [-0.598924, 0.598925], Y [0.898750, 2.101250], Z [-0.5989, 0.5989]. These values describe this model only. Inspect another model and derive its mapping rather than assuming these axes or dimensions.

Preserve vertex coordinates/counts, polygons, vertex weights, modifiers, armature, animation, body material assignments, original materials and every existing UV layer. Never rerun the clothing script with preview_skin=True over a painted face. Preserve the existing skin appearance; when it is texture-driven, sample or retain that shader instead of reading an unconnected default Base Color value.

## Apply a separate face layer

For the measured R6 head:

1. Identify head polygons whose vertices all belong to Head with weight >0.5. Snapshot body polygon material indices and existing UV coordinates before changing anything.
2. Load the chosen PNG, pack it in the blend, and use a dedicated Face_Paint_UV layer and R6 Painted Anime Face material. Reuse these named resources on repeat application; do not duplicate them on every run.
3. Derive planar UV coordinates from the actual head bounds: u=(x-x_min)/(x_max-x_min), v=(y-y_min)/(y_max-y_min). This maps the full image to the front of this head. Adjust margins only after visual inspection if a different image has different framing.
4. Assign the face material only to forward-facing head polygons. For this head, local normal.z > 0.15 selected 125 polygons. Leave the back and side skin materials intact; this threshold is not universal.
5. Connect an explicit UV Map node for Face_Paint_UV to the image. Mix the underlying skin color with the PNG's color using its Alpha as the factor, then connect the result to Principled BSDF Base Color. Keep the material opaque: transparency belongs to the decal overlay, not to the head surface. Use Principled roughness about 0.88 for this style.
6. Keep the clothing shader explicitly connected to Clothing_Paint_UV. Do not let a change in active UV silently remap clothing or other materials that depend on the active render UV; set explicit references or retain their original active render UV.
7. Verify body assignments and pre-existing UVs are identical to their snapshots. Inspect the applied face from the front and three-quarter view. Check eye alignment, mouth orientation, transparency edges, side wrapping and seams.
8. Save a new packed .blend, the PNG, a face close-up and a whole-character preview. Restore any temporary render camera changes. Save user deliverables through the Library workflow and persist updates to this skill through its Git repository.

Look shader nodes up by type, not localized display names. Do not hardcode unsupported Blender enum values. On a different head layout, adapt the projection and selection to the inspected geometry; do not claim the original 125-polygon selection applies.

## Original design prompt template

Replace bracketed fields only with choices supported by the request. For "design it yourself", choose an original face that suits the character; briefly state the choice and proceed.

> Create one original game-ready facial decal for a Roblox R6 head, viewed straight on in an orthographic flat layout. Character personality: [personality]. Art style: [style matching the outfit]. Eye color: [color]. Brows: [shape]. Mouth: [expression]. Draw only two eyes with opaque sclera and pupils, eyebrows, a minimal nose mark, and a simple mouth. Use a genuinely transparent background with clean antialiased edges. Do not draw a head silhouette, skin rectangle, ears, hair, neck, body, accessories, text, watermark, lighting, or cast shadows. Keep both eyes level and facing forward. Place eye centers near 31% and 69% of canvas width and 43% of canvas height from the top; brows around 30%, nose around 59%, mouth around 72%. Leave ample transparent margins. Use clear shapes readable on a small game character. Output one square RGBA PNG. Facial marks may be shaded subtly, but do not bake scene lighting into the decal.

For the cached style use: adult male anime swordsman, slate-blue narrow almond eyes, dark angular brows, small warm-brown nose mark, subtle confident closed smile; blue-and-white robe aesthetic. Request transparent_background=True. Inspect the result because prompts cannot guarantee exact feature positions, alpha, or pixel dimensions.

## Cache and reuse

Keep each accepted design in its own versioned asset folder with the exact PNG, preview and manifest containing actual dimensions, SHA-256, measured mapping and original brief. Do not overwrite anime-face-v1 when making a new face. A prompt is a design recipe; the retained image and mapping are what avoid regeneration.
