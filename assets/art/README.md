# Dino Ages — drop-in art pipeline & asset specification

Drop art for a creature into `assets/art/<creature>/` (or a scene into
`assets/art/scenes/<age>/`) and the app uses it automatically — no code changes.
Everything is served from the app itself at `/art/...` (self-hosted, no third-party CDN). If a folder
is missing or invalid, the app falls back to the built-in code-drawn art, so you
can replace one creature at a time.

Creature folders (lowercase keys): `trilobite`, `anomalocaris`, `opabinia`,
`pikaia`, `hallucigenia`, `wiwaxia`.

## Canvas, anchors, format
- **Canvas:** 240 × 240 units, creature centred horizontally, **feet/underside at
  y ≈ 190**, head toward the top. The on-floor **shadow sits at y ≈ 214**.
- **Format:** transparent **SVG** (preferred, crisp at any size) or transparent
  **PNG at 480 × 480** (2×). One file per layer, all the same 240×240 canvas so
  they stack in register (like Photoshop layers).
- **Pivots:** give the rotation anchor for any part that swings (antenna, fin,
  nozzle, tail) as `[x, y]` in canvas units.

## Two ways to supply art

### 1) Easiest — one flat image (gets bob / squash / rotate life)
```
assets/art/anomalocaris/
  creature.png        (or .svg) — the whole creature, transparent, 480×480
  rig.json            {"image": "creature.png"}
```
Good for a quick image-generator result. It will gently bob and squash on
tap/correct, but parts won't move independently.

### 2) Best — layered parts (full rig: idle, blink, sway, happy, kind-wrong…)
```
assets/art/anomalocaris/
  shadow.svg   body.svg   eyes.svg   mouth.svg   limbs.svg   tail.svg   extras.svg
  rig.json
```
`rig.json`:
```json
{
  "name": "Anomalocaris",
  "viewBox": "0 0 240 240",
  "shadow": "shadow.svg",
  "parts": [
    {"id": "body",  "src": "body.svg"},
    {"id": "limbs", "src": "limbs.svg", "anim": "sway", "pivot": [50, 120]},
    {"id": "tail",  "src": "tail.svg",  "anim": "sway", "pivot": [206, 128]},
    {"id": "eyes",  "src": "eyes.svg",  "anim": "blink"},
    {"id": "mouth", "src": "mouth.svg"},
    {"id": "extras","src": "extras.svg"}
  ],
  "states": {"idle":"breathe+blink+sway","tap":"hop","talking":"talk",
             "happy":"happy","kindWrong":"wrong","sleeping":"dim","celebrate":"happy"}
}
```
- `anim: "blink"` → the part blinks (use for the eyes layer; put each eye white +
  a `class="cr-pupil"` circle so the eyes also follow the pointer).
- `anim: "sway"` → the part gently rotates around its `pivot` (fins, antennae,
  nozzle, tail).
- Everything breathes together; `happy`/`kindWrong`/`tap`/`talking` are driven by
  the app. The whole creature should read at a glance even with no animation.

**Worked example:** `assets/art/trilobite/` (shadow, body, antenna, eyes, face +
rig.json) is a complete, working reference — copy its structure.

## Backgrounds (scenes)
```
assets/art/scenes/cambrian/
  layer1_sky.svg ... layer6_foreground.svg   (5–7 layers, back→front, 1200×800+)
  scene.json  {"layers":[{"src":"layer1_sky.svg","depth":0.1}, ...],
               "particles":{"bubbles":40,"plankton":30,"fish":6,"caustics":true}}
```
`depth` 0 (far, barely moves) → 1 (near, moves most) for parallax. Keep tall
foreground plants at the **left/right edges only** so they never cover the UI.
The code-drawn Cambrian scene is the fallback until these files exist.

## Per-creature spec for an illustrator / image generator (Age 1)
Base each on the REAL animal, then make it friendly (big eyes, mouth, cheeks,
soft shading, rim light, a clear texture). Each needs its own palette.
| Creature | Must-have features | Personality |
|---|---|---|
| Trilobite | 3 lobes (raised central axial + 2 side), segmented ribs, two eyes, antennae | calm, wise |
| Anomalocaris | 2 front grasping appendages, circular ringed mouth, stalked eye, side swim-flaps, fan tail | confident, a bit cheeky |
| Opabinia | **five** stalked eyes, long frontal nozzle ending in a claw, segmented body + flaps | comically surprised |
| Pikaia | eel ribbon, visible notochord line + zig-zag muscle bands, gentle eye | gentle, curious |
| Hallucigenia | paired dorsal spines, ~7 pairs of tentacle legs, tiny head | quirky, playful |
| Wiwaxia | overlapping scaly armour (sclerites), two rows of upward spikes | proud little tank |

Deliver each as layered parts (preferred) or one transparent image. If you want
me to wire a newly-dropped creature or tune its rig, just say so.
