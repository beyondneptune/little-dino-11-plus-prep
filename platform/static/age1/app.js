/* app.js — screen orchestration for the Age-1 slice. Presents only what the API
   serves; every question already passed the serve gate server-side. */
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion:reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const api = (u, o) => fetch(u, o).then(r => r.ok ? r.json() : Promise.reject(r));
  const content = $(".content");
  const screen = content && content.dataset.screen;

  // render a creature: Age-1 hand code kit if known, else the template kit (ages 2-3)
  function creatureFig(key, fig) {
    if (Creatures.byStation[key]) return Creatures.byStation[key]();
    if (fig && window.CreatureTemplates) return CreatureTemplates.build(Object.assign({ id: key }, fig));
    return Creatures.trilobite();
  }

  // ---- shared chrome: a11y toggles, sound prompt/mute, page portal ----------
  function chrome() {
    // one small ⚙ button that opens a tucked-away menu, so the controls never
    // sit on top of question/answer content (a safe zone on phones).
    const a = document.createElement("div"); a.className = "a11y";
    a.innerHTML = `<div class="a11y-menu" id="a11ymenu" hidden>
        <button class="icon-btn" id="mute" title="Sound">${Sound.on ? "🔊" : "🔈"}</button>
        <button class="icon-btn" id="font" title="Easy-read font">Aa</button>
        <button class="icon-btn" id="big" title="Bigger text">A+</button></div>
      <button class="icon-btn a11y-toggle" id="a11ybtn" title="Settings" aria-expanded="false">⚙</button>`;
    document.body.appendChild(a);
    if (localStorage.dys === "1") document.body.classList.add("dys");
    if (localStorage.big === "1") document.documentElement.style.fontSize = "20px";
    $("#a11ybtn").onclick = () => {
      const m = $("#a11ymenu"), open = m.hidden;
      m.hidden = !open; $("#a11ybtn").setAttribute("aria-expanded", String(open)); Sound.play("tap");
    };
    $("#mute").onclick = e => { const on = Sound.toggle(); e.target.textContent = on ? "🔊" : "🔈"; if (on) Sound.play("tap"); };
    $("#font").onclick = () => { document.body.classList.toggle("dys"); localStorage.dys = document.body.classList.contains("dys") ? "1" : "0"; };
    $("#big").onclick = () => { const big = document.documentElement.style.fontSize !== "20px"; document.documentElement.style.fontSize = big ? "20px" : "18px"; localStorage.big = big ? "1" : "0"; };
    // No blocking prompt: browsers need a user gesture to start audio, so enable
    // sound on the first tap (unless the parent muted it before) and say so briefly.
    if (localStorage.sound === undefined) {
      const enableOnce = () => {
        window.removeEventListener("pointerdown", enableOnce, true);
        Sound.enable(); const mb = $("#mute"); if (mb) mb.textContent = "🔊";
        setTimeout(() => toast("🔊 Sound on — tap ⚙ to change"), 250);
      };
      window.addEventListener("pointerdown", enableOnce, true);
    }
  }
  function go(url) {
    Sound.play("whoosh");
    const p = document.createElement("div");
    p.style.cssText = "position:fixed;inset:0;z-index:99;background:radial-gradient(circle,#7af0ea,#06243a);opacity:0";
    document.body.appendChild(p);
    if (reduce) { location.href = url; return; }
    p.animate([{ opacity: 0, clipPath: "circle(0% at 50% 50%)" }, { opacity: 1, clipPath: "circle(150% at 50% 50%)" }],
      { duration: 420, easing: "ease-in", fill: "forwards" }).onfinish = () => location.href = url;
  }
  function entry() {
    const p = document.createElement("div");
    p.style.cssText = "position:fixed;inset:0;z-index:99;background:radial-gradient(circle,#7af0ea,#06243a);pointer-events:none";
    document.body.appendChild(p);
    p.animate([{ clipPath: "circle(150% at 50% 50%)" }, { clipPath: "circle(0% at 50% 50%)" }],
      { duration: 460, easing: "ease-out", fill: "forwards" }).onfinish = () => p.remove();
  }

  function startScene() {
    const stage = $(".stage"); if (!stage) return;
    // each age renders through the config-driven theme engine (data-theme on content)
    const themeName = (content && content.dataset.theme) || "cambrian";
    const theme = window.Themes && (Themes[themeName] || Themes.cambrian);
    stage.insertAdjacentHTML("afterbegin", theme ? Scene.buildTheme(theme) : Scene.cambrian());
    const fx = document.createElement("canvas"); fx.id = "fx"; stage.appendChild(fx);
    if (theme) Scene.themeParticles(fx, theme); else Scene.particles(fx);
    Scene.parallax(stage);
  }

  // ---------------------------------------------------- HOME
  function initHome() {
    document.querySelectorAll(".player").forEach((pl, idx) => {
      const holder = pl.querySelector(".buddy-holder");
      holder.innerHTML = Creatures.buddy(pl.dataset.color);
      const d = +(localStorage["streak_" + pl.dataset.who] || 0);
      pl.querySelector(".streak").textContent = d ? `🔥 ${d}-day streak` : "⭐ New explorer";
      // the buddy waves and greets the child by name
      const name = pl.querySelector(".pname").textContent;
      const hi = document.createElement("div"); hi.className = "hello"; hi.textContent = `Hi, ${name}! 👋`;
      holder.appendChild(hi);
      if (!reduce) setTimeout(() => {
        hi.animate([{ opacity: 0, transform: "translate(-50%,6px) scale(.8)" },
          { opacity: 1, transform: "translate(-50%,0) scale(1)" }], { duration: 400, fill: "forwards" });
        const c = holder.querySelector(".cr"); if (c) Creatures.react(c, "happy");
      }, 300 + idx * 260);
      pl.addEventListener("click", e => { e.preventDefault(); Sound.play("tap"); go(`/map/${pl.dataset.who}`); });
    });
  }

  // ---------------------------------------------------- MAP
  function ring(done, total) {
    const r = 54, c = 2 * Math.PI * r, frac = total ? done / total : 0;
    return `<svg class="ring" viewBox="0 0 120 120"><circle cx="60" cy="60" r="${r}" fill="none"
        stroke="rgba(255,255,255,.35)" stroke-width="7"/><circle cx="60" cy="60" r="${r}" fill="none"
        stroke="#ffc24a" stroke-width="7" stroke-linecap="round" stroke-dasharray="${c}"
        stroke-dashoffset="${c * (1 - frac)}" transform="rotate(-90 60 60)"/></svg>`;
  }
  function initMap() {
    const host = $(".stations"); const who = content.dataset.who; const age = content.dataset.age || "1";
    const items = JSON.parse(host.dataset.stations);
    items.forEach(s => {
      const avail = s.served || s.fossil;                 // the Fossil Dig is always open
      const el = document.createElement(avail ? "a" : "div");
      el.className = "station" + (avail ? "" : " locked") + (s.next ? " next" : "") + (s.fossil ? " dig" : "");
      el.style.left = s.x + "%"; el.style.top = s.y + "%";
      const art = s.fossil ? fossilIcon() : creatureFig(s.cre, s.fig);
      const mist = avail ? "" : '<div class="mist"></div>';
      const sub = s.fossil ? "<small>⛏️ dig!</small>"
        : (s.total ? `<small>${s.done}/${s.total}</small>` : (s.served ? "" : "<small>💤 sleeping</small>"));
      el.innerHTML = `<div class="holder">${s.next ? '<div class="glowpulse"></div>' : ""}${mist}<div class="cr-slot">${art}</div>${s.served ? ring(s.done, s.total) : ""}</div>
        <span class="tag">${s.name}${sub}</span>`;
      if (!s.fossil) Rig.enhance(el.querySelector(".cr-slot"), s.cre);
      if (s.next) el.querySelector(".glowpulse").animate(
        [{ opacity: .1, transform: "scale(.9)" }, { opacity: .6, transform: "scale(1.15)" }, { opacity: .1, transform: "scale(.9)" }],
        { duration: 1600, iterations: Infinity });
      el.addEventListener("click", e => {
        e.preventDefault(); Sound.play("tap");
        if (s.fossil) go(`/dig/${who}/${age}`);
        else if (s.served) go(`/station/${who}/${s.cre}`);
        else toast(`${s.name} is still waking up — new puzzles coming soon!`);
      });
      host.appendChild(el);
      if (s.served) Creatures.liveIdle(el.querySelector(".cr"));
    });
  }
  function fossilIcon() {
    return `<svg class="cr" viewBox="0 0 240 240"><g class="cr-body">
      <ellipse cx="120" cy="200" rx="66" ry="12" fill="#00121c" opacity=".25"/>
      <path d="M60,150 Q120,90 180,150 Q180,186 120,196 Q60,186 60,150Z" fill="#caa86a"/>
      <circle cx="96" cy="140" r="12" fill="#6b4f2a"/><circle cx="144" cy="140" r="12" fill="#6b4f2a"/>
      <path d="M96,168 q24,16 48,0" stroke="#6b4f2a" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M86,120 l-16,-16 M154,120 l16,-16" stroke="#e7cf9a" stroke-width="7" stroke-linecap="round"/>
      </g></svg>`;
  }
  function toast(msg) {
    const t = document.createElement("div");
    t.className = "panel"; t.style.cssText = "position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:40;padding:12px 18px;font-weight:800;max-width:84vw;text-align:center;pointer-events:none";
    t.textContent = msg; document.body.appendChild(t);
    t.animate([{ opacity: 0, transform: "translate(-50%,10px)" }, { opacity: 1, transform: "translate(-50%,0)" }], { duration: 250 });
    setTimeout(() => { t.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 300 }).onfinish = () => t.remove(); }, 2200);
  }

  // ---------------------------------------------------- STATION
  function initStation() {
    const root = $("#station");
    const who = root.dataset.who, creature = root.dataset.creature;
    const age = root.dataset.age || "1";
    const topics = JSON.parse(root.dataset.topics);
    const kidName = root.dataset.name || "";
    const greet = (kidName ? kidName + "! " : "") + root.dataset.greet;
    let fig = null; try { fig = JSON.parse(root.dataset.fig || "{}"); } catch (e) {}
    const SESSION_N = 6;                 // questions per session == journey milestones
    let ti = 0, streak = 0, gotCard = null;
    const creatureSvg = () => creatureFig(creature, fig);

    // time-on-task heartbeat → parent dashboard (usage analytics only)
    let lastTick = Date.now();
    const sendTick = (useBeacon) => {
      if (document.hidden) { lastTick = Date.now(); return; }
      const secs = Math.round((Date.now() - lastTick) / 1000); lastTick = Date.now();
      const tid = topics[ti] && topics[ti].id;
      if (!tid || secs <= 0) return;
      const payload = JSON.stringify({ who, topic: tid, seconds: secs });
      if (useBeacon && navigator.sendBeacon)
        navigator.sendBeacon("/api/tick", new Blob([payload], { type: "application/json" }));
      else api("/api/tick", { method: "POST", headers: { "Content-Type": "application/json" }, body: payload }).catch(() => {});
    };
    const hb = setInterval(() => sendTick(false), 15000);
    window.addEventListener("pagehide", () => { clearInterval(hb); sendTick(true); });

    meet();
    function meet() {
      root.innerHTML = `<div class="meet"><div class="holder swimin">${creatureSvg()}</div>
        <div class="bubble" id="say"></div>
        <button class="btn big" id="start" style="opacity:0">Let's learn!</button></div>`;
      const h = $(".holder", root);
      Rig.enhance(h, creature);
      if (!reduce) h.animate([{ transform: "translateX(-60vw) rotate(-8deg)" }, { transform: "translateX(0) rotate(0)" }], { duration: 700, easing: "cubic-bezier(.2,.8,.3,1)" });
      typeOut($("#say"), greet, () => { const s = $("#start"); if (s) s.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, fill: "forwards" }); });
      $("#start").onclick = () => { Sound.play("tap"); learn(); };
    }
    function typeOut(el, text, done) {
      const svg = $(".meet .cr"); let i = 0;
      (function tick() {
        if (!el.isConnected) return;               // child moved on — stop safely
        el.textContent = text.slice(0, i);
        if (i < text.length) { if (text[i] !== " " && i % 2 === 0) Sound.play("blip"); i++; setTimeout(tick, 28); }
        else done && done();
      })();
      svg && Creatures.react(svg, "talk");
    }

    async function learn() {
      const topic = topics[ti];
      const data = await api(`/api/lesson/${topic.id}`);
      const cards = FX.lessonCards(data.markdown || data.html || "");
      // insert an interactive try-it for rounding
      if (topic.id === "MA-A05") cards.splice(1, 0, "__NUMLINE__");
      let ci = 0;
      const SAYS = ["Let's look at this!", "Here's how it works ✨", "Watch this one 👀",
        "Try it yourself!", "Nearly there!", "You've got this! 💪"];
      render();
      function render() {
        const dots = cards.map((_, k) => `<i class="${k === ci ? "on" : ""}"></i>`).join("");
        const last = ci === cards.length - 1;
        const say = cards[ci] === "__NUMLINE__" ? "Give it a go — drag the ball!" : SAYS[ci % SAYS.length];
        root.innerHTML = `<div class="cardwrap">
            <div class="teacher"><div class="learn-creature">${creatureSvg()}</div>
              <div class="tbubble">${say}</div></div>
            <div class="card-light learncard" id="card"></div></div>
          <div class="dots">${dots}</div>
          <div style="text-align:center;padding-bottom:16px">
            <button class="btn ${last ? "" : "teal"}" id="nxt">${last ? "Let's practise! 🎯" : "Next ▶"}</button></div>`;
        const card = $("#card");
        Rig.enhance($(".learn-creature"), creature);
        Creatures.react($(".learn-creature .cr"), "talk");
        if (cards[ci] === "__NUMLINE__") {
          card.innerHTML = `<div class="cardart">${FX.cardArt("nearest number line")}</div>
            <h3>Try it!</h3><p>Drag the ball to a number, then see which ten it is nearest.</p>`;
          const holder = document.createElement("div"); card.appendChild(holder);
          FX.numberLine(holder, { lo: 0, hi: 100, step: 10, start: 37 });
        } else {
          card.innerHTML = `<div class="cardart">${FX.cardArt(cards[ci])}</div><div class="md">${FX.md(cards[ci])}</div>`;
          card.animate([{ opacity: 0, transform: "translateY(16px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 300 });
        }
        $("#nxt").onclick = () => { Sound.play("tap"); if (last) return session(topic, 0, 0); ci++; render(); };
      }
    }

    async function session(topic, n, correct) {
      const total = SESSION_N;                         // one continuous journey per session
      if (n >= total) return endSession(topic, correct);
      // ramp difficulty across ALL served levels of the topic through the session
      const lvls = (topic.levels && topic.levels.length ? topic.levels : [1]);
      const level = lvls[Math.min(lvls.length - 1, Math.floor(n / total * lvls.length))];
      let q;
      try { q = await api(`/api/question?who=${who}&topic=${topic.id}&level=${level}`); }
      catch { root.innerHTML = `<div class="finish"><p class="panel" style="padding:18px">No puzzles are ready here yet.</p></div>`; return; }
      const frac = n / total;
      const pips = Array.from({ length: total }, (_, k) =>
        `<i class="pip ${k < n ? "hit" : ""}" style="left:${(k + .5) / total * 100}%">${k < n ? "★" : k + 1}</i>`).join("");
      root.innerHTML = `<div class="play">
        <div class="streakflame" title="Answer streak">🔥 <b>${streak}</b></div>
        <div class="journey"><div class="jtrack"></div>
          <div class="jfill" style="width:0%"></div>${pips}
          <span class="jflag">🏁</span>
          <div class="jwalker" style="left:0%">${creatureSvg()}</div></div>
        <div class="qwrap"><div class="creature-on">${creatureSvg()}</div>
          <div class="qbubble panel" style="padding:${q.nvr ? "12px 18px" : "16px 22px"}"><div class="stem">${q.nvr ? q.prompt : q.stem}</div></div>
          ${q.nvr && q.seq && q.seq.length
            ? `<div class="nvr-seq">${q.seq.map(s => `<div class="nvr-cell">${s}</div>`).join("")}<div class="nvr-cell q">?</div></div>`
            : ""}
          ${q.nvr
            ? `<div class="tiles nvr-opts">${q.options.map((s, i) => `<button class="tile nvr-opt" data-i="${i}"><span class="oplabel">${"ABCDE"[i]}</span>${s}</button>`).join("")}</div>`
            : topic.typed
            ? `<form class="typedform" id="tf"><input class="typed-input" id="ti" autocomplete="off"
                 enterkeyhint="done" placeholder="Type your answer…">
               <button type="submit" class="btn teal" id="checkbtn">Check ✓</button></form>`
            : `<div class="tiles">${q.options.map((o, i) => `<button class="tile" data-i="${i}">${o}</button>`).join("")}</div>`}
          <div class="feedback" id="fb" hidden></div>
          <div style="text-align:center"><button class="btn teal" id="next" hidden>Next ▶</button></div>
        </div></div>`;
      requestAnimationFrame(() => {
        $(".journey .jfill").style.width = (frac * 100) + "%";
        $(".journey .jwalker").style.left = (frac * 100) + "%";
      });
      Rig.enhance($(".qwrap .creature-on"), creature);
      const onScreen = $(".qwrap .cr");
      const stepWalker = (starred) => {
        const nf = (n + 1) / total * 100;
        const jw = $(".journey .jwalker"), jf = $(".journey .jfill");
        if (jw) jw.style.left = nf + "%"; if (jf) jf.style.width = nf + "%";
        if (starred) { const np = root.querySelectorAll(".journey .pip")[n]; if (np) { np.classList.add("hit"); np.textContent = "★"; } }
      };
      // shared result handling for both tap-the-tile and typed-answer modes
      function showResult(res, flashEl) {
        const fb = $("#fb"); fb.hidden = false;
        const sf = $(".streakflame");
        if (res.correct) {
          if (flashEl) flashEl.classList.add("correct");
          streak++; if (sf) sf.innerHTML = "🔥 <b>" + streak + "</b>";
          if (flashEl) FX.fly(flashEl, sf, "⭐"); Sound.play(streak % 3 === 0 ? "streak" : "correct");
          stepWalker(true); Creatures.react(onScreen, "happy"); FX.confetti(document.body);
          fb.className = "feedback good"; fb.innerHTML = "✔ Brilliant! " + (res.explanation || "");
          $("#next").hidden = false; $("#next").onclick = () => session(topic, n + 1, correct + 1);
        } else {
          if (flashEl) flashEl.classList.add("wrong");
          streak = 0; if (sf) sf.innerHTML = "🔥 <b>0</b>";
          Sound.play("wrong"); Creatures.react(onScreen, "wrong"); stepWalker(false);
          fb.className = "feedback try";
          fb.innerHTML = res.why_wrong ? res.why_wrong : (res.explanation || "Not quite — have another go.");
          $("#next").hidden = false; $("#next").textContent = "Try a similar one ▶";
          $("#next").onclick = () => session(topic, n + 1, correct);
        }
        requestAnimationFrame(() => { const nx = $("#next"); if (nx) nx.scrollIntoView({ block: "nearest" }); });
      }
      if (topic.typed) {
        const form = $("#tf"), input = $("#ti");
        form.onsubmit = async (e) => {
          e.preventDefault();
          if (input.disabled || !input.value.trim()) return;
          input.disabled = true; $("#checkbtn").disabled = true;
          const res = await api("/api/answer", { method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ who, topic: topic.id, qid: q.id, typed: input.value, count: true }) });
          input.classList.add(res.correct ? "ok" : "bad");
          showResult(res, null);
        };
        input.focus();
      } else {
        const tiles = root.querySelectorAll(".tile");
        tiles.forEach(b => b.onclick = async () => {
          tiles.forEach(x => x.disabled = true);
          const chosen = +b.dataset.i;
          const res = await api("/api/answer", { method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ who, topic: topic.id, qid: q.id, chosen, count: true }) });
          tiles[res.answer_index].classList.add("correct");
          showResult(res, b);
        });
      }
    }

    const STATE_CLASS = { "Not started": "st-none", "Learning": "st-learning", "Developing": "st-developing",
      "Secure": "st-secure", "Strong": "st-strong", "Mastered": "st-mastered" };
    async function endSession(topic, correct) {
      const res = await api("/api/master", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ who, topic: topic.id, creature }) });
      if (res.card) gotCard = res.card;
      const mastered = res.mastered;
      const head = correct >= 5 ? "Brilliant! 🎉" : correct >= 3 ? "Good work!" : "Keep practising!";
      const stars = correct >= 5 ? "⭐⭐⭐" : correct >= 3 ? "⭐⭐" : "⭐";
      const pill = `<div class="statepill ${STATE_CLASS[res.state] || "st-none"}">${mastered ? "🏆 " : ""}${res.state}${res.attempts ? " · " + res.pct + "%" : ""}</div>`;
      if (mastered) { Sound.play("streak"); FX.confetti(document.body); }
      root.innerHTML = `<div class="finish">
        <div class="holder" style="width:220px;height:220px">${creatureSvg()}</div>
        <div class="stars">${stars}</div>
        <h2 style="color:#fff;text-shadow:0 2px 10px #0006">${head}</h2>
        <p class="panel" style="padding:12px 18px">You got ${correct} out of ${SESSION_N} this time.</p>
        ${pill}
        <button class="btn big" id="cont">${ti + 1 < topics.length ? "Next topic ▶" : "Finish expedition"}</button></div>`;
      Creatures.react($(".finish .cr"), "happy");
      if (mastered) {
        const cr = $(".finish .cr"), st = $(".finish .stars");
        [0, 180, 360].forEach((d) => setTimeout(() => { Sound.play("bone"); FX.fly(cr, st, "🦴"); }, 250 + d));
      }
      $("#cont").onclick = () => { Sound.play("tap"); ti++; if (ti < topics.length) learn(); else finish(); };
    }
    function finish() {
      const card = gotCard ? `<p class="panel" style="padding:12px 16px">🦴 You earned a fact card — see it in the Museum!</p>` : "";
      root.innerHTML = `<div class="finish">
        <div class="holder" style="width:200px;height:200px">${Creatures.buddy("#59c08a")}</div>
        <h2 style="color:#fff;text-shadow:0 2px 10px #0006">Done for today! 🎉</h2>${card}
        <a class="btn big teal" id="back">Back to the map</a></div>`;
      FX.confetti(document.body); Creatures.react($(".finish .cr"), "happy");
      $("#back").onclick = () => go(`/map/${who}/${age}`);
    }
  }

  // ---------------------------------------------------- FOSSIL DIG
  // original "stone cast" fossil line-art revealed by brushing away sand
  function fossilArt(id) {
    const S = inner => `<svg viewBox="0 0 240 240" class="fossilsvg">${inner}</svg>`;
    if (id === "ammonite") {
      let spiral = "";
      for (let i = 0; i < 60; i++) { const a = i * .5, r = 6 + i * 1.7;
        const x = 120 + r * Math.cos(a), y = 120 + r * Math.sin(a);
        spiral += `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`; }
      const ribs = Array.from({ length: 16 }, (_, i) => { const a = i * .39, r = 10 + i * 6;
        return `<line x1="120" y1="120" x2="${(120 + r * Math.cos(a)).toFixed(1)}" y2="${(120 + r * Math.sin(a)).toFixed(1)}" stroke="#7c5a2a" stroke-width="2" opacity=".5"/>`; }).join("");
      return S(`<circle cx="120" cy="120" r="104" fill="#d9bd82"/><circle cx="120" cy="120" r="104" fill="none" stroke="#a9843f" stroke-width="4"/>
        ${ribs}<path d="${spiral}" fill="none" stroke="#5f4420" stroke-width="7" stroke-linecap="round"/>`);
    }
    if (id === "brachiopod") {
      const ridges = Array.from({ length: 11 }, (_, i) => { const x = 60 + i * 12;
        return `<path d="M120,66 Q${x},150 ${x},182" fill="none" stroke="#6f5126" stroke-width="3" opacity=".6"/>`; }).join("");
      return S(`<circle cx="120" cy="120" r="104" fill="#d9bd82"/><circle cx="120" cy="120" r="104" fill="none" stroke="#a9843f" stroke-width="4"/>
        <path d="M120,60 Q196,120 150,186 Q120,198 90,186 Q44,120 120,60 Z" fill="none" stroke="#5f4420" stroke-width="7"/>${ridges}
        <path d="M70,120 q50,22 100,0" fill="none" stroke="#5f4420" stroke-width="4" opacity=".7"/>`);
    }
    // trilobite cast
    const ribs = Array.from({ length: 7 }, (_, i) => { const y = 92 + i * 13;
      return `<path d="M150,${y} q-30,10 -58,2" fill="none" stroke="#5f4420" stroke-width="3" opacity=".6"/>
        <path d="M90,${y} q30,10 58,2" fill="none" stroke="#5f4420" stroke-width="3" opacity=".6"/>`; }).join("");
    return S(`<circle cx="120" cy="120" r="104" fill="#d9bd82"/><circle cx="120" cy="120" r="104" fill="none" stroke="#a9843f" stroke-width="4"/>
      <path d="M52,120 Q120,48 188,120 Q190,186 120,198 Q50,186 52,120 Z" fill="none" stroke="#5f4420" stroke-width="7"/>
      <path d="M98,70 Q120,60 142,70 Q150,120 142,188 Q120,198 98,188 Q90,120 98,70 Z" fill="none" stroke="#5f4420" stroke-width="5" opacity=".8"/>
      ${ribs}`);
  }

  function initDig() {
    const root = $("#dig");
    const who = root.dataset.who;
    const age = root.dataset.age || "1";
    const fossils = JSON.parse(root.dataset.fossils);
    start();
    function start() {
      const f = fossils[Math.floor(Math.random() * fossils.length)];
      root.innerHTML = `<div class="digwrap">
        <h2 class="digtitle">Brush away the sand to find a fossil! 🪨</h2>
        <div class="digsite"><div class="fossil">${fossilArt(f.id)}</div><canvas class="sand"></canvas></div>
        <div class="digdone" id="digdone" hidden></div></div>`;
      const site = $(".digsite"), cv = $(".sand", site), ctx = cv.getContext("2d");
      let done = false, digging = false;
      const paint = () => {
        const r = site.getBoundingClientRect(); cv.width = r.width; cv.height = r.height;
        ctx.globalCompositeOperation = "source-over";
        const g = ctx.createLinearGradient(0, 0, 0, cv.height);
        g.addColorStop(0, "#e7cf9a"); g.addColorStop(1, "#c8a86a");
        ctx.fillStyle = g; ctx.fillRect(0, 0, cv.width, cv.height);
        for (let i = 0; i < cv.width * cv.height / 800; i++) {
          ctx.fillStyle = Math.random() < .5 ? "#d8bd84" : "#b8975f";
          ctx.fillRect(Math.random() * cv.width, Math.random() * cv.height, 2, 2);
        }
      };
      paint(); const onResize = () => { if (!done) paint(); }; window.addEventListener("resize", onResize);
      const pt = e => { const r = cv.getBoundingClientRect(); const p = e.touches ? e.touches[0] : e;
        return [p.clientX - r.left, p.clientY - r.top]; };
      const brush = (x, y) => { ctx.globalCompositeOperation = "destination-out";
        ctx.beginPath(); ctx.arc(x, y, 28, 0, 7); ctx.fill(); };
      const cleared = () => { const d = ctx.getImageData(0, 0, cv.width, cv.height).data;
        let c = 0, n = 0; for (let i = 3; i < d.length; i += 80) { n++; if (d[i] < 25) c++; } return c / n; };
      cv.addEventListener("pointerdown", e => { digging = true; Sound.play("tap"); const [x, y] = pt(e); brush(x, y); });
      cv.addEventListener("pointermove", e => { if (!digging) return; const [x, y] = pt(e); brush(x, y); if (Math.random() < .12) Sound.play("blip"); });
      window.addEventListener("pointerup", () => { if (!digging) return; digging = false; if (!done && cleared() > .5) reveal(); });
      function reveal() {
        done = true; Sound.play("streak"); FX.confetti(document.body);
        cv.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 600, fill: "forwards" }).onfinish = () => cv.remove();
        api("/api/dig", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ who, fossil: f.id }) }).catch(() => {});
        const d = $("#digdone"); d.hidden = false;
        d.innerHTML = `<div class="card-light factcard"><h3>You dug up the ${f.name}! 🎉</h3><p>${f.fact}</p>
          <div class="digbtns"><button class="btn teal" id="again">Dig again ⛏️</button>
          <a class="btn" href="/museum/${who}/${age}">See the Museum 🦴</a></div></div>`;
        $("#again").onclick = () => { Sound.play("tap"); start(); };
      }
    }
  }

  // ---------------------------------------------------- MUSEUM
  function initMuseum() {
    const hall = $(".hall");
    const items = JSON.parse(hall.dataset.items);
    const fossils = JSON.parse(hall.dataset.fossils || "[]");
    items.forEach(it => {
      const ex = document.createElement("div");
      ex.className = "exhibit" + (it.earned ? " earned" : " locked");
      ex.innerHTML = `<div class="flip"><div class="face front">
          <div class="ex-cr cr-slot" data-cre="${it.key}"></div>
          <div class="plate">${it.name}<small>${it.subject}</small></div>
          ${it.earned ? '<span class="badge">🦴 tap me</span>' : `<span class="prog">💤 ${it.done}/${it.total} to unlock</span>`}
        </div><div class="face back"><h4>${it.name}</h4>
          <p>${it.earned ? it.fact : "Master this creature's topics to reveal its fossil fact."}</p>
          <span class="flipback">↩ back</span></div></div>`;
      hall.appendChild(ex);
      const slot = ex.querySelector(".cr-slot");
      slot.innerHTML = creatureFig(it.key, it.fig);
      Rig.enhance(slot, it.key);
      if (it.earned) {
        Creatures.liveIdle(slot.querySelector(".cr"));
        ex.querySelector(".flip").addEventListener("click", () => { Sound.play("tap"); ex.classList.toggle("flipped"); });
      }
    });
    if (fossils.length) {
      const sec = document.createElement("div"); sec.className = "fossilcase";
      sec.innerHTML = `<h3>🪨 Fossils you dug up</h3><div class="fcase-row">` +
        fossils.map(f => `<div class="fcard ${f.found ? "found" : "empty"}">
          <div class="fmini">${f.found ? fossilArt(f.id) : '<span class="qm">?</span>'}</div>
          <b>${f.found ? f.name : "Keep digging!"}</b>${f.found ? `<small>${f.fact}</small>` : ""}</div>`).join("") +
        `</div>`;
      hall.appendChild(sec);
    }
  }

  // ---------------------------------------------------- SCALING KIT (demo)
  function initKit() {
    const stage = $(".stage"), host = $(".kit");
    const theme = (window.Themes && Themes[host.dataset.theme]) || (window.Themes && Themes.jurassic);
    if (theme) {
      stage.insertAdjacentHTML("afterbegin", Scene.buildTheme(theme));
      const fx = document.createElement("canvas"); fx.id = "fx"; stage.appendChild(fx);
      Scene.themeParticles(fx, theme); Scene.parallax(stage);
    }
    JSON.parse(host.dataset.dinos).forEach(d => {
      const card = document.createElement("div"); card.className = "kit-card";
      card.innerHTML = `<div class="kit-cr">${CreatureTemplates.build(d)}</div>
        <div class="kit-name">${d.name}<small>${d.plan} plan</small></div>
        <p class="kit-blurb">${d.blurb}</p>`;
      host.appendChild(card);
      Creatures.liveIdle(card.querySelector(".cr"));
    });
  }

  // creatures watch the pointer everywhere
  document.addEventListener("pointermove", e => {
    document.querySelectorAll(".station:not(.locked) .cr, .meet .cr, .qwrap .cr, .player .cr, .kit-cr .cr")
      .forEach(s => Creatures.lookAt(s, e.clientX, e.clientY));
  });

  // ---------------------------------------------------- boot
  chrome();
  if (screen !== "parent" && screen !== "kit") startScene();   // kit builds its own themed scene
  entry();
  if (screen === "home") initHome();
  else if (screen === "map") initMap();
  else if (screen === "station") initStation();
  else if (screen === "dig") initDig();
  else if (screen === "museum") initMuseum();
  else if (screen === "kit") initKit();
  else if (screen === "lineup") document.querySelectorAll(".cr-slot").forEach(s => {
    s.innerHTML = (Creatures.byStation[s.dataset.cre] || Creatures.trilobite)();
    Rig.enhance(s, s.dataset.cre);
    Creatures.liveIdle(s.querySelector(".cr"));
  });
})();
