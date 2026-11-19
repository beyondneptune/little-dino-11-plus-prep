# UI OVERHAUL — Dino Ages (paste this to Claude Code)

The parent has reviewed the Checkpoint 1 screenshots and rejected the look: "dull, boring, looks like Windows 3.1, not vibrant, not interactive." The question engine, verifiers and serve gate are correct and are NOT being changed. The UI now has to be top notch: two children (Year 3 and Year 4) must WANT to open this every day.

Read `DESIGN_SPEC.md` again, then treat this document as overriding it wherever they differ. Be honest with yourself: the current build did not meet the spec. Do not defend it. Rebuild the front end.

## 0. Hard boundaries
- Do NOT touch generators, testers, verifiers, banks, the serve gate or mastery logic. The UI only presents what the API serves. `make test` must stay green throughout.
- No external network requests at runtime. Vendor every library and font into the repo (self-hosted). Licences must allow it; record them in `design/LICENSES.md`.
- Original art only. No copyrighted characters, no traced or imitated existing artwork.
- Work on a branch (`ui-overhaul`). Do not merge until the gate in section 8 passes.

## 1. Bugs seen in the screenshots (fix first)
1. Lesson text shows raw markdown (`*Common mistake:*`). Render properly.
2. Parent PIN screen: Back button overlaps the input. Layout is broken.
3. Home screen: background gradient ends in a hard band partway down the screen; the scene must fill the viewport.
4. Museum: creature art is clipped inside cards.
5. All screens are top-left aligned with large dead areas at tablet and desktop sizes.
6. Map shows 3 creatures; every age must show all 6 stations plus the Fossil Dig.

## 2. Art direction: "a storybook nature documentary for kids"
Mood: rich, warm, glowing, layered, friendly. Think chunky rounded characters with big expressive eyes, soft gradients, rim lighting, visible depth. Not flat clip-art.
- Display font for titles and buttons: a chunky rounded face (e.g. Fredoka, Baloo 2 or similar, OFL-licensed, self-hosted). Body: a highly legible rounded sans (e.g. Nunito). No default system fonts anywhere.
- Each age has its OWN palette, lighting and weather, not one theme recoloured:
  Cambrian Seas (turquoise water, god rays, bioluminescent glow), Devonian (murky green shallows, giant fish), Carboniferous Swamps (misty greens, giant dragonflies), Permian (red desert, heat shimmer), Triassic (dusty golden plains), Jurassic (lush jungle, mist, ferns), Early Cretaceous (flowers, warm light), Late Cretaceous (dramatic sunset sky, volcano glow), Paleogene (grassland dawn), Ice Age (aurora, snow, breath clouds).
- UI chrome should feel like part of the world: buttons are chunky and tactile (raised, pressable with squash-and-release), panels look like carved stone, wood, bone, amber or sea glass depending on the age. Generous rounded corners, soft shadows, small decorative details.
- Every screen fills the viewport edge to edge with a scene; no empty cream pages.

## 3. How to produce art that is actually good
Hand-drawing ellipses was the failure. Required approach:
- Build a reusable **Creature Kit**: each creature is a layered SVG (body, belly, back plates/stripes, limbs, tail, head, eye, pupils, eyelids, mouth, cheek blush, highlights, shadow) using gradients, outlines with varied weight, texture patterns and rim light.
- Each creature is rigged with separate animated parts and these states: idle (breathing, blinking, tail/fin sway), hover/tap (look at the pointer, bounce), talking (mouth moves while speech bubble types out), happy (jump, spin, sparkle), sad-but-kind (small slump, then encouraging nod), sleeping (locked station), celebrate (bones, confetti).
- Produce each creature at real illustration quality. Study your own output screenshot by screenshot against section 8's rubric, and redraw until it passes. Budget your effort on the first creature (Trilobite): get that one excellent, then derive the kit.
- Backgrounds: 5–7 parallax layers per age (sky/water, far shapes, mid landscape, near foliage, foreground frame), animated ambient life (drifting particles, swimming fish, falling pollen/snow, swaying plants, light rays, heat shimmer).
- If you judge that vector-by-code cannot reach the bar for a creature, say so plainly in STATE.md and list which assets would be best produced by the parent with an image generator or an illustrator, with exact filenames, sizes, transparent-background layers needed and a drop-in folder (`assets/art/<creature>/`). Build the pipeline so dropped-in art works with the same animations (sprite sheets or layered PNG/SVG). Do not silently ship weak art.

## 4. Motion and interactivity engine
- Use a proper animation approach, not CSS transitions only: vendored GSAP (check its licence for this use) or Web Animations API plus a small canvas/PixiJS layer for particles. Target 60fps on a mid-range tablet; test with throttled CPU.
- Page transitions are never cuts: the "time machine" between ages, zoom into a station, door/portal swirl, creature walking in.
- Micro-interactions everywhere: buttons press and bounce, cards tilt on hover, creatures follow touch, ripples on tap, numbers count up, progress bars fill with a shine.
- Honour `prefers-reduced-motion` (calm mode) and provide a visible toggle.

## 5. Screens (all must be rebuilt)
**Home / who's playing:** full-screen animated world (time-vortex or sunrise over a prehistoric sea). Big logo with a hand-lettered feel. Each child is a large character card with their own avatar (child picks a baby dino buddy; the buddy follows them everywhere and grows through the course). Streak flame, "Continue your expedition" big button showing where they left off. "Grown-ups" is small and tucked away.

**River of Time map:** a scrolling, parallax landscape with all 10 ages as distinct destinations along a winding path; locked ages are misty and silhouetted, the current one glows; the buddy dino walks along the path. Tapping an age triggers the time-machine transition.

**Age map (e.g. Cambrian Seas):** a rich full-screen scene with all 6 creature stations + the Fossil Dig placed naturally in the scenery, each with a progress ring, a bobbing idle animation and an unlock state. Ambient life. Clear next-best action highlighted (the system's recommended weakest topic) with a pulsing glow and the buddy pointing at it.

**Station (meet → learn → practise):**
- Meet: the creature swims or walks in, greets the child, speech bubble types out.
- Learn: NOT a text wall. Break each lesson into 3–6 short animated cards, with the creature "teaching" each one. Each card has ONE idea, a visual, and a quick interactive try-it before moving on (for example, rounding: a draggable number line with a ball that snaps and shows the nearer ten; place value: tappable digit blocks; times tables: array grid that fills). Provide a manipulative or visual for every topic type, built from reusable components (number line, place-value blocks, array grid, fraction bar, clock, coordinate grid, balance scale, letter tiles, shape/net viewer). Render lesson text with a proper markdown renderer, short sentences, reading level capped at about Year 4–5.
- Practise: a game layer around each question, not four beige buttons. The creature is on screen with the question in a speech/story bubble; options are chunky tappable tiles; a progress path shows the creature travelling along a trail toward the station's reward; correct answers trigger a happy reaction, sparkles, sound and the streak counter; wrong answers get a kind reaction and a clear, short per-option explanation (use the engine's distractor explanations), then a "try a similar one" retry. Timed/exam-practice mode later, optional.
- Finish: a celebratory result screen with stars, bones collected, buddy dance, and what to do next.

**Fossil Dig (per-age review):** an interactive dig site: brush away dust by dragging to reveal bones as the child answers a mix of earlier topics; assemble the skeleton at the end.

**Museum:** a proper museum hall: skeletons assembled bone by bone, fact cards that flip in 3D, glass cases with lighting, creatures in dioramas; locked items as dark silhouettes. Nothing clipped.

**Parent area:** can be calmer but must still be polished: fixed PIN layout, clean cards, per-topic mastery heatmap by age, weak-topic list, time spent, streaks, readable on phone and tablet. Use the same typography and palette.

## 6. Layout and responsiveness
Design mobile-first for tablet portrait (768×1024) and landscape (1024×768), then phone and desktop (1440×900). Scenes fill the viewport and re-compose per aspect ratio (not just scale). Minimum 48px touch targets. Keep the existing Aa/A+ text-size control but restyle it as a part of the UI (small, unobtrusive icon).

## 7. Sound and feedback
Add a short, original, synthesised sound set via WebAudio (tap, correct, wrong-gentle, streak, bone collected, page whoosh, ambience per age, a creature "voice" blip while it talks). A friendly first-run prompt asks "Sound on?"; remember the choice; a mute button is always visible. No audio files from outside sources. Add vibration (where supported) on correct answers.

## 8. Process and the gate: ONE vertical slice first
Do not rebuild everything and hope. Rebuild in this order and stop at the gate:
1. Design foundations: fonts, tokens (colours, radii, shadows, spacing), button/panel components, motion helpers, audio helper, markdown renderer.
2. Vertical slice only: Home, Age 1 map, Trilobite station (meet, one learn card set with an interactive number-line for rounding, practise with game layer, finish screen), and the buddy.
3. Capture screenshots at 768×1024, 1024×768, 1440×900, plus a 10-second screen recording or GIF of the map and the practise flow (use Playwright video), plus a frame-rate measurement.
4. Self-review against this rubric, scoring each item 1–5 honestly, quoting what you see in the screenshot: (a) Would a 9-year-old ask to play it? (b) Depth: layers, lighting, shadows. (c) Character: expressive, animated creatures. (d) Motion: ambient life and transitions. (e) Colour: vibrant and cohesive, age-specific palette. (f) Typography: chunky, readable, not default. (g) Interactivity in lesson and practise. (h) Feedback: reactions, sound, rewards. (i) No dead space; layout fits every size. (j) No visual bugs. Any item below 4 means iterate before the checkpoint. Do not claim a score you cannot justify from the screenshots.
5. CHECKPOINT: write `design/UI_CHECKPOINT.md` with the screenshots, the GIF, the scores and the list of anything that falls short. STOP and wait for the parent. Do not proceed to other ages or screens until the parent approves the slice.
6. After approval: roll the kit out to the remaining Age 1 screens (Anomalocaris, Pikaia, Fossil Dig, Museum, Parent area), then the other nine ages one by one, each with its own scene, palette, creatures and ambient life, with screenshot QA at three sizes per age and `make test` green at each commit.

## 9. Do not
- Do not ship placeholder shapes as final art, and do not mark visual work as done without screenshots reviewed against the rubric.
- Do not spend effort on the question engine in this pass.
- Do not add anything that makes a screen heavier than the tablet can run at 60fps.

Begin with section 1 (bug fixes) and section 8 step 1, then go straight to the vertical slice.
