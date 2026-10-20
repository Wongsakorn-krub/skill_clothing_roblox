# UV and quality rules

The approved atlas is 1254 x 1254 pixels with irregular panels. Use manifest.json, not equal quarter divisions. Several bottom-row panels contain two legs; the manifest isolates one leg. Preserve the approved artwork exactly.

Local X is horizontal, Y is up and +Z is front. Character Right Arm is negative X, and appears on the viewer's left in a front view. Convert top-origin pixel rectangles to bottom-origin UVs. Prefer front/back projection on beveled-edge ties.

Validate all hashes, paths, groups and axes before modifying. Keep Object Mode, a single-user mesh, original UVs and materials, topology, weights, armature modifiers, poses and animations. Preserve head materials and UV values by default. The neutral skin preview is an explicit option for an unfinished base, not permission to replace a finished face.

Inspect front, back and three-quarter views. Check one leg per crop, distinct left/right, neckline on torso only, no duplicated torso ornaments on limbs, cuff/belt alignment, packed texture availability and unchanged geometry/rig counts. UV painting does not add puffed sleeves or hanging robe geometry.

The original screenshot was not retrieved as local pixels during the first run; the approved output is an adapted sample. Do not claim exact reconstruction. Use the approved preview as the cached visual authority.
