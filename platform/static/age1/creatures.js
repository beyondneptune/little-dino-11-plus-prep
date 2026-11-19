/* Creature Kit v2 — original, scientifically-recognisable, characterful SVG
   creatures. Each is layered + rigged (idle breathe/blink/sway, pointer-follow
   eyes, happy/kind-wrong/talk reactions). Big expressive faces, shading via
   gradients, rim light, textures/patterns, unique palette + personality. */
(function (global) {
  let UID = 0;
  const rad = (id, stops, cx = "42%", cy = "32%", r = "75%") =>
    `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}">${stops}</radialGradient>`;
  const lin = (id, stops, x2 = 0, y2 = 1) =>
    `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}">${stops}</linearGradient>`;

  // a big friendly eye with white, pupil (pointer-trackable), highlights, lid
  function eye(cx, cy, r) {
    return `<g class="cr-eye" data-eye="${cx},${cy}">
      <ellipse cx="${cx}" cy="${cy}" rx="${r}" ry="${r * 1.15}" fill="#fff"/>
      <ellipse cx="${cx}" cy="${cy}" rx="${r}" ry="${r * 1.15}" fill="none" stroke="#0e2630" stroke-opacity=".12" stroke-width="2"/>
      <circle class="cr-pupil" cx="${cx}" cy="${cy + r * .12}" r="${r * .6}" fill="#13202b"/>
      <circle cx="${cx - r * .24}" cy="${cy - r * .24}" r="${r * .24}" fill="#fff"/>
      <circle cx="${cx + r * .28}" cy="${cy + r * .22}" r="${r * .1}" fill="#ffffffbb"/></g>`;
  }
  const blush = (cx, cy, r = 11) => `<ellipse cx="${cx}" cy="${cy}" rx="${r}" ry="${r * .55}" fill="#ff6e6e" opacity=".32"/>`;
  const smile = (cx, cy, w, c = "#13202b") => `<path d="M${cx - w},${cy} q${w},${w * .7} ${2 * w},0" fill="none" stroke="${c}" stroke-width="4" stroke-linecap="round"/>`;
  const shadow = () => `<ellipse class="cr-shadow" cx="120" cy="214" rx="74" ry="13" fill="#00121c" opacity=".26"/>`;
  const wrap = (kind, defs, body) =>
    `<svg class="cr cr-${kind}" viewBox="0 0 240 240" role="img" aria-label="${kind}">
      <defs>${defs}</defs>${shadow()}<g class="cr-body">${body}</g></svg>`;

  const Creatures = {
    // 3-lobed, segmented, recognisably a trilobite
    trilobite() {
      const u = "t" + UID++;
      const defs =
        rad(`shell${u}`, `<stop offset="0" stop-color="#8be6ea"/><stop offset=".5" stop-color="#43b2c6"/><stop offset="1" stop-color="#1b6f8d"/>`) +
        lin(`axis${u}`, `<stop offset="0" stop-color="#d4f8f6"/><stop offset="1" stop-color="#63c6cf"/>`);
      // pleural segments: ribs crossing the side lobes
      const ribs = [];
      for (let i = 0; i < 6; i++) {
        const y = 96 + i * 13;
        ribs.push(`<path d="M${150 - i * 2},${y} q-30,10 -58,2" fill="none" stroke="#12627d" stroke-width="3.5" opacity=".55" stroke-linecap="round"/>
          <path d="M${90 + i * 2},${y} q30,10 58,2" fill="none" stroke="#12627d" stroke-width="3.5" opacity=".55" stroke-linecap="round"/>`);
      }
      const body = `
        <path d="M46,118 Q120,50 194,118 Q196,176 120,190 Q44,176 46,118 Z" fill="url(#shell${u})"/>
        <path d="M46,118 Q120,50 194,118" fill="none" stroke="#e3fcff" stroke-width="5" opacity=".65" stroke-linecap="round"/>
        <path d="M120,66 L120,186" stroke="#0f5f79" stroke-width="2" opacity=".35"/>
        ${ribs.join("")}
        <path d="M98,70 Q120,60 142,70 Q150,120 142,182 Q120,192 98,182 Q90,120 98,70 Z" fill="url(#axis${u})" opacity=".95"/>
        <g stroke="#2f93a3" stroke-width="2" opacity=".4">${[92, 108, 124, 140, 156, 172].map(y => `<line x1="102" y1="${y}" x2="138" y2="${y}"/>`).join("")}</g>
        <g class="cr-antenna" style="transform-origin:120px 70px">
          <path d="M106,74 Q88,38 72,42" fill="none" stroke="#12627d" stroke-width="4" stroke-linecap="round"/>
          <path d="M134,74 Q152,38 168,42" fill="none" stroke="#12627d" stroke-width="4" stroke-linecap="round"/></g>
        ${eye(100, 102, 19)}${eye(140, 102, 19)}
        ${blush(82, 128)}${blush(158, 128)}${smile(110, 140, 10)}`;
      return wrap("trilobite", defs, body);
    },

    // lateral flaps, front grasping appendages, ringed mouth, stalked eye — cheeky
    anomalocaris() {
      const u = "a" + UID++;
      const defs = lin(`an${u}`, `<stop offset="0" stop-color="#ffbb86"/><stop offset="1" stop-color="#e3632f"/>`);
      const flaps = [];
      for (let i = 0; i < 5; i++) { const x = 92 + i * 20;
        flaps.push(`<path d="M${x},150 q10,22 -2,34 q-14,-6 -14,-30 Z" fill="#f0824e" opacity=".85"/>
          <path d="M${x},96 q10,-22 -2,-34 q-14,6 -14,30 Z" fill="#f0824e" opacity=".7"/>`); }
      const body = `
        ${flaps.join("")}
        <path d="M60,122 Q120,92 188,118 q16,8 20,22 q-20,18 -148,10 Q48,146 60,122 Z" fill="url(#an${u})"/>
        <path d="M60,124 q-6,0 -10,2" fill="none"/>
        <path d="M188,120 q22,-8 34,2 q-14,10 -34,14 Z" fill="#e3632f"/>
        <g stroke="#b64a22" stroke-width="2.5" opacity=".4">${[96, 118, 140, 162].map(x => `<path d="M${x},112 q0,16 0,30"/>`).join("")}</g>
        <path d="M60,128 q-26,14 -28,38 q18,0 30,-24 M60,138 q-22,20 -20,42 q16,-4 24,-28"
          fill="none" stroke="#e3632f" stroke-width="8" stroke-linecap="round"/>
        <g transform="translate(40,160)"><circle r="12" fill="none" stroke="#b64a22" stroke-width="5"/>
          <g stroke="#b64a22" stroke-width="3">${Array.from({length:8},(_,i)=>`<line x1="0" y1="0" x2="${9*Math.cos(i*0.785)}" y2="${9*Math.sin(i*0.785)}"/>`).join("")}</g></g>
        <g transform="translate(96,86)"><line x1="0" y1="18" x2="0" y2="0" stroke="#e3632f" stroke-width="5"/>${eye(0, -6, 13)}</g>
        ${blush(118, 136)}${smile(104, 128, 11, "#7c3015")}`;
      return wrap("anomalocaris", defs, body);
    },

    // five mushroom eyes + long frontal nozzle — comically surprised
    opabinia() {
      const u = "o" + UID++;
      const defs = lin(`op${u}`, `<stop offset="0" stop-color="#86d6d4"/><stop offset="1" stop-color="#2f8f8c"/>`);
      const flaps = [92, 112, 132, 152].map(x => `<path d="M${x},150 q8,16 -2,26 q-12,-4 -10,-24 Z" fill="#43a3a0" opacity=".8"/>`).join("");
      const eyes = [[92, 86], [108, 78], [124, 76], [140, 80], [156, 88]].map(([x, y]) =>
        `<line x1="${x}" y1="${y + 18}" x2="${x}" y2="${y}" stroke="#2f8f8c" stroke-width="4"/>${eye(x, y, 9)}`).join("");
      const body = `
        ${flaps}
        <path d="M70,128 Q120,100 176,126 q14,10 14,22 q-26,14 -120,8 Q58,150 70,128 Z" fill="url(#op${u})"/>
        <g stroke="#277673" stroke-width="2" opacity=".4">${[90,110,130,150].map(x=>`<path d="M${x},116 q0,16 0,28"/>`).join("")}</g>
        <path class="cr-nozzle" d="M70,132 q-30,6 -42,30 q-6,14 6,16 q14,2 16,-14 q4,-18 20,-22 Z"
          fill="#2f8f8c" style="transform-origin:70px 140px"/>
        <circle cx="34" cy="176" r="7" fill="#1f6a67"/>
        ${eyes}${blush(150,138)}<ellipse cx="120" cy="146" rx="9" ry="7" fill="#123" opacity=".8"/>`;
      return wrap("opabinia", defs, body);
    },

    // ribbon body, notochord line + zig-zag myomeres — gentle, curious
    pikaia() {
      const u = "p" + UID++;
      const defs = lin(`pk${u}`, `<stop offset="0" stop-color="#9ad97b"/><stop offset="1" stop-color="#4fae63"/>`);
      const myo = [];
      for (let x = 56; x <= 176; x += 14) myo.push(`<path d="M${x},118 l5,14 l-5,14" fill="none" stroke="#3b8a4b" stroke-width="2.5" opacity=".55"/>`);
      const body = `
        <path d="M40,138 Q74,104 108,124 Q146,146 182,116 Q206,100 210,126 Q204,150 180,150 Q140,150 108,150 Q74,168 40,138 Z" fill="url(#pk${u})"/>
        <path d="M44,138 Q78,118 110,134 Q148,150 180,128" fill="none" stroke="#2c6b38" stroke-width="3" opacity=".6"/>
        ${myo.join("")}
        ${eye(190, 120, 12)}${blush(170, 138)}${smile(176, 142, 8, "#2c6b38")}`;
      return wrap("pikaia", defs, body);
    },

    // tube body, paired dorsal spines, tentacle legs — quirky, friendly
    hallucigenia() {
      const u = "h" + UID++;
      const defs = lin(`ha${u}`, `<stop offset="0" stop-color="#f3cd6e"/><stop offset="1" stop-color="#d49a36"/>`);
      const spines = [64, 84, 104, 124, 144].map(x => `<path d="M${x},136 l-5,-44" stroke="#b97e2a" stroke-width="5" stroke-linecap="round"/><path d="M${x+6},136 l5,-44" stroke="#b97e2a" stroke-width="5" stroke-linecap="round"/>`).join("");
      const legs = [60, 78, 96, 114, 132, 150, 168].map((x, i) => `<path class="cr-leg" d="M${x},150 q${i%2?6:-6},22 0,34" fill="none" stroke="#c98f30" stroke-width="5" stroke-linecap="round"/>`).join("");
      const body = `${spines}${legs}
        <path d="M46,148 Q120,128 196,148 Q196,160 120,164 Q46,160 46,148 Z" fill="url(#ha${u})"/>
        <circle cx="196" cy="148" r="15" fill="url(#ha${u})"/>
        ${eye(198, 144, 7)}<ellipse cx="196" cy="158" rx="6" ry="4" fill="#8a5e1e"/>
        ${eye(176, 146, 6)}`;
      return wrap("hallucigenia", defs, body);
    },

    // oval scaly armour + two rows of spikes — proud little tank
    wiwaxia() {
      const u = "w" + UID++;
      const defs = rad(`wi${u}`, `<stop offset="0" stop-color="#c7dd86"/><stop offset="1" stop-color="#889e4a"/>`);
      const spikesBack = [74, 96, 118, 140, 162].map(x => `<path d="M${x},126 l-3,-42 l6,0 Z" fill="#6f853c"/>`).join("");
      const spikesTop = [86, 108, 130, 152].map(x => `<path d="M${x},116 l-3,-28 l6,0 Z" fill="#7e944a"/>`).join("");
      const scales = [];
      for (let r = 0; r < 3; r++) for (let x = 66 + (r%2)*12; x < 180; x += 24)
        scales.push(`<path d="M${x-12},${150+r*8} q12,-13 24,0" fill="#a9c05f" stroke="#6f853c" stroke-width="1.4"/>`);
      const body = `${spikesBack}${spikesTop}
        <path d="M50,152 Q120,120 190,152 Q190,170 120,174 Q50,170 50,152 Z" fill="url(#wi${u})"/>
        ${scales.join("")}
        ${eye(176, 150, 8)}${smile(160, 158, 7, "#3f4a1e")}`;
      return wrap("wiwaxia", defs, body);
    },

    buddy(color = "#59c08a") {
      const u = "b" + UID++;
      const defs = rad(`bd${u}`, `<stop offset="0" stop-color="#ffffff" stop-opacity=".6"/><stop offset=".3" stop-color="${color}"/><stop offset="1" stop-color="#2f8f63"/>`);
      const body = `
        <path class="cr-tail" d="M66,168 q-34,2 -46,-22 q28,-4 48,12 Z" fill="${color}" style="transform-origin:66px 168px"/>
        <ellipse cx="128" cy="150" rx="58" ry="52" fill="url(#bd${u})"/>
        <ellipse cx="128" cy="168" rx="36" ry="30" fill="#fbe9c7"/>
        <path d="M94,80 q6,-22 20,-8 M162,80 q-6,-22 -20,-8" fill="#2f8f63"/>
        <circle cx="124" cy="104" r="48" fill="url(#bd${u})"/>
        ${eye(108, 100, 17)}${eye(148, 100, 17)}
        ${blush(92, 118)}${blush(162, 118)}${smile(118, 116, 10, "#1f6b48")}
        <ellipse cx="104" cy="196" rx="16" ry="12" fill="#2f8f63"/><ellipse cx="152" cy="196" rx="16" ry="12" fill="#2f8f63"/>`;
      return wrap("buddy", defs, body);
    },
  };

  Creatures.byStation = {
    trilobite: Creatures.trilobite, anomalocaris: Creatures.anomalocaris,
    pikaia: Creatures.pikaia, opabinia: Creatures.opabinia,
    hallucigenia: Creatures.hallucigenia, wiwaxia: Creatures.wiwaxia,
  };
  Creatures.order = ["trilobite", "anomalocaris", "opabinia", "pikaia", "hallucigenia", "wiwaxia"];

  Creatures.lookAt = function (svg, cx, cy) {
    if (!svg) return;
    const r = svg.getBoundingClientRect();
    const dx = Math.max(-1, Math.min(1, (cx - (r.left + r.width / 2)) / (r.width / 2)));
    const dy = Math.max(-1, Math.min(1, (cy - (r.top + r.height / 2)) / (r.height / 2)));
    svg.querySelectorAll(".cr-pupil").forEach(p => p.style.transform = `translate(${dx * 4}px,${dy * 4}px)`);
  };
  Creatures.react = function (svg, kind) {
    if (!svg) return;
    const body = svg.querySelector(".cr-body"); if (!body) return;
    if (window.matchMedia("(prefers-reduced-motion:reduce)").matches) return;
    const anims = {
      happy: [[{ transform: "translateY(0) rotate(0)" }, { transform: "translateY(-28px) rotate(-7deg)" },
        { transform: "translateY(0) rotate(0)" }, { transform: "translateY(-13px) rotate(5deg)" },
        { transform: "translateY(0)" }], { duration: 950, easing: "ease-out" }],
      wrong: [[{ transform: "rotate(0)" }, { transform: "rotate(-6deg) translateY(5px)" },
        { transform: "rotate(4deg)" }, { transform: "rotate(0)" }], { duration: 700 }],
      talk: [[{ transform: "translateY(0)" }, { transform: "translateY(-5px)" }, { transform: "translateY(0)" }],
        { duration: 480, iterations: 3 }],
      hop: [[{ transform: "translateY(0)" }, { transform: "translateY(-10px)" }, { transform: "translateY(0)" }], { duration: 600 }],
    };
    const a = anims[kind]; if (a) body.animate(a[0], a[1]);
  };
  // random gentle idle behaviours (a hop or wiggle) so creatures feel alive
  Creatures.liveIdle = function (svg) {
    if (!svg || window.matchMedia("(prefers-reduced-motion:reduce)").matches) return;
    const tick = () => { if (!svg.isConnected) return;
      Creatures.react(svg, Math.random() < .5 ? "hop" : "talk");
      setTimeout(tick, 4000 + Math.random() * 5000); };
    setTimeout(tick, 2500 + Math.random() * 4000);
  };

  global.Creatures = Creatures;
})(window);
