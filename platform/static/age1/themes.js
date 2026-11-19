/* Age Theme System — each age is DATA (palette, sky, declarative parallax layers,
   ambient particles, swimmers/flyers, sound set), not a hand-coded screen. A new
   age = one entry here; Scene.buildTheme(theme) + Scene.themeParticles(canvas,theme)
   render it. Weather is a simple named overlay (none/motes/snow/ash).

   This is the scaling spine for the other ages: drop in a palette + layer list and
   the whole backdrop comes up, with the creature-template kit supplying inhabitants. */
(function (global) {
  const Themes = {
    cambrian: {
      name: "Cambrian Seas",
      sky: "radial-gradient(120% 80% at 50% -10%, #39b7c0 0%, #157e97 38%, #0a4a63 70%, #06243a 100%)",
      palette: {
        spire: "#0b4258", reef: "#0e4f63", haze: "#0c5e78",
        ground1: "#e7cf9a", ground2: "#d7b878",
        flora: ["#49a86f", "#3f9a63", "#58c08a"], fgflora: "#06303c",
        coral: ["#ff8a5c", "#ffc24a", "#1c6f82"], ray: "#bdfffa", caustic: "#cffff8",
      },
      ambient: "bubbles", weather: "motes", swimmers: { kind: "fish", count: 4 },
      layers: [
        { t: "spires", depth: 0.10 }, { t: "rays", depth: 0.15 }, { t: "haze", depth: 0.30 },
        { t: "reef", depth: 0.55 }, { t: "caustics", depth: 0.65 },
        { t: "floor", depth: 0.80, flora: "kelp" }, { t: "foreground", depth: 1.15, flora: "kelp" },
      ],
      sounds: "sea",
    },

    jurassic: {
      name: "Jurassic Valley",
      sky: "radial-gradient(120% 85% at 50% -8%, #d8ecff 0%, #a9d9a6 34%, #67a86c 64%, #2f6b45 100%)",
      palette: {
        spire: "#49684f", reef: "#356b3e", haze: "#5a8a5f",
        ground1: "#cdb06a", ground2: "#a98f4e",
        flora: ["#3f8f45", "#2f7a3a", "#5fab5a"], fgflora: "#203f27",
        coral: ["#e0b24a", "#d98f4a", "#7a9a52"], ray: "#fff6c8", caustic: "#fff6c8",
      },
      ambient: "pollen", weather: "motes", swimmers: { kind: "flyer", count: 3 },
      layers: [
        { t: "spires", depth: 0.10 }, { t: "rays", depth: 0.15 }, { t: "haze", depth: 0.30 },
        { t: "reef", depth: 0.55 }, { t: "floor", depth: 0.80, flora: "ferns" },
        { t: "foreground", depth: 1.15, flora: "ferns" },
      ],
      sounds: "forest",
    },

    devonian: {
      name: "Devonian Seas (Age of Fishes)",
      sky: "radial-gradient(120% 80% at 50% -10%, #4fd0b6 0%, #1f8f86 36%, #0c5a5e 68%, #052e34 100%)",
      palette: {
        spire: "#0a3b40", reef: "#0d5a52", haze: "#117a66",
        ground1: "#d8caa0", ground2: "#b8a06a",
        flora: ["#2f9a7a", "#2a8f86", "#54b89a"], fgflora: "#06302c",
        coral: ["#e07a5c", "#e0b24a", "#1c7a72"], ray: "#bdfff0", caustic: "#d2fff2",
      },
      ambient: "bubbles", weather: "motes", swimmers: { kind: "fish", count: 5 },
      layers: [
        { t: "spires", depth: 0.10 }, { t: "rays", depth: 0.15 }, { t: "haze", depth: 0.30 },
        { t: "reef", depth: 0.55 }, { t: "caustics", depth: 0.65 },
        { t: "floor", depth: 0.80, flora: "kelp" }, { t: "foreground", depth: 1.15, flora: "kelp" },
      ],
      sounds: "sea",
    },

    carboniferous: {
      name: "Carboniferous Swamps",
      sky: "radial-gradient(120% 85% at 50% -8%, #cfe6c4 0%, #8fbf7a 34%, #4f7d47 64%, #22351f 100%)",
      palette: {
        spire: "#3a5234", reef: "#2c5a2e", haze: "#4a7342",
        ground1: "#8a7a44", ground2: "#6a5a30",
        flora: ["#2f7a3a", "#246630", "#4f9a46"], fgflora: "#16301a",
        coral: ["#b88a3a", "#9a7a2e", "#5f7a3a"], ray: "#eaffc8", caustic: "#eaffc8",
      },
      ambient: "pollen", weather: "motes", swimmers: { kind: "flyer", count: 4 },
      layers: [
        { t: "spires", depth: 0.10 }, { t: "rays", depth: 0.15 }, { t: "haze", depth: 0.30 },
        { t: "reef", depth: 0.55 }, { t: "floor", depth: 0.80, flora: "ferns" },
        { t: "foreground", depth: 1.15, flora: "ferns" },
      ],
      sounds: "forest",
    },
  };

  global.Themes = Themes;
})(window);
