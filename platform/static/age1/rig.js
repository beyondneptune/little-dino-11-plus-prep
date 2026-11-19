/* Art pipeline loader. A creature is rendered by the code kit (creatures.js)
   instantly, then ENHANCED from assets/art/<name>/ if the parent dropped art in:
     - rig.json {"parts":[...]}  -> layered SVG, fully rigged (idle/blink/sway + reactions)
     - rig.json {"image":"x.png"} -> single flat image, bob/squash/rotate fallback
   If no art is found, the code creature stays. See assets/art/README.md. */
(function (global) {
  const cache = {};
  const ANIM = { sway: "cr-antenna", blink: "cr-eye", shadow: "cr-shadow" };
  let manifest = null;

  async function fetchText(u) { const r = await fetch(u); return r.ok ? r.text() : ""; }

  async function hasArt(name) {
    if (!manifest) {
      try { manifest = await (await fetch("/art/manifest.json")).json(); }
      catch (e) { manifest = { creatures: [] }; }
    }
    return (manifest.creatures || []).includes(name);
  }

  async function loadRig(name) {
    if (name in cache) return cache[name];
    if (!(await hasArt(name))) { cache[name] = null; return null; }   // skip -> no 404s
    let rig = null;
    try {
      const r = await fetch(`/art/${name}/rig.json`);
      if (r.ok) {
        rig = await r.json();
        if (rig.parts) {
          await Promise.all(rig.parts.concat(rig.shadow ? [{ src: rig.shadow, _s: 1 }] : [])
            .map(async p => { if (p.src) p._svg = await fetchText(`/art/${name}/${p.src}`); }));
        }
      }
    } catch (e) { rig = null; }
    cache[name] = rig;
    return rig;
  }

  function composeParts(name, rig) {
    const inside = rig.parts.map(p => {
      const cls = ANIM[p.anim] || "";
      const tf = p.pivot ? ` style="transform-origin:${p.pivot[0]}px ${p.pivot[1]}px"` : "";
      return `<g class="${cls}"${tf}>${p._svg || ""}</g>`;
    }).join("");
    return `<svg class="cr cr-${name} cr-rigged" viewBox="${rig.viewBox || "0 0 240 240"}">
      ${rig._shadowSvg || ""}<g class="cr-body">${inside}</g></svg>`;
  }

  async function enhance(container, name) {
    if (!container) return;
    const rig = await loadRig(name);
    if (!rig) return;                                  // keep code creature
    if (rig.image) {
      container.innerHTML = `<img class="cr cr-img" alt="${name}" src="/art/${name}/${rig.image}">`;
    } else if (rig.parts) {
      // shadow is a plain layer outside the breathing body
      let shadowSvg = "";
      if (rig.shadow) shadowSvg = `<g>${await fetchText(`/art/${name}/${rig.shadow}`)}</g>`;
      rig._shadowSvg = shadowSvg;
      container.innerHTML = composeParts(name, rig);
    }
  }

  // render = instant code creature + async enhance from files
  function render(container, name) {
    if (!container) return;
    container.innerHTML = (global.Creatures.byStation[name] || global.Creatures.trilobite)();
    enhance(container, name);
  }

  global.Rig = { enhance, render, loadRig };
})(window);
