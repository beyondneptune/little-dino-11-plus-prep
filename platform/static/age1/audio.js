/* Sound — original synthesised cues via Web Audio (no audio files). Off until the
   child says yes; choice remembered; a mute button is always visible. */
(function (global) {
  let ctx = null, master = null;
  const S = { on: localStorage.sound === "1" };

  function ensure() {
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = 0.22; master.connect(ctx.destination);
  }
  function tone(freq, dur, type = "sine", when = 0, vol = 1, slideTo = null) {
    const o = ctx.createOscillator(), gn = ctx.createGain();
    o.type = type; o.frequency.setValueAtTime(freq, ctx.currentTime + when);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, ctx.currentTime + when + dur);
    gn.gain.setValueAtTime(0.0001, ctx.currentTime + when);
    gn.gain.exponentialRampToValueAtTime(vol, ctx.currentTime + when + 0.012);
    gn.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + when + dur);
    o.connect(gn); gn.connect(master); o.start(ctx.currentTime + when); o.stop(ctx.currentTime + when + dur + .02);
  }
  const sounds = {
    tap: () => tone(520, .08, "triangle", 0, .6),
    correct: () => { [660, 880, 1320].forEach((f, i) => tone(f, .18, "sine", i * .07, .7)); },
    wrong: () => { tone(300, .2, "sine", 0, .5, 180); },
    streak: () => { [660, 990, 1320, 1760].forEach((f, i) => tone(f, .16, "triangle", i * .06, .6)); },
    bone: () => { tone(880, .12, "square", 0, .4, 1200); tone(440, .14, "sine", .05, .4); },
    whoosh: () => { tone(200, .35, "sawtooth", 0, .25, 900); },
    blip: () => tone(420 + Math.random() * 120, .05, "square", 0, .35),
  };

  S.enable = function () { S.on = true; localStorage.sound = "1"; ensure();
    if (ctx.state === "suspended") ctx.resume(); };
  S.disable = function () { S.on = false; localStorage.sound = "0"; };
  S.toggle = function () { S.on ? S.disable() : S.enable(); return S.on; };
  S.play = function (name) {
    if (!S.on) return; ensure(); if (ctx.state === "suspended") ctx.resume();
    (sounds[name] || (() => {}))();
  };
  global.Sound = S;
})(window);
