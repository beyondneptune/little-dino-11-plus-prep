/* Creature Template Kit — parametric, original SVG body plans so a new creature
   is a CONFIG entry (+ light touch-ups), not hand-drawn from scratch. Output is
   rig-compatible (viewBox 0 0 240 240, .cr-body, .cr-eye, .cr-shadow, .cr-pupil),
   so the existing idle/blink/pointer-eye/reaction animations and the art pipeline
   apply unchanged. A generated/illustrated hero image can still override any
   template by dropping files in assets/art/<id>/ (the rig loader prefers those).

   Config:
   {
     id, name,
     plan: "biped" | "longneck" | "armoured" | "quadruped" |
           "flyer" | "swimmer" | "arthropod" | "mammal",
     colors: { main, belly, accent },
     size: 1.0,              // overall scale
     horns: 0..3,            // head horns (biped/quadruped/armoured)
     plates: false|true,     // back plates (armoured/quadruped)
     spikes: false|true,     // tail spikes (armoured)
     crest: false|true,      // head crest (biped/flyer)
     tail: "short"|"long",   // tail length
     face: { happy: true }   // friendly face by default
   }
*/
(function (global) {
  let UID = 0;
  const lin = (id, a, b, x2 = 0, y2 = 1) =>
    `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}">
       <stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
  const rad = (id, a, b, cx = "42%", cy = "32%", r = "75%") =>
    `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}">
       <stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></radialGradient>`;

  function eye(cx, cy, r) {
    return `<g class="cr-eye" data-eye="${cx},${cy}">
      <ellipse cx="${cx}" cy="${cy}" rx="${r}" ry="${r * 1.12}" fill="#fff"/>
      <circle class="cr-pupil" cx="${cx}" cy="${cy + r * .12}" r="${r * .58}" fill="#13202b"/>
      <circle cx="${cx - r * .24}" cy="${cy - r * .24}" r="${r * .24}" fill="#fff"/></g>`;
  }
  const smile = (cx, cy, w, c = "#13202b") =>
    `<path d="M${cx - w},${cy} q${w},${w * .7} ${2 * w},0" fill="none" stroke="${c}" stroke-width="4" stroke-linecap="round"/>`;
  const blush = (cx, cy, r = 10) => `<ellipse cx="${cx}" cy="${cy}" rx="${r}" ry="${r * .55}" fill="#ff6e6e" opacity=".3"/>`;
  const shadow = (rx = 70) => `<ellipse class="cr-shadow" cx="120" cy="214" rx="${rx}" ry="12" fill="#00121c" opacity=".26"/>`;

  // --- shared decorations driven by params -----------------------------------
  const horns = (n, pts, c) => pts.slice(0, n).map(([x, y, dx, dy]) =>
    `<path d="M${x},${y} l${dx},${dy} l6,4 Z" fill="${c}"/>`).join("");
  const platesRow = (pts, c) => pts.map(([x, y, h]) =>
    `<path d="M${x - 10},${y} Q${x},${y - h} ${x + 10},${y} Z" fill="${c}"/>`).join("");
  const spikesRow = (pts, c) => pts.map(([x, y, dx, dy]) =>
    `<path d="M${x},${y} l${dx},${dy} l4,5 Z" fill="${c}"/>`).join("");

  // ======================= BODY PLANS =======================================
  const PLANS = {
    // bipedal theropod — stands on two legs, small arms, big head, long tail
    biped(c, col, u) {
      const tailLong = c.tail !== "short";
      const tail = tailLong
        ? `<path d="M96,168 Q40,172 20,150 Q46,160 92,150 Z" fill="url(#g${u})"/>`
        : `<path d="M100,168 Q70,176 56,160 Q76,166 98,156 Z" fill="url(#g${u})"/>`;
      const crest = c.crest ? `<path d="M150,54 Q168,40 182,52 Q166,56 156,70 Z" fill="${col.accent}"/>` : "";
      const horn = horns(c.horns || 0, [[176, 70, 12, -12], [150, 56, 4, -16]], col.accent);
      return `${tail}
        <path d="M108,196 q-10,8 -22,6 q-2,-10 8,-16 Z" fill="${col.accent}"/>
        <path d="M140,196 q10,8 22,6 q2,-10 -8,-16 Z" fill="${col.accent}"/>
        <path d="M100,120 q-2,56 10,74 q14,6 28,0 q12,-20 10,-74 Z" fill="url(#g${u})"/>
        <path d="M112,150 q10,30 10,44 q-12,2 -18,-6 q-4,-20 2,-40 Z" fill="${col.belly}" opacity=".85"/>
        <ellipse cx="124" cy="110" rx="48" ry="44" fill="url(#g${u})"/>
        <path d="M100,96 q-14,-8 -18,-26 q18,6 26,18 Z" fill="url(#g${u})"/>
        ${crest}
        <path d="M150,96 q26,-6 40,8 q-4,16 -26,18 q-20,0 -22,-10 Z" fill="url(#g${u})"/>
        <path d="M172,110 q14,0 20,4 q-8,8 -20,6 Z" fill="${col.belly}"/>
        ${horn}
        ${eye(150, 100, 11)}${blush(140, 118)}${smile(160, 114, 8, col.accent)}
        <g stroke="${col.accent}" stroke-width="2" opacity=".4">${[86, 104, 122].map(y => `<path d="M108,${y} q16,6 30,0"/>`).join("")}</g>`;
    },

    // sauropod — four legs, huge round body, very long neck + small head
    longneck(c, col, u) {
      return `<path d="M70,180 Q30,180 18,150 Q44,164 78,158 Z" fill="url(#g${u})"/>
        ${[86, 116, 146, 172].map(x => `<rect x="${x}" y="168" width="18" height="34" rx="8" fill="${col.accent}"/>`).join("")}
        <ellipse cx="120" cy="150" rx="74" ry="46" fill="url(#g${u})"/>
        <ellipse cx="120" cy="164" rx="52" ry="28" fill="${col.belly}" opacity=".8"/>
        <path d="M168,138 q22,-54 34,-74 q10,-14 20,-8 q6,6 -2,18 q-16,24 -30,72 Z" fill="url(#g${u})"/>
        <ellipse cx="206" cy="58" rx="20" ry="16" fill="url(#g${u})"/>
        <path d="M222,60 q10,-2 16,2 q-6,8 -16,6 Z" fill="${col.belly}"/>
        ${eye(210, 52, 8)}${smile(214, 62, 6, col.accent)}
        <g fill="${col.accent}" opacity=".5">${[120, 150, 180].map(x => `<circle cx="${x}" cy="124" r="4"/>`).join("")}</g>`;
    },

    // armoured ornithischian — low quadruped, back plates, tail spikes, horns
    armoured(c, col, u) {
      const plates = c.plates !== false
        ? platesRow([[86, 150, 34], [112, 142, 42], [140, 142, 42], [166, 150, 34]], col.accent) : "";
      const spikes = c.spikes !== false
        ? spikesRow([[36, 168, -16, -6], [30, 180, -16, 2]], col.accent) : "";
      const horn = horns(c.horns || 0, [[196, 150, 14, -10], [188, 140, 6, -14]], col.accent);
      return `<path d="M74,176 Q40,180 44,196 Q60,190 86,186 Z" fill="url(#g${u})"/>
        ${spikes}
        ${[78, 108, 150, 180].map(x => `<rect x="${x}" y="176" width="16" height="26" rx="7" fill="${col.accent}"/>`).join("")}
        ${plates}
        <path d="M58,168 Q120,128 196,160 Q198,184 120,190 Q54,186 58,168 Z" fill="url(#g${u})"/>
        <ellipse cx="120" cy="176" rx="56" ry="16" fill="${col.belly}" opacity=".7"/>
        <path d="M184,150 q26,0 32,14 q-8,14 -30,12 q-16,-2 -16,-14 Z" fill="url(#g${u})"/>
        ${horn}
        ${eye(196, 158, 8)}${smile(202, 170, 6, col.accent)}`;
    },

    // generic quadruped (herbivore) — base for many plans
    quadruped(c, col, u) {
      const horn = horns(c.horns || 0, [[196, 120, 14, -12], [186, 112, 6, -16]], col.accent);
      return `<path d="M64,160 Q34,160 26,138 Q48,150 72,146 Z" fill="url(#g${u})"/>
        ${[78, 104, 150, 176].map(x => `<rect x="${x}" y="156" width="16" height="42" rx="7" fill="${col.accent}"/>`).join("")}
        <ellipse cx="118" cy="140" rx="66" ry="40" fill="url(#g${u})"/>
        <ellipse cx="118" cy="154" rx="46" ry="22" fill="${col.belly}" opacity=".8"/>
        <path d="M172,122 q26,-6 40,8 q-2,18 -26,20 q-18,0 -20,-12 Z" fill="url(#g${u})"/>
        ${horn}${eye(196, 118, 9)}${blush(186, 134)}${smile(204, 132, 7, col.accent)}`;
    },

    // flyer — winged, small body, big wings
    flyer(c, col, u) {
      const crest = c.crest ? `<path d="M150,70 q22,-14 36,-6 q-14,8 -24,22 Z" fill="${col.accent}"/>` : "";
      return `<path d="M120,120 Q60,70 24,96 Q70,110 108,138 Z" fill="url(#g${u})" opacity=".92"/>
        <path d="M120,120 Q180,70 216,96 Q170,110 132,138 Z" fill="url(#g${u})" opacity=".92"/>
        <ellipse cx="120" cy="140" rx="30" ry="40" fill="url(#g${u})"/>
        <ellipse cx="120" cy="150" rx="18" ry="26" fill="${col.belly}" opacity=".85"/>
        <circle cx="120" cy="96" r="26" fill="url(#g${u})"/>
        <path d="M120,92 q24,-6 40,2 q-16,10 -40,8 Z" fill="url(#g${u})"/>
        ${crest}${eye(132, 90, 10)}${eye(108, 90, 10)}${smile(120, 104, 8, col.accent)}
        ${[150, 182].map(x => `<path d="M100,200 q10,10 20,0" fill="none"/>`).join("")}`;
    },

    // swimmer — streamlined marine reptile, flippers
    swimmer(c, col, u) {
      return `<path d="M70,150 Q120,120 196,146 q16,8 18,18 q-22,16 -146,8 Q56,168 70,150 Z" fill="url(#g${u})"/>
        <ellipse cx="120" cy="156" rx="60" ry="16" fill="${col.belly}" opacity=".7"/>
        <path d="M96,166 q-16,24 -8,40 q16,-6 22,-30 Z" fill="${col.accent}"/>
        <path d="M150,166 q16,24 8,40 q-16,-6 -22,-30 Z" fill="${col.accent}"/>
        <path d="M196,146 q22,-6 30,4 q-10,12 -30,14 Z" fill="url(#g${u})"/>
        ${eye(200, 146, 9)}${smile(206, 158, 6, col.accent)}`;
    },

    // arthropod/insect — segmented body, legs, antennae
    arthropod(c, col, u) {
      const legs = [66, 90, 150, 174].map((x, i) => `<path d="M${x},160 q${i % 2 ? 10 : -10},20 0,30" stroke="${col.accent}" stroke-width="5" fill="none" stroke-linecap="round"/>`).join("");
      return `${legs}
        <path d="M60,150 Q120,128 196,150 Q196,166 120,170 Q60,166 60,150 Z" fill="url(#g${u})"/>
        <g stroke="${col.accent}" stroke-width="2" opacity=".4">${[96, 118, 140, 162].map(x => `<path d="M${x},134 q0,18 0,32"/>`).join("")}</g>
        <circle cx="196" cy="150" r="18" fill="url(#g${u})"/>
        <path d="M206,138 q14,-18 24,-16 M206,142 q16,-10 26,-4" stroke="${col.accent}" stroke-width="3" fill="none" stroke-linecap="round"/>
        ${eye(200, 146, 7)}${eye(188, 150, 6)}`;
    },

    // early mammal — furry, rounded, little ears + snout
    mammal(c, col, u) {
      return `<path d="M96,170 q-24,6 -30,22 q16,2 30,-10 Z" fill="url(#g${u})"/>
        ${[92, 112, 140, 160].map(x => `<rect x="${x}" y="176" width="12" height="22" rx="6" fill="${col.accent}"/>`).join("")}
        <ellipse cx="124" cy="150" rx="58" ry="40" fill="url(#g${u})"/>
        <ellipse cx="124" cy="162" rx="40" ry="24" fill="${col.belly}"/>
        <circle cx="168" cy="120" r="30" fill="url(#g${u})"/>
        <path d="M150,96 q-4,-18 10,-20 q8,10 2,22 Z" fill="${col.accent}"/>
        <path d="M186,96 q4,-18 -10,-20 q-8,10 -2,22 Z" fill="${col.accent}"/>
        <path d="M186,122 q14,0 20,6 q-8,8 -20,6 Z" fill="${col.belly}"/>
        <circle cx="204" cy="126" r="4" fill="#3a2a1c"/>
        ${eye(176, 116, 9)}${blush(166, 132)}${smile(188, 130, 7, col.accent)}`;
    },
  };

  function build(cfg) {
    const c = Object.assign({ plan: "biped", size: 1, tail: "long", horns: 0 }, cfg);
    const col = Object.assign({ main: "#6cc24a", belly: "#eaf5c6", accent: "#3f8f45" }, c.colors || {});
    const u = "k" + UID++;
    const defs = (c.plan === "swimmer" || c.plan === "longneck")
      ? lin(`g${u}`, col.main, col.accent)
      : rad(`g${u}`, _lighten(col.main), col.accent);
    const plan = PLANS[c.plan] || PLANS.biped;
    const inner = plan(c, col, u);
    const sc = c.size && c.size !== 1 ? ` transform="translate(120 120) scale(${c.size}) translate(-120 -120)"` : "";
    return `<svg class="cr cr-${c.id || c.plan}" viewBox="0 0 240 240" role="img" aria-label="${c.name || c.plan}">
      <defs>${defs}</defs>${shadow(70 * (c.size || 1))}<g class="cr-body"${sc}>${inner}</g></svg>`;
  }

  function _lighten(hex) {
    const n = parseInt(hex.slice(1), 16);
    const r = Math.min(255, (n >> 16) + 50), g = Math.min(255, ((n >> 8) & 255) + 50), b = Math.min(255, (n & 255) + 50);
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  }

  global.CreatureTemplates = { build, PLANS: Object.keys(PLANS) };
})(window);
