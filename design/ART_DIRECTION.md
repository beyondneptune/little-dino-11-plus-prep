# Art direction — Dino Ages

The feeling: **a warm, hand-illustrated field expedition through deep time.** A
child should feel like an explorer discovering real creatures, not sitting a test.
Calm, friendly, a little magical — never babyish, never clinical.

## Principles
- One consistent **vector/SVG, flat-with-soft-gradients** style. Layered scenes
  with gentle parallax. No photo-real textures, no harsh outlines.
- **Original art only.** No franchise characters, names, music or assets. All art
  here is drawn as inline SVG in this repo. Any third-party asset would be logged
  in `assets/LICENSES.md` with its licence (none used yet).
- **Scientifically reasonable** creatures (right body plan, era-appropriate). Where
  science is unsure (colour), choose a pleasant plausible palette and the fact
  cards say "scientists think".
- Calm motion only; everything respects `prefers-reduced-motion`. Sound off by
  default.

## Palette
- Global ink: `#22323b` (deep slate, for text — AA contrast on light).
- Parchment UI: `#fbf4e6` surface, `#efe3c8` panels, `#d9c7a0` edges.
- Accent (expedition): `#e07a3f` (warm amber) and `#2f6f6a` (teal).
- Success `#3f9d5a`, gentle-wrong `#c7693f` (never red alarm), focus ring `#2f6f6a`.
- **Age 1 Cambrian Seas palette:** deep sea `#17384d` → `#2b6e86` → shallow
  `#63b7c4`; sand `#e8d6a8`; coral/soft life accents `#e58a6a`, `#f3c969`,
  `#8fb66a`. Light shafts in pale cyan.

## Typography
- System font stack only (bundled/none fetched): `"Segoe UI", system-ui, -apple-system,
  "Helvetica Neue", Arial, sans-serif`. Large, rounded, generous line-height.
- A **dyslexia-friendly toggle** switches to `"Comic Sans MS", "Trebuchet MS",
  sans-serif` with extra letter-spacing (bundled/system only).
- Minimum body 18px; question text 22px+; tap targets ≥ 44px.

## The two guides (original)
- **Fern** — a young explorer in a teal coat and amber hat, round friendly face.
  Gives hints and cheers. Idle: small blink/bob.
- **Pip** — a tiny round companion trilobite with big eyes, rides along. Reacts:
  happy wiggle on success, soft "let's try again" on a miss. Never shames.

## Age 1 scene — Cambrian Seas
A side-on seabed: layered water bands (parallax), drifting light shafts, swaying
soft coral and sponges, a few ambient swimmers. Creature **stations** are glowing
spots on the seabed; tapping one meets the creature. Locked later ages appear up a
"river of time" as misty, mysterious silhouettes — intriguing, not punishing.

## Creatures for the served stations (Age 1)
- **Trilobite** (Maths) — oval segmented body, three lobes, gentle eyes. Teaches
  MA-A05 (rounding), MA-B01 (mental calc).
- **Anomalocaris** (Maths) — graceful swimmer, two front grasping arms, fan tail,
  big compound eyes. Teaches MA-B04 (division facts).
- **Pikaia** (VR) — little eel-like ribbon swimmer. Teaches VR-C02 (letter series).
Each has a **personality pose** and a one-line greeting; earns a **fact card**
(true fact + two sources) and adds a **bone** to its skeleton in the **Museum**.

## Interaction & reward
- Flow per station: Meet → Learn → Guided practice (hints) → Practice → Mastery
  check → fact card + bone. A clear, happy "done for today" stop.
- Rewards are for **mastery and effort**: fact cards and skeleton bones. No loot
  boxes, no randomness, no streak guilt, no countdown pressure for the young child.
- Mistakes → a clear explanation of the right method and a retry of a similar
  question. Encouraging, specific, never shaming.

## Visual QA rubric (applied to every screen)
Is it beautiful? Is the next action obvious to a 7-year-old? Anything babyish or
confusing for a 9-year-old? Would a dinosaur-lover think the creature looks right?
Is text readable and not cramped? Screenshots at 1440×900, 1024×768, 768×1024.
