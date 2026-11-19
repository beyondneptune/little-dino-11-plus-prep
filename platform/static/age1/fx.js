/* FX — markdown renderer (fixes raw-markdown bug), confetti, count-up, and the
   interactive number-line manipulative for rounding. No third-party libraries. */
(function (global) {
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  function md(src) {
    const lines = src.replace(/\r/g, "").split("\n");
    let html = "", inList = false, para = [];
    const inline = t => esc(t)
      .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
      .replace(/(^|[^*])\*(?!\*)([^*]+?)\*/g, "$1<i>$2</i>")
      .replace(/`([^`]+)`/g, "<code>$1</code>");
    const flushP = () => { if (para.length) { html += `<p>${inline(para.join(" "))}</p>`; para = []; } };
    const flushL = () => { if (inList) { html += "</ol>"; inList = false; } };
    for (let raw of lines) {
      const line = raw.trim();
      if (!line) { flushP(); flushL(); continue; }
      let m;
      if ((m = line.match(/^#\s+(.*)/))) { flushP(); flushL(); html += `<h3>${inline(m[1])}</h3>`; }
      else if ((m = line.match(/^##\s+(.*)/))) { flushP(); flushL(); html += `<h4>${inline(m[1])}</h4>`; }
      else if ((m = line.match(/^\d+\.\s+(.*)/))) { flushP(); if (!inList) { html += "<ol>"; inList = true; } html += `<li>${inline(m[1])}</li>`; }
      else { flushL(); para.push(line); }     // join wrapped lines into one paragraph
    }
    flushP(); flushL();
    return html;
  }

  // a flying emoji token from a source element to a target (reward feel)
  function fly(from, to, glyph) {
    if (!from || !to || window.matchMedia("(prefers-reduced-motion:reduce)").matches) return;
    const a = from.getBoundingClientRect(), b = to.getBoundingClientRect();
    const el = document.createElement("div");
    el.textContent = glyph;
    el.style.cssText = `position:fixed;left:${a.left + a.width / 2}px;top:${a.top}px;font-size:28px;
      z-index:60;pointer-events:none;transform:translate(-50%,-50%)`;
    document.body.appendChild(el);
    el.animate([{ transform: "translate(-50%,-50%) scale(1.4)", opacity: 1 },
      { transform: `translate(${b.left + b.width / 2 - a.left - a.width / 2}px,${b.top - a.top}px) scale(.5)`, opacity: .2 }],
      { duration: 700, easing: "cubic-bezier(.3,.7,.3,1)" }).onfinish = () => el.remove();
  }

  // an original, theme-matched illustration for a learn card, chosen from the
  // card's text so NO card is text-only. Returns an inline SVG banner.
  function cardArt(src) {
    const t = (src || "").toLowerCase();
    const svg = inner => `<svg class="cardart-svg" viewBox="0 0 340 104" preserveAspectRatio="xMidYMid meet" aria-hidden="true">${inner}</svg>`;
    const label = (x, s) => `<text x="${x}" y="92" text-anchor="middle" font-family="Fredoka" font-size="15" fill="#10232b">${s}</text>`;
    if (/round|nearest/.test(t)) {
      // a number line 0..10 with a ball at 7 and an arrow rounding up to 10
      let ticks = "";
      for (let i = 0; i <= 10; i++) { const x = 24 + i * 29;
        ticks += `<line x1="${x}" y1="44" x2="${x}" y2="58" stroke="#2e7a77" stroke-width="3"/>`;
        if (i % 5 === 0) ticks += label(x, i);
      }
      const bx = 24 + 7 * 29, tx = 24 + 10 * 29;
      return svg(`<line x1="24" y1="51" x2="314" y2="51" stroke="#9fd0cf" stroke-width="7" stroke-linecap="round"/>
        ${ticks}<path d="M${bx},30 Q${(bx + tx) / 2},6 ${tx},30" fill="none" stroke="#ff8a3d" stroke-width="4" stroke-dasharray="5 5"/>
        <polygon points="${tx},33 ${tx - 8},22 ${tx + 6},20" fill="#ff8a3d"/>
        <circle cx="${bx}" cy="51" r="11" fill="#ff8a3d" stroke="#fff" stroke-width="3"/>`);
    }
    if (/ones digit|tens|units|place value|digit/.test(t)) {
      // three place-value blocks
      const block = (x, c, n, cap) => `<rect x="${x}" y="26" width="58" height="46" rx="10" fill="${c}"/>
        <text x="${x + 29}" y="57" text-anchor="middle" font-family="Fredoka" font-size="26" fill="#fff">${n}</text>${label(x + 29, cap)}`;
      return svg(`${block(70, "#2fb6c4", "4", "hundreds")}${block(140, "#36c26a", "7", "tens")}${block(210, "#ff8a5c", "2", "ones")}`);
    }
    if (/times|multipl|product|array/.test(t)) {
      let dots = "";
      for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++)
        dots += `<circle cx="${118 + c * 30}" cy="${22 + r * 24}" r="9" fill="#2fb6c4"/>`;
      return svg(`${dots}<text x="60" y="56" text-anchor="middle" font-family="Fredoka" font-size="20" fill="#115e5b">3 × 4</text>`);
    }
    if (/divid|share|group|halve/.test(t)) {
      const basket = x => `<path d="M${x},40 h44 l-6,34 h-32 Z" fill="#e7cf9a" stroke="#c7a561" stroke-width="2"/>
        <circle cx="${x + 14}" cy="54" r="6" fill="#ff8a5c"/><circle cx="${x + 30}" cy="54" r="6" fill="#ff8a5c"/><circle cx="${x + 22}" cy="66" r="6" fill="#ff8a5c"/>`;
      return svg(`${basket(70)}${basket(150)}${basket(230)}${label(170, "shared equally")}`);
    }
    if (/add|plus|sum|total|subtract|minus|take away|differ/.test(t)) {
      const sign = /subtract|minus|take away|differ/.test(t) ? "−" : "+";
      const row = (x, n, c) => Array.from({ length: n }, (_, i) =>
        `<circle cx="${x + i * 22}" cy="50" r="9" fill="${c}"/>`).join("");
      return svg(`${row(40, 3, "#2fb6c4")}<text x="128" y="58" font-family="Fredoka" font-size="30" fill="#115e5b">${sign}</text>${row(150, 2, "#ff8a5c")}<text x="228" y="58" font-family="Fredoka" font-size="30" fill="#115e5b">=</text>${row(254, 5, "#36c26a")}`);
    }
    // default: three friendly sea shells (always on theme, never text-only)
    const shell = (x, c) => `<g transform="translate(${x},64)"><path d="M0,0 a30,30 0 0 1 60,0 Z" fill="${c}"/>
      <path d="M30,0 L18,-26 M30,0 L30,-30 M30,0 L42,-26" stroke="#fff" stroke-width="2" opacity=".7"/></g>`;
    return svg(`${shell(70, "#2fb6c4")}${shell(140, "#ff8a5c")}${shell(210, "#36c26a")}`);
  }

  // split a lesson markdown into short teaching cards (one idea each)
  function lessonCards(src) {
    const blocks = src.split(/\n(?=##?\s)/).map(s => s.trim()).filter(Boolean);
    const cards = [];
    blocks.forEach(b => {
      if (/^#\s/.test(b)) return;                    // skip the bare H1 title block
      const head = (b.match(/^#+\s+(.*)/) || [])[1] || "";
      if (/worked example/i.test(head)) {
        // one card per numbered example
        const items = b.split(/\n(?=\d+\.\s)/).filter(x => /^\d+\./.test(x.trim()));
        items.forEach(it => cards.push("## Worked example\n" + it.trim().replace(/^\d+\.\s*/, "")));
      } else {
        cards.push(b);
      }
    });
    return cards;
  }

  function confetti(host) {
    if (window.matchMedia("(prefers-reduced-motion:reduce)").matches) return;
    const colors = ["#ff8a3d", "#ffc24a", "#36c26a", "#2fb6c4", "#ff7a7a", "#7af0ea"];
    for (let i = 0; i < 70; i++) {
      const p = document.createElement("div");
      const size = 6 + Math.random() * 8;
      p.style.cssText = `position:fixed;left:${50 + (Math.random() - .5) * 30}%;top:40%;
        width:${size}px;height:${size * .6}px;background:${colors[i % colors.length]};
        border-radius:2px;pointer-events:none;z-index:50`;
      host.appendChild(p);
      p.animate([
        { transform: `translate(0,0) rotate(0)`, opacity: 1 },
        { transform: `translate(${(Math.random() - .5) * 500}px,${300 + Math.random() * 300}px) rotate(${Math.random() * 720}deg)`, opacity: 0 }
      ], { duration: 1200 + Math.random() * 800, easing: "cubic-bezier(.2,.6,.3,1)" })
        .onfinish = () => p.remove();
    }
  }

  function countUp(el, to, ms = 600) {
    const start = performance.now();
    (function step(t) {
      const k = Math.min(1, (t - start) / ms);
      el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(step);
    })(start);
  }

  // Interactive number line: drag the ball; it snaps to the nearer ten and tells you.
  function numberLine(host, { lo = 0, hi = 100, step = 10, start = 37 }) {
    const W = 600, H = 150, pad = 40, y = 90;
    const px = v => pad + (v - lo) / (hi - lo) * (W - 2 * pad);
    const ticks = [];
    for (let v = lo; v <= hi; v += step) ticks.push(`
      <line x1="${px(v)}" y1="${y - 12}" x2="${px(v)}" y2="${y + 12}" stroke="#2e7a77" stroke-width="3"/>
      <text x="${px(v)}" y="${y + 36}" text-anchor="middle" font-family="Fredoka" font-size="18" fill="#10232b">${v}</text>`);
    host.innerHTML = `<div class="numline card-light" style="padding:14px">
      <div class="nl-say" style="font-family:Fredoka;font-size:1.25rem;color:#115e5b;text-align:center;min-height:1.5em">
        Drag the glowing ball to <b>${start}</b> on the line…</div>
      <svg viewBox="0 0 ${W} ${H}">
        <line x1="${pad}" y1="${y}" x2="${W - pad}" y2="${y}" stroke="#9fd0cf" stroke-width="6" stroke-linecap="round"/>
        ${ticks.join("")}
        <circle class="nl-ball" cx="${px(start)}" cy="${y}" r="18" fill="#ff8a3d" stroke="#fff" stroke-width="4"/>
      </svg></div>`;
    const svg = host.querySelector("svg"), ball = host.querySelector(".nl-ball"), say = host.querySelector(".nl-say");
    const nearest = v => Math.round(v / step) * step;
    let done = false, onDone = null;
    const toVal = clientX => {
      const r = svg.getBoundingClientRect();
      const sx = (clientX - r.left) / r.width * W;
      return Math.max(lo, Math.min(hi, lo + (sx - pad) / (W - 2 * pad) * (hi - lo)));
    };
    const move = e => {
      const v = toVal((e.touches ? e.touches[0] : e).clientX);
      ball.setAttribute("cx", px(v));
    };
    const up = e => {
      window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up);
      const v = toVal((e.changedTouches ? e.changedTouches[0] : e).clientX);
      const n = nearest(v);
      ball.style.transition = "cx .25s ease-out";
      ball.setAttribute("cx", px(n));
      ball.setAttribute("fill", "#36c26a");
      say.innerHTML = `The nearest ${step} to that spot is <b>${n}</b>. Nice!`;
      global.Sound && Sound.play("correct");
      if (!done) { done = true; onDone && onDone(n); }
    };
    ball.style.cursor = "grab";
    ball.addEventListener("pointerdown", e => {
      e.preventDefault(); global.Sound && Sound.play("tap");
      window.addEventListener("pointermove", move); window.addEventListener("pointerup", up);
    });
    return { whenTried(cb) { onDone = cb; } };
  }

  global.FX = { md, lessonCards, confetti, countUp, numberLine, fly, cardArt };
})(window);
