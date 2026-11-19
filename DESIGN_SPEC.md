# Design spec: the visual and interactive experience (standing rules)

Saved from the earlier autonomous prompt (cancelled). The parent's top concern
is that the children find the platform beautiful, interactive and exciting.
Follow this for every screen, and verify with real screenshots.

## 7. Delight: the visual and interactive experience

**Goal: a child asks to play. It should feel like an adventure through time,
not a worksheet.** The parent cares about this more than anything else, so
spend real effort here and check it with real screenshots.

### Art direction (write `design/ART_DIRECTION.md` first, then follow it)
- One consistent, warm, richly coloured illustrated style (vector/SVG, layered
  scenes), a distinct palette and landscape for each of the 10 ages, original
  characters only. Two original friendly guides (an explorer and a small
  companion creature) with expressions and idle animations.
- Scientifically reasonable creatures (feathers on theropods where the
  evidence says so), each with a distinct personality pose and idle animation,
  and reactions: cheering on success, gentle encouragement on mistakes.
- Spend the most polish on Age 1 and on Ages 5-8 (the real dinosaurs).

### Experience
- **Home screen:** a beautiful, scrollable "river of time" map through the 10
  ages, with parallax layers and ambient life (drifting clouds, swaying ferns,
  volcano glow, swimming creatures). Locked ages look mysterious, not
  punishing.
- **Time-machine moment** when an age opens; confetti and sparkle on mastery.
- **Creature stations:** tap a creature to meet it, learn, practise, earn its
  **fact card** (collectible; no loot boxes, no randomness for rewards).
- **Fossil Dig:** brush away dirt to reveal each question; each mastered topic
  adds a bone, completing the creature's skeleton in the **Museum**, where the
  child can see their collection. A **Field Journal** sticker book records
  achievements.
- **Interactive question types** that are still solver-verified, at least for
  Age 1: drag-and-drop sorting (Venn/Carroll), build-the-net (cube nets),
  number-line placement, shape builders, plus ordinary multiple choice. Each
  new interactive type needs its own verifier and planted-bug test.
- **Short sessions:** about 10-15 minutes per "expedition", a clear "done for
  today" screen with a happy summary, no streak guilt, no countdown pressure
  for the young child, a pause that never loses progress.
- Encouraging, specific feedback; mistakes lead to a clear explanation and a
  retry of a similar question, never to shame.
- Sound effects optional and **off by default**, with a visible mute; no
  autoplay music.

### Quality of build
- Responsive for laptop and tablet (landscape and portrait), touch-friendly
  (tap targets of at least 44px), keyboard usable, respects
  `prefers-reduced-motion`, adjustable text size and a dyslexia-friendly font
  option, WCAG AA colour contrast, bundled fonts and assets only.
- Fast: first screen quickly interactive, smooth animation on a mid-range
  tablet, assets compressed, works with the network blocked.
- Keep the code simple and maintainable; no heavy build chain unless needed.

### Visual QA (automated, every working session that changes the UI)
Use a headless browser (Playwright) to screenshot every screen at 1440x900,
1024x768 and 768x1024 into `design/screenshots/`. Automatically check for
text overflow, overlapping elements, broken images, console errors,
unreachable buttons, tap-target size and contrast. Then **look at the
screenshots yourself** against this rubric and fix what fails:
*Is it beautiful? Is the next action obvious to a 7-year-old? Is anything
babyish or confusing for a 9-year-old? Would a dinosaur-lover think the
creature looks cool and right? Is text readable and not cramped?* Iterate up
to five times per screen. Record results in `design/VISUAL_QA.md`.

---
