/* Scene engine — layered parallax backgrounds + a light canvas particle system.
   Original art; transforms/opacity only; capped particles; respects reduced-motion. */
(function (global) {
  const reduce = () => window.matchMedia("(prefers-reduced-motion:reduce)").matches;

  // Cambrian Seas: 6 parallax layers injected as absolutely-positioned SVGs.
  function cambrian() {
    const L = (depth, svg) =>
      `<div class="parallax" data-depth="${depth}" style="z-index:${Math.round(depth * 10)}">${svg}</div>`;
    const ray = (x, w, o) => `<polygon points="${x},-40 ${x + w},-40 ${x + w * 1.6},900 ${x - w * .6},900" fill="#bdfffa" opacity="${o}"/>`;
    const kelp = (x, h, c) => `<path d="M${x},700 q-18,-${h * .4} 0,-${h * .7} q18,-${h * .3} 0,-${h}"
        fill="none" stroke="${c}" stroke-width="16" stroke-linecap="round"/>`;
    const coral = (x, y, s, c) => `<g transform="translate(${x},${y}) scale(${s})" fill="${c}">
        <path d="M0,0 q-10,-40 6,-66 q12,24 2,66 Z"/><path d="M14,0 q-4,-28 12,-48 q6,22 -4,48 Z"/>
        <path d="M-14,0 q-6,-24 6,-40 q6,18 -2,40 Z"/></g>`;
    // caustics: wavy light ripples that drift across the sand (CSS-animated)
    const causticLine = (y, o) => `<path d="M-120,${y} q60,-22 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0"
        fill="none" stroke="#cffff8" stroke-width="6" stroke-linecap="round" opacity="${o}"/>`;
    return `
      <div class="sky" style="background:
         radial-gradient(120% 80% at 50% -10%, #39b7c0 0%, #157e97 38%, #0a4a63 70%, #06243a 100%)"></div>
      ${L(0.1, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMax slice">
         <path d="M0,560 L120,340 L250,560 Z" fill="#0b4258" opacity=".5"/>
         <path d="M980,560 L1085,320 L1190,560 Z" fill="#0b4258" opacity=".45"/></svg>`)}
      ${L(0.15, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice">${ray(240, 150, .10)}${ray(760, 120, .08)}</svg>`)}
      ${L(0.3, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice">
         <ellipse cx="200" cy="300" rx="260" ry="200" fill="#0c5e78" opacity=".45"/>
         <ellipse cx="1000" cy="360" rx="300" ry="220" fill="#0c5e78" opacity=".4"/></svg>`)}
      ${L(0.55, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMax slice">
         <path d="M0,640 Q300,560 600,620 T1200,600 L1200,800 L0,800 Z" fill="#0e4f63"/>
         ${coral(180, 648, 1.4, "#1c6f82")}${coral(980, 636, 1.6, "#1c6f82")}</svg>`)}
      ${L(0.65, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMax slice">
         <g class="caust">${causticLine(688, .16)}${causticLine(724, .12)}${causticLine(760, .09)}</g></svg>`)}
      ${L(0.8, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMax slice">
         <path d="M0,720 Q300,650 600,710 T1200,700 L1200,800 L0,800 Z" fill="#e7cf9a"/>
         <path d="M0,752 Q300,700 600,744 T1200,738 L1200,800 L0,800 Z" fill="#d7b878"/>
         ${coral(120, 726, 1.6, "#ff8a5c")}${coral(430, 736, 1.1, "#ffc24a")}${coral(1040, 724, 1.5, "#ff8a5c")}
         ${kelp(300, 150, "#49a86f")}${kelp(820, 180, "#3f9a63")}${kelp(880, 140, "#58c08a")}</svg>`)}
      ${L(1.15, `<svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMax slice" style="filter:blur(2.2px)">
         ${kelp(54, 300, "#06303c")}${kelp(96, 250, "#073340")}${kelp(1150, 320, "#06303c")}${kelp(1112, 258, "#073340")}</svg>`)}
      <div class="vignette"></div>`;
  }

  // canvas particles: rising bubbles, drifting motes, drifting fish silhouettes
  let raf = 0;
  function particles(canvas) {
    const ctx = canvas.getContext("2d");
    let W, H, dpr;
    const resize = () => {
      dpr = Math.min(2, window.devicePixelRatio || 1);
      W = canvas.width = canvas.clientWidth * dpr;
      H = canvas.height = canvas.clientHeight * dpr;
    };
    resize(); window.addEventListener("resize", resize);
    const rnd = (a, b) => a + Math.random() * (b - a);
    const bubbles = Array.from({ length: 46 }, () => ({
      x: rnd(0, 1), y: rnd(0, 1), r: rnd(2, 7), s: rnd(.0004, .0014), w: rnd(.2, 1) }));
    const motes = Array.from({ length: 40 }, () => ({ x: rnd(0, 1), y: rnd(0, 1), r: rnd(.6, 2), s: rnd(.00005, .0002) }));
    const fish = Array.from({ length: 4 }, (_, i) => ({ x: rnd(0, 1), y: rnd(.2, .6), s: rnd(.0002, .0005) * (i % 2 ? 1 : -1), sc: rnd(.7, 1.3) }));
    if (reduce()) { drawStatic(); return () => {}; }
    let t = 0;
    function frame() {
      t += 1; ctx.clearRect(0, 0, W, H);
      ctx.globalCompositeOperation = "lighter";
      motes.forEach(m => { m.y -= m.s; if (m.y < 0) m.y = 1;
        ctx.fillStyle = "rgba(180,255,250,.5)"; ctx.beginPath();
        ctx.arc(m.x * W, m.y * H, m.r * dpr, 0, 7); ctx.fill(); });
      bubbles.forEach(b => { b.y -= b.s; b.x += Math.sin((t * .01) + b.y * 10) * .0006 * b.w;
        if (b.y < -.02) { b.y = 1.02; b.x = Math.random(); }
        const x = b.x * W, y = b.y * H, r = b.r * dpr;
        ctx.strokeStyle = "rgba(210,255,252,.5)"; ctx.lineWidth = 1.2 * dpr;
        ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.stroke();
        ctx.fillStyle = "rgba(255,255,255,.35)"; ctx.beginPath();
        ctx.arc(x - r * .3, y - r * .3, r * .3, 0, 7); ctx.fill(); });
      ctx.globalCompositeOperation = "source-over";
      fish.forEach(f => { f.x += f.s; if (f.x > 1.1) f.x = -.1; if (f.x < -.1) f.x = 1.1;
        drawFish(ctx, f.x * W, f.y * H, 26 * dpr * f.sc, f.s > 0); });
      raf = requestAnimationFrame(frame);
    }
    function drawFish(c, x, y, s, right) {
      c.save(); c.translate(x, y); c.scale(right ? 1 : -1, 1); c.globalAlpha = .18;
      c.fillStyle = "#05303f"; c.beginPath();
      c.ellipse(0, 0, s, s * .4, 0, 0, 7); c.fill();
      c.beginPath(); c.moveTo(-s, 0); c.lineTo(-s * 1.5, -s * .5); c.lineTo(-s * 1.5, s * .5); c.closePath(); c.fill();
      c.restore();
    }
    function drawStatic() { ctx.clearRect(0, 0, W, H);
      bubbles.slice(0, 20).forEach(b => { ctx.strokeStyle = "rgba(210,255,252,.4)";
        ctx.beginPath(); ctx.arc(b.x * W, b.y * H, b.r * dpr, 0, 7); ctx.stroke(); }); }
    frame();
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); };
  }

  function parallax(root) {
    if (reduce()) return;
    const layers = [...root.querySelectorAll(".parallax")];
    let tx = 0, ty = 0, cx = 0, cy = 0;
    root.addEventListener("pointermove", e => {
      const r = root.getBoundingClientRect();
      tx = ((e.clientX - r.left) / r.width - .5);
      ty = ((e.clientY - r.top) / r.height - .5);
    });
    (function loop() {
      cx += (tx - cx) * .06; cy += (ty - cy) * .06;
      layers.forEach(l => { const d = +l.dataset.depth || .3;
        l.style.transform = `translate(${-cx * d * 60}px,${-cy * d * 36}px) scale(${1 + d * .06})`; });
      requestAnimationFrame(loop);
    })();
  }

  // ===================== config-driven theme engine ==========================
  // Declarative layer primitives read a palette, so a new age is just a Theme.
  const L = (depth, svg) => `<div class="parallax" data-depth="${depth}" style="z-index:${Math.round(depth * 10)}">${svg}</div>`;
  const SVG = (inner, aspect = "xMidYMax slice") => `<svg viewBox="0 0 1200 800" preserveAspectRatio="${aspect}">${inner}</svg>`;
  const coralShape = (x, y, s, c) => `<g transform="translate(${x},${y}) scale(${s})" fill="${c}">
      <path d="M0,0 q-10,-40 6,-66 q12,24 2,66 Z"/><path d="M14,0 q-4,-28 12,-48 q6,22 -4,48 Z"/>
      <path d="M-14,0 q-6,-24 6,-40 q6,18 -2,40 Z"/></g>`;
  const kelp = (x, h, c) => `<path d="M${x},700 q-18,-${h * .4} 0,-${h * .7} q18,-${h * .3} 0,-${h}" fill="none" stroke="${c}" stroke-width="16" stroke-linecap="round"/>`;
  const fern = (x, h, c) => {
    const frond = (a) => `<path d="M${x},720 q${a * 20},-${h * .5} ${a * 40},-${h}" fill="none" stroke="${c}" stroke-width="7" stroke-linecap="round"/>`;
    return `${frond(-1)}${frond(-.4)}${frond(.2)}${frond(.9)}<rect x="${x - 3}" y="${720 - h}" width="6" height="${h}" fill="${c}"/>`;
  };
  const flora = (kind, x, h, c) => kind === "ferns" || kind === "fern" ? fern(x, h, c) : kelp(x, h, c);

  const PRIM = {
    spires: (p) => SVG(`<path d="M0,560 L120,340 L250,560 Z" fill="${p.spire}" opacity=".5"/>
        <path d="M980,560 L1085,320 L1190,560 Z" fill="${p.spire}" opacity=".45"/>`),
    rays: (p) => { const ray = (x, w, o) => `<polygon points="${x},-40 ${x + w},-40 ${x + w * 1.6},900 ${x - w * .6},900" fill="${p.ray}" opacity="${o}"/>`;
      return SVG(ray(240, 150, .10) + ray(760, 120, .08), "xMidYMid slice"); },
    haze: (p) => SVG(`<ellipse cx="200" cy="300" rx="260" ry="200" fill="${p.haze}" opacity=".42"/>
        <ellipse cx="1000" cy="360" rx="300" ry="220" fill="${p.haze}" opacity=".36"/>`, "xMidYMid slice"),
    reef: (p) => SVG(`<path d="M0,640 Q300,560 600,620 T1200,600 L1200,800 L0,800 Z" fill="${p.reef}"/>
        ${coralShape(180, 648, 1.4, p.coral[2])}${coralShape(980, 636, 1.6, p.coral[2])}`),
    caustics: (p) => { const line = (y, o) => `<path d="M-120,${y} q60,-22 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0" fill="none" stroke="${p.caustic}" stroke-width="6" stroke-linecap="round" opacity="${o}"/>`;
      return SVG(`<g class="caust">${line(688, .16)}${line(724, .12)}${line(760, .09)}</g>`); },
    floor: (p, o) => SVG(`<path d="M0,720 Q300,650 600,710 T1200,700 L1200,800 L0,800 Z" fill="${p.ground1}"/>
        <path d="M0,752 Q300,700 600,744 T1200,738 L1200,800 L0,800 Z" fill="${p.ground2}"/>
        ${coralShape(120, 726, 1.6, p.coral[0])}${coralShape(430, 736, 1.1, p.coral[1])}${coralShape(1040, 724, 1.5, p.coral[0])}
        ${flora(o.flora, 300, 150, p.flora[0])}${flora(o.flora, 820, 180, p.flora[1])}${flora(o.flora, 880, 140, p.flora[2])}`),
    foreground: (p, o) => SVG(`${flora(o.flora, 54, 300, p.fgflora)}${flora(o.flora, 96, 250, p.fgflora)}
        ${flora(o.flora, 1150, 320, p.fgflora)}${flora(o.flora, 1112, 258, p.fgflora)}`, "xMidYMax slice")
      .replace("<svg ", '<svg style="filter:blur(2.2px)" '),
  };

  function buildTheme(theme) {
    const p = theme.palette;
    const layers = theme.layers.map(ly => L(ly.depth, (PRIM[ly.t] || (() => ""))(p, ly))).join("");
    return `<div class="sky" style="background:${theme.sky}"></div>${layers}<div class="vignette"></div>`;
  }

  // ambient particles + drifting swimmers/flyers, both palette/kind-driven
  let traf = 0;
  function themeParticles(canvas, theme) {
    const ctx = canvas.getContext("2d");
    const pollen = theme.ambient === "pollen";
    let W, H, dpr;
    const resize = () => { dpr = Math.min(2, window.devicePixelRatio || 1);
      W = canvas.width = canvas.clientWidth * dpr; H = canvas.height = canvas.clientHeight * dpr; };
    resize(); window.addEventListener("resize", resize);
    const rnd = (a, b) => a + Math.random() * (b - a);
    const motes = Array.from({ length: pollen ? 60 : 46 }, () => ({ x: rnd(0, 1), y: rnd(0, 1), r: rnd(1, pollen ? 3 : 7), s: rnd(.0003, .0012), w: rnd(.2, 1) }));
    const sw = Array.from({ length: (theme.swimmers && theme.swimmers.count) || 3 },
      (_, i) => ({ x: rnd(0, 1), y: rnd(.18, .55), s: rnd(.0002, .0005) * (i % 2 ? 1 : -1), sc: rnd(.7, 1.3) }));
    if (reduce()) return () => {};
    let t = 0;
    const fly = theme.swimmers && theme.swimmers.kind === "flyer";
    function frame() {
      t++; ctx.clearRect(0, 0, W, H); ctx.globalCompositeOperation = "lighter";
      motes.forEach(m => { m.y -= m.s; m.x += Math.sin(t * .01 + m.y * 9) * .0004 * m.w; if (m.y < -.02) { m.y = 1.02; m.x = Math.random(); }
        ctx.fillStyle = pollen ? "rgba(255,240,180,.6)" : "rgba(200,255,250,.5)";
        ctx.beginPath(); ctx.arc(m.x * W, m.y * H, m.r * dpr, 0, 7); ctx.fill(); });
      ctx.globalCompositeOperation = "source-over";
      sw.forEach(f => { f.x += f.s; if (f.x > 1.1) f.x = -.1; if (f.x < -.1) f.x = 1.1;
        (fly ? drawFlyer : drawFish)(ctx, f.x * W, f.y * H, 24 * dpr * f.sc, f.s > 0); });
      traf = requestAnimationFrame(frame);
    }
    function drawFish(c, x, y, s, right) { c.save(); c.translate(x, y); c.scale(right ? 1 : -1, 1); c.globalAlpha = .18; c.fillStyle = "#05303f";
      c.beginPath(); c.ellipse(0, 0, s, s * .4, 0, 0, 7); c.fill();
      c.beginPath(); c.moveTo(-s, 0); c.lineTo(-s * 1.5, -s * .5); c.lineTo(-s * 1.5, s * .5); c.closePath(); c.fill(); c.restore(); }
    function drawFlyer(c, x, y, s, right) { c.save(); c.translate(x, y); c.scale(right ? 1 : -1, 1); c.globalAlpha = .2; c.fillStyle = "#2a3a22";
      const wing = Math.sin(t * .15) * s * .4;
      c.beginPath(); c.moveTo(0, 0); c.quadraticCurveTo(-s, -wing - s * .3, -s * 1.6, 0); c.quadraticCurveTo(-s, s * .2, 0, 0);
      c.moveTo(0, 0); c.quadraticCurveTo(s, -wing - s * .3, s * 1.6, 0); c.quadraticCurveTo(s, s * .2, 0, 0); c.fill();
      c.beginPath(); c.ellipse(0, 0, s * .25, s * .5, 0, 0, 7); c.fill(); c.restore(); }
    frame();
    return () => { cancelAnimationFrame(traf); window.removeEventListener("resize", resize); };
  }

  global.Scene = { cambrian, particles, parallax, buildTheme, themeParticles };
})(window);
