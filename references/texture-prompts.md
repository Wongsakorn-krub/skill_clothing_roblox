# Reusable clothing prompts

## Apply the approved outfit without generating
ใช้ $blender-r6-clothing ใส่ชุด blue-robe-v1 ที่เก็บไว้ให้โมเดล R6 ที่เปิดอยู่ใน Blender ใช้ Texture และตำแหน่ง UV เดิม ห้ามเจนภาพใหม่ เก็บโมเดล Rig น้ำหนักกระดูก และใบหน้าเดิม ตรวจด้านหน้า ด้านหลัง และมุมเฉียง แล้วบันทึกไฟล์ .blend โดยฝัง Texture ไว้

## Generate a new outfit atlas only when requested
Attach the real clothing reference images when using this prompt. Do not run it to restore the approved outfit.

Create one production base-color texture atlas for an existing Roblox R6 character. Use the attached clothing reference as the design authority. Preserve its garment layers, colors, asymmetry, seams, cuffs, waist height and visible patterns. Do not invent medals, jewelry, tassels, logos or extra straps. Where the back or sides are not shown, extend the visible garment construction simply and consistently.

OUTPUT
A square 2048 x 2048 image with an exact 4-column by 4-row grid. Each cell occupies 512 x 512 pixels and contains exactly ONE flattened clothing surface. Fill each cell edge to edge. No gaps, decorative frames, grid lines, labels, text, numbers, background, character render, mannequin, hair or face.

CELL ORDER, left to right:
Row 1: torso front | torso back | torso character-right side | torso character-left side.
Row 2: character-right arm front | right arm back | right arm outer side | right arm inner side.
Row 3: character-left arm front | left arm back | left arm outer side | left arm inner side.
Row 4: character-right leg front | right leg back | character-left leg front | left leg back.

ORIENTATION AND PROPORTIONS
Right and left always mean the CHARACTER'S right and left. In a front view, the character's right is on the viewer's left.
The top of every tile is toward the shoulder or waist; the bottom is toward the wrist or ankle. Never rotate a tile.
Torso front/back represent a 2:2 rectangular face. Torso sides and every limb face represent a 1:2 rectangular face. For each 1:2 surface, expand the artwork horizontally to fill its square tile so that it returns to the correct proportions when mapped onto the narrow mesh.
Every arm tile contains ONE arm surface only. Every leg tile contains ONE leg surface only, including ONE boot section if the reference has boots. Never draw two legs, a crotch, a complete pair of pants, or a paired pair of boots inside one tile.
Do not put a neckline or full waist belt on an arm. Do not duplicate torso jewelry onto limbs.

SURFACE PAINTING
Create clean stylized game clothing with controlled painted folds, readable seams, restrained fabric grain and reference-matched color values. Keep large color areas clear at game-camera distance. Use only modest form shading within the folds. No scene lighting, strong baked shadows, shiny highlights, realistic camera effects or perspective.
Match each front edge to its adjacent side/back edge. Keep sleeve hems and belt height consistent across matching tiles. Do not mirror asymmetric details onto the opposite limb.
Deliver the flat atlas only.

## Important operational limits
Prompt wording improves consistency but does not guarantee exact output pixels or seam continuity. Inspect the actual result and measure the returned tile bounds before constructing UVs. Do not blindly use 512-pixel coordinates if the output size or layout differs. For this approved outfit, use the existing 1254-pixel atlas and its measured manifest, not this new-atlas grid.

When a new image is approved, save it and its mapping together. Later applications reuse that cache and require no further generation.
