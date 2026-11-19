# Vendored assets and licences

Everything the UI loads is self-hosted in this repo — the app makes **no external
network requests at runtime**. Third-party assets are listed here with their
licence; all permit self-hosting and redistribution.

## Fonts (SIL Open Font License 1.1)
| Font | Role | File | Source | Licence |
|---|---|---|---|---|
| Fredoka (variable wdth,wght) | Display / titles / buttons | `platform/static/vendor/fonts/Fredoka.woff2` | google/fonts `ofl/fredoka` | OFL 1.1 (`Fredoka-OFL.txt`) |
| Nunito (variable wght) | Body text | `platform/static/vendor/fonts/Nunito.woff2` | google/fonts `ofl/nunito` | OFL 1.1 (`Nunito-OFL.txt`) |

Downloaded at build time from the Google Fonts GitHub mirror and converted to
woff2 with fontTools. Full licence text kept alongside each font.

## JavaScript / animation
No third-party JS libraries are used or vendored. Motion uses the browser's
**Web Animations API**; particles use a small hand-written `<canvas>` system
(original code in this repo); sound is synthesised with the **Web Audio API**
(no audio files). This avoids any library licence/redistribution question and
keeps the bundle light for tablets.

## Art
All creature and scene art is **original**, drawn as layered SVG in this repo
(`platform/static/age1/creatures.js`, scene builders). No copyrighted characters,
no traced or imitated artwork. If any creature is later replaced by parent-/
illustrator-supplied art, it will be dropped into `assets/art/<creature>/` and
recorded here with its source and licence.
