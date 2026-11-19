#!/usr/bin/env python3
"""
Fact-checked biology + fact cards for every Dino Ages creature (brief rule 5,
Phase 1b decision 3: two sources each, museum/scientific — not Wikipedia).

Every creature was checked on 2026-11-14 against TWO independent reputable
sources (recorded as source_1 / source_2), drawn from museum and scientific
pages: Natural History Museum (incl. its Dino Directory), Smithsonian / Ocean
Portal, American Museum of Natural History, Field Museum, Royal Ontario Museum
(Burgess Shale), UC Museum of Paleontology, Australian Museum, Florida Museum,
La Brea Tar Pits, Encyclopaedia Britannica, National Geographic, and peer-
reviewed papers (Nature / PMC). For each creature the geological period was
confirmed to match its assigned age and the is_dinosaur flag was confirmed.
fact_card.verified stays FALSE until the parent approves (see the printable
approval sheet, scripts/approval_sheet.py -> content/creature_approval_sheet.md).

THINLY-SOURCED (flagged for the parent): Pulmonoscorpius, Petrolacosaurus and
Pholiderpeton are obscure Carboniferous animals with no dedicated kid-friendly
museum page; their sources are peer-reviewed papers / general museum pages.
The parent may accept these or swap the creature for a better-documented one.

Keyed by the creature name used in build_taxonomy.CREATURES.
"""

FACTS = {
    # ---- Age 1: Cambrian Seas ----
    "Trilobite": dict(
        group="Marine arthropod (class Trilobita)",
        diet="Varied — predators, scavengers and filter-feeders",
        size="Mostly 3-10 cm (largest ~70 cm)",
        lived="Cambrian to Permian (first appeared ~521 Ma)",
        fact="Trilobites could roll up into a ball to protect themselves, just like a modern pill bug.",
        source_1="https://www.amnh.org/research/paleontology/collections/fossil-invertebrate-collection/trilobite-website/introduction-to-trilobites",
        source_2="https://ucmp.berkeley.edu/arthropoda/trilobita/trilobitafr.html"),
    "Anomalocaris": dict(
        group="Radiodont (an early stem-arthropod)",
        diet="Carnivore — hunted soft-bodied prey",
        size="~34-38 cm (body)",
        lived="Cambrian (~520-499 Ma)",
        fact="Its eyes had over 24,000 lenses each — among the sharpest eyes of its time.",
        source_1="https://www.amnh.org/explore/news-blogs/apex-predator-soft-diet",
        source_2="https://ucmp.berkeley.edu/cambrian/burgessnew.html"),
    "Opabinia": dict(
        group="Stem-arthropod (Dinocaridida)",
        diet="Grabbed small soft food from the seafloor with its nozzle",
        size="4-7 cm",
        lived="Middle Cambrian (~505 Ma)",
        fact="Opabinia had five eyes and a long clawed nozzle instead of jaws.",
        source_1="https://burgess-shale.rom.on.ca/fossils/opabinia-regalis/",
        source_2="https://www.britannica.com/animal/Opabinia"),
    "Hallucigenia": dict(
        group="Lobopodian (a velvet-worm relative)",
        diet="Likely a scavenger/predator",
        size="0.5-5.5 cm",
        lived="Cambrian (~505 Ma)",
        fact="Scientists first reconstructed it upside-down and back-to-front — it took decades to get it right.",
        source_1="https://burgess-shale.rom.on.ca/fossils/hallucigenia-sparsa/",
        source_2="https://www.nationalgeographic.com/science/article/when-hallucinations-walked-the-world"),
    "Pikaia": dict(
        group="Early chordate (relative of backboned animals)",
        diet="Tiny organic particles filtered from the water",
        size="~3.8-5 cm",
        lived="Middle Cambrian (~505 Ma)",
        fact="This little swimmer is one of the earliest known relatives of all backboned animals — including us.",
        source_1="https://burgess-shale.rom.on.ca/fossils/pikaia-gracilens/",
        source_2="https://www.britannica.com/animal/Pikaia"),
    "Wiwaxia": dict(
        group="Early lophotrochozoan (possible stem-mollusc)",
        diet="Scraped bacteria and microbes off the seafloor",
        size="up to ~5 cm",
        lived="Cambrian (~520-505 Ma)",
        fact="Wiwaxia wore two rows of long spines on its back like armour.",
        source_1="https://burgess-shale.rom.on.ca/fossils/wiwaxia-corrugata/",
        source_2="https://www.britannica.com/animal/Wiwaxia"),

    # ---- Age 2: Devonian (Age of Fishes) ----
    "Dunkleosteus": dict(
        group="Placoderm (armoured fish, arthrodire)",
        diet="Apex carnivore — ate armoured fish",
        size="~3.4 m (up to ~4 m)",
        lived="Late Devonian (~382-358 Ma)",
        fact="Instead of teeth it had self-sharpening bony blades and one of the strongest bites of any fish.",
        source_1="https://ocean.si.edu/through-time/bony-beginnings-rise-vertebrate-innovation-devonian",
        source_2="https://www.nhm.ac.uk/discover/prehistoric-fish-timeline.html"),
    "Tiktaalik": dict(
        group="Lobe-finned fish (a fish-to-tetrapod 'fishapod')",
        diet="Carnivore of shallow waters",
        size="~1.25-2.75 m",
        lived="Late Devonian (~375 Ma)",
        fact="It had a flat head and fins with wrist-like joints — a bridge between swimming fish and land animals.",
        source_1="https://ucmp.berkeley.edu/about/ucmpnews/09_05/tiktaalik09_05.php",
        source_2="https://www.nationalgeographic.com/animals/article/140113-tiktaalik-pelvis-fossil-discovery-science"),
    "Cladoselache": dict(
        group="Early cartilaginous fish (shark relative)",
        diet="Fast predator of small fish",
        size="up to ~2 m",
        lived="Late Devonian (~359 Ma)",
        fact="Its fossils are so well preserved that scientists can see its last meals still inside its stomach.",
        source_1="https://www.britannica.com/animal/Cladoselache",
        source_2="https://www.nhm.ac.uk/discover/shark-evolution-a-450-million-year-timeline.html"),
    "Eusthenopteron": dict(
        group="Lobe-finned fish (Sarcopterygii)",
        diet="Carnivore — ate smaller fish",
        size="~1.5-2.1 m",
        lived="Late Devonian (~384-372 Ma)",
        fact="The bones in its fins line up like the arm and leg bones in your own body.",
        source_1="https://www.britannica.com/animal/Eusthenopteron",
        source_2="https://naturalhistory.si.edu/visit/virtual-tour/current-exhibits/deep-time-virtual-tour-fossil-list"),
    "Hyneria": dict(
        group="Lobe-finned fish (Sarcopterygii)",
        diet="Predatory carnivore",
        size="~2.5-3 m",
        lived="Late Devonian (Famennian)",
        fact="This river hunter had fangs over 5 cm long and sensed prey in murky water.",
        source_1="https://www.pbs.org/wgbh/evolution/library/04/3/text_pop/l_043_42.html",
        source_2="https://ucmp.berkeley.edu/devonian/devonian.php"),
    "Stethacanthus": dict(
        group="Early cartilaginous fish (shark relative)",
        diet="Carnivore of small sea animals",
        size="~1.5-3 m",
        lived="Late Devonian into the Carboniferous",
        fact="Males had a strange anvil-shaped, spiky dorsal fin shaped a bit like an ironing board.",
        source_1="https://www.fieldmuseum.org/blog/four-fossil-sharks-are-cooler-megalodon",
        source_2="https://ocean.si.edu/through-time/carboniferous-sharks"),

    # ---- Age 3: Carboniferous Swamps ----
    "Meganeura": dict(
        group="Giant griffinfly (a dragonfly relative, Meganisoptera)",
        diet="Predator of other insects",
        size="~65-75 cm wingspan",
        lived="Late Carboniferous (~300 Ma)",
        fact="With wings wider than a school ruler is long, it was one of the biggest flying insects ever.",
        source_1="https://www.nhm.ac.uk/discover/giant-dragonflies.html",
        source_2="https://www.nationalgeographic.com/science/article/110808-ancient-insects-bugs-giants-oxygen-animals-science"),
    "Arthropleura": dict(
        group="Giant millipede relative (myriapod)",
        diet="Detritivore — ate rotting plants",
        size="up to ~2.5 m long",
        lived="Carboniferous to early Permian (~344-292 Ma)",
        fact="It was the largest land invertebrate ever — about as long as a surfboard.",
        source_1="https://www.nhm.ac.uk/discover/news/2021/december/worlds-largest-terrestrial-arthropod-was-car-sized-millipede.html",
        source_2="https://www.britannica.com/animal/Arthropleura"),
    "Hylonomus": dict(
        group="One of the earliest reptiles (early amniote)",
        diet="Ate small insects and millipedes",
        size="~20-25 cm",
        lived="Late Carboniferous (~318 Ma)",
        fact="It is one of the earliest animals known to live its whole life on land.",
        source_1="https://www.britannica.com/animal/Hylonomus",
        source_2="https://ucmp.berkeley.edu/carboniferous/carboniferous.php"),
    "Pulmonoscorpius": dict(
        group="Giant scorpion (arachnid)",
        diet="Hunted smaller arthropods and small animals",
        size="up to ~70 cm",
        lived="Early Carboniferous (~341 Ma)",
        fact="This scorpion grew as long as your arm and hunted by day with large eyes.",
        source_1="https://www.nature.com/articles/314355a0",
        source_2="https://pmc.ncbi.nlm.nih.gov/articles/PMC4232842/"),
    "Petrolacosaurus": dict(
        group="Early diapsid reptile",
        diet="Insectivore",
        size="~40 cm",
        lived="Late Carboniferous (~302 Ma)",
        fact="It is one of the earliest reptiles with the two-holed skull pattern later seen in dinosaurs and lizards.",
        source_1="https://ucmp.berkeley.edu/diapsids/diapsids.html",
        source_2="https://pmc.ncbi.nlm.nih.gov/articles/PMC3203498/"),
    "Pholiderpeton": dict(
        group="Embolomere amphibian (older name: Eogyrinus)",
        pronunciation="foll-ih-DER-pet-on",
        diet="Carnivore — probably ate fish",
        size="up to ~4 m",
        lived="Late Carboniferous",
        fact="This eel-like swamp amphibian grew as long as a small crocodile.",
        source_1="https://www.britannica.com/science/Carboniferous-Period/Carboniferous-life",
        source_2="https://ucmp.berkeley.edu/carboniferous/carboniferous.php"),

    # ---- Age 4: Permian Wilds ----
    "Dimetrodon": dict(
        group="Synapsid (a mammal ancestor — NOT a dinosaur)",
        diet="Carnivore",
        size="~1.7-4.6 m",
        lived="Early Permian (~294-271 Ma)",
        fact="Its big back sail makes people think it is a dinosaur, but it lived ~40 million years earlier and is closer to us than to dinosaurs.",
        source_1="https://www.britannica.com/animal/Dimetrodon",
        source_2="https://www.fieldmuseum.org/page/fossil-non-mammalian-synapsid-collection-field-museum"),
    "Edaphosaurus": dict(
        group="Synapsid (early mammal relative)",
        diet="Herbivore",
        size="~0.5-3.5 m",
        lived="Late Carboniferous to Early Permian",
        fact="It had a tall back sail with little cross-bars, like a prehistoric sailboat.",
        source_1="https://www.britannica.com/animal/Edaphosaurus",
        source_2="https://ucmp.berkeley.edu/synapsids/pelycosaurs.html"),
    "Gorgonops": dict(
        group="Gorgonopsian therapsid (mammal relative)",
        diet="Carnivore",
        size="skull ~30 cm; body ~1-2 m",
        lived="Middle-Late Permian (~260-254 Ma)",
        fact="It had sabre-like fangs long before the sabre-toothed cats existed.",
        source_1="https://ucmp.berkeley.edu/synapsids/gorgonopsia.html",
        source_2="https://www.fieldmuseum.org/about/press/fossil-predator-is-the-oldest-known-animal-with-saber-teeth"),
    "Inostrancevia": dict(
        group="Gorgonopsian therapsid (mammal relative)",
        diet="Apex carnivore",
        size="~3-3.5 m",
        lived="Late Permian (~256-252 Ma)",
        fact="Its sabre teeth reached about 15 cm — longer than your hand.",
        source_1="https://www.fieldmuseum.org/about/press/fossils-of-a-saber-toothed-top-predator-reveal-a-scramble-for-dominance",
        source_2="https://ucmp.berkeley.edu/synapsids/gorgonopsia.html"),
    "Helicoprion": dict(
        group="Cartilaginous fish (a chimaera relative)",
        diet="Ate soft-bodied prey like squid relatives",
        size="~5-12 m (estimated)",
        lived="Early-Middle Permian (~290-270 Ma)",
        fact="Its lower jaw held a bizarre spiral 'buzz-saw' whorl of teeth.",
        source_1="https://australian.museum/learn/animals/fishes/helicoprion/",
        source_2="https://www.nationalgeographic.com/science/article/buzzsaw-jaw-helicoprion-was-a-freaky-ratfish"),
    "Diadectes": dict(
        group="Reptile-like tetrapod (reptiliomorph)",
        diet="Herbivore",
        size="~3 m",
        lived="Early Permian (~290-272 Ma)",
        fact="It was one of the first big plant-eating land animals.",
        source_1="https://www.britannica.com/animal/Diadectes",
        source_2="https://www.si.edu/object/nmnhpaleobiology_3450979"),

    # ---- Age 5: Triassic ----
    "Eoraptor": dict(
        group="Early dinosaur (basal sauropodomorph)",
        diet="Omnivore",
        size="~1.2-1.3 m",
        lived="Late Triassic (~231 Ma)",
        fact="One of the earliest dinosaurs — small, light and quick.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/eoraptor.html",
        source_2="https://www.britannica.com/animal/Eoraptor"),
    "Herrerasaurus": dict(
        group="Early dinosaur (saurischian)",
        diet="Carnivore",
        size="~6 m",
        lived="Late Triassic (~231 Ma)",
        fact="One of the earliest meat-eating dinosaurs, named after the goat-herder who found it.",
        source_1="https://ucmp.berkeley.edu/diapsids/herrerasaurus.html",
        source_2="https://www.britannica.com/animal/Herrerasaurus"),
    "Coelophysis": dict(
        group="Theropod dinosaur",
        diet="Carnivore",
        size="~3 m",
        lived="Late Triassic (~215-201 Ma)",
        fact="A Coelophysis skull even flew to space aboard the Space Shuttle in 1998.",
        source_1="https://www.amnh.org/explore/ology/ology-cards/263-coelophysis",
        source_2="https://www.britannica.com/animal/Coelophysis"),
    "Plateosaurus": dict(
        group="Sauropodomorph dinosaur",
        diet="Herbivore",
        size="~5-10 m",
        lived="Late Triassic (~214-204 Ma)",
        fact="Over 100 skeletons have been found, so scientists know it very well.",
        source_1="https://www.britannica.com/animal/Plateosaurus",
        source_2="https://pmc.ncbi.nlm.nih.gov/articles/PMC12092109/"),
    "Postosuchus": dict(
        group="Pseudosuchian archosaur (crocodile line — NOT a dinosaur)",
        diet="Apex carnivore",
        size="~5-6 m",
        lived="Late Triassic (Norian)",
        fact="It was a top predator on the crocodile branch of the family tree, not a dinosaur.",
        source_1="https://ucmp.berkeley.edu/taxa/verts/archosaurs/rauisuchia.php",
        source_2="https://www.nationalgeographic.com/science/article/poposaurus-postosuchus-and-the-dinosaur-mimic-croc-walk"),
    "Tanystropheus": dict(
        group="Archosauromorph reptile (NOT a dinosaur)",
        diet="Fish-eater",
        size="~6 m",
        lived="Middle to early Late Triassic",
        fact="Its neck was longer than its body and tail put together.",
        source_1="https://www.fieldmuseum.org/about/press/fossil-mystery-solved-super-long-necked-reptiles-lived-ocean-not-land",
        source_2="https://www.nhm.ac.uk/discover/the-triassic-period-the-rise-of-the-dinosaurs.html"),

    # ---- Age 6: Jurassic ----
    "Brachiosaurus": dict(
        group="Sauropod dinosaur",
        diet="Herbivore (high browser)",
        size="~18-22 m",
        lived="Late Jurassic (~156-145 Ma)",
        fact="Its front legs were longer than its back legs, so it stood like a giant giraffe.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/brachiosaurus.html",
        source_2="https://www.amnh.org/explore/news-blogs/largest-dinosaur-foot-study"),
    "Diplodocus": dict(
        group="Sauropod dinosaur",
        diet="Herbivore",
        size="~24-26 m",
        lived="Late Jurassic (~152-149 Ma)",
        fact="Its whip-like tail contained around 80 bones.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/diplodocus.html",
        source_2="https://www.britannica.com/animal/Diplodocus"),
    "Stegosaurus": dict(
        group="Ornithischian armoured dinosaur",
        diet="Herbivore",
        size="~7-9 m",
        lived="Late Jurassic (~155-145 Ma)",
        fact="Despite weighing several tonnes, its brain was only about the size of a dog's.",
        source_1="https://www.britannica.com/animal/Stegosaurus",
        source_2="https://www.amnh.org/explore/ology/ology-cards/017-stegosaurus-stenops"),
    "Allosaurus": dict(
        group="Theropod dinosaur",
        diet="Carnivore",
        size="~7.5-9 m",
        lived="Late Jurassic (~155-143 Ma)",
        fact="Like a shark, it kept growing and shedding new serrated teeth all its life.",
        source_1="https://www.britannica.com/animal/Allosaurus",
        source_2="https://www.si.edu/newsdesk/releases/just-our-type-smithsonians-dinosaur-skeleton-becomes-scientific-standard"),
    "Ceratosaurus": dict(
        group="Theropod dinosaur",
        diet="Carnivore",
        size="~5.3-7 m",
        lived="Late Jurassic (~155 Ma)",
        fact="It had a horn on its nose, probably for show rather than for fighting.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/ceratosaurus.html",
        source_2="https://www.britannica.com/animal/Ceratosaurus"),
    "Archaeopteryx": dict(
        group="Feathered dinosaur / earliest bird (avialan theropod)",
        diet="Carnivore",
        size="~0.5 m long (raven-sized)",
        lived="Late Jurassic (~150 Ma)",
        fact="It is a famous link between feathered dinosaurs and modern birds.",
        source_1="https://www.britannica.com/animal/Archaeopteryx",
        source_2="https://www.fieldmuseum.org/exhibition/halls-and-galleries/meet-the-chicago-archaeopteryx"),

    # ---- Age 7: Early Cretaceous ----
    "Iguanodon": dict(
        group="Ornithopod dinosaur",
        diet="Herbivore",
        size="~9-11 m",
        lived="Early Cretaceous (~126-122 Ma)",
        fact="Its big thumb spike was first put on its nose by mistake, like a little horn.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/iguanodon.html",
        source_2="https://www.britannica.com/animal/Iguanodon"),
    "Deinonychus": dict(
        group="Dromaeosaur ('raptor') dinosaur",
        diet="Carnivore",
        size="~3.4 m",
        lived="Early Cretaceous (~115-108 Ma)",
        fact="Its name means 'terrible claw' after the big sickle claw on each foot.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/deinonychus.html",
        source_2="https://www.britannica.com/animal/Deinonychus"),
    "Utahraptor": dict(
        group="Dromaeosaur ('raptor') dinosaur",
        diet="Carnivore",
        size="~6-7 m",
        lived="Early Cretaceous (~139-135 Ma)",
        fact="It was the largest known raptor, with a killing claw about 24 cm long.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/utahraptor.html",
        source_2="https://www.nationalgeographic.com/animals/article/150106-utahraptor-death-trap-fossil"),
    "Baryonyx": dict(
        group="Spinosaurid theropod dinosaur",
        diet="Fish-eater (piscivore)",
        size="~7.5-10 m",
        lived="Early Cretaceous (~130-125 Ma)",
        fact="Fish scales were found in its stomach, proving it fished like a giant heron.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/baryonyx.html",
        source_2="https://www.fieldmuseum.org/blog/lets-lend-these-dinosaurs-hand"),
    "Polacanthus": dict(
        group="Ankylosaur (armoured dinosaur)",
        diet="Herbivore",
        size="~4-5 m",
        lived="Early Cretaceous (~130-125 Ma)",
        fact="Its back was covered in armour plates and spikes like a walking tank.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/polacanthus.html",
        source_2="https://www.nhm.ac.uk/discover/isle-of-wight-dinosaur-island.html"),
    "Hypsilophodon": dict(
        group="Small ornithopod dinosaur",
        diet="Herbivore",
        size="~1.5-2 m",
        lived="Early Cretaceous (~130-125 Ma)",
        fact="It was a fast little runner that could grip plants with a special finger.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/hypsilophodon.html",
        source_2="https://www.britannica.com/animal/Hypsilophodon"),

    # ---- Age 8: Late Cretaceous ----
    "Tyrannosaurus rex": dict(
        group="Tyrannosaurid theropod dinosaur",
        diet="Apex carnivore",
        size="~12-13 m",
        lived="Late Cretaceous (~69-66 Ma)",
        fact="Its bite was one of the most powerful of any land animal ever.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/tyrannosaurus.html",
        source_2="https://www.amnh.org/exhibitions/permanent/saurischian-dinosaurs/tyrannosaurus-rex"),
    "Triceratops": dict(
        group="Ceratopsian (horned) dinosaur",
        diet="Herbivore",
        size="~8-9 m",
        lived="Late Cretaceous (~69-66 Ma)",
        fact="A baby's whole skull was only about the size of a grown-up's head.",
        source_1="https://www.britannica.com/animal/Triceratops",
        source_2="https://www.amnh.org/exhibitions/dinosaurs-ancient-fossils/display-or-defense/the-horned-dinosaurs"),
    "Velociraptor": dict(
        group="Dromaeosaur ('raptor') dinosaur",
        diet="Carnivore",
        size="~1.5-2 m (turkey-sized)",
        lived="Late Cretaceous (~75-71 Ma)",
        fact="The real Velociraptor was feathered and only turkey-sized — the movie ones were based on the bigger Deinonychus.",
        source_1="https://www.nhm.ac.uk/discover/velociraptor-facts.html",
        source_2="https://www.nationalgeographic.com/science/article/velociraptor"),
    "Ankylosaurus": dict(
        group="Ankylosaur (armoured dinosaur)",
        diet="Herbivore",
        size="~6-8 m",
        lived="Late Cretaceous (~70-66 Ma)",
        fact="Its tail ended in a heavy bony club it could swing like a hammer.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/ankylosaurus.html",
        source_2="https://www.britannica.com/animal/Ankylosaurus"),
    "Pachycephalosaurus": dict(
        group="Pachycephalosaur (dome-headed) dinosaur",
        diet="Mixed plant diet",
        size="~4.5 m",
        lived="Late Cretaceous (~70-66 Ma)",
        fact="Its super-thick skull roof may have been used for head-butting, like a bighorn sheep.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/pachycephalosaurus.html",
        source_2="https://www.britannica.com/animal/Pachycephalosaurus"),
    "Parasaurolophus": dict(
        group="Hadrosaur (duck-billed) dinosaur",
        diet="Herbivore",
        size="~9 m",
        lived="Late Cretaceous (~76.5-73 Ma)",
        fact="Its long hollow head-crest could make deep trumpet-like sounds.",
        source_1="https://www.nhm.ac.uk/discover/dino-directory/parasaurolophus.html",
        source_2="https://www.britannica.com/animal/Parasaurolophus"),

    # ---- Age 9: Paleogene (Rise of Mammals) ----
    "Titanoboa": dict(
        group="Giant snake (a boa relative)",
        diet="Fish-eater",
        size="~12.8-14.3 m",
        lived="Paleocene (~60-58 Ma)",
        fact="It is the largest snake ever found — about as long as a bus.",
        source_1="https://www.floridamuseum.ufl.edu/science/titanoboa/",
        source_2="https://www.britannica.com/animal/Titanoboa"),
    "Gastornis": dict(
        group="Giant flightless bird",
        diet="Herbivore (once thought a predator)",
        size="~2 m tall",
        lived="Paleocene-Eocene (~66-45 Ma)",
        fact="Despite its scary beak, new evidence says this giant bird was a gentle plant-eater.",
        source_1="https://www.amnh.org/explore/ology/ology-cards/002-diatryma-gigantea",
        source_2="https://www.nationalgeographic.com/science/article/giant-prehistoric-bird-crushed-seeds-not-little-horses"),
    "Basilosaurus": dict(
        group="Early whale (marine mammal)",
        diet="Apex carnivore",
        size="~17-20 m",
        lived="Late Eocene (~41-34 Ma)",
        fact="Its name means 'king lizard', but it is really an early whale — the name was a mistake.",
        source_1="https://www.britannica.com/animal/Basilosaurus",
        source_2="https://ocean.si.edu/ocean-life/marine-mammals/whales"),
    "Uintatherium": dict(
        group="Dinoceratan mammal",
        diet="Herbivore (browser)",
        size="~1.5 m at the shoulder",
        lived="Eocene (~50-37 Ma)",
        fact="It had three pairs of bony knobs on its head and big tusks.",
        source_1="https://www.britannica.com/animal/Uintatherium",
        source_2="https://www.nationalgeographic.com/science/article/battle-for-the-bone-wars-beasts"),
    "Paraceratherium": dict(
        group="Hornless rhino relative (mammal)",
        diet="Herbivore (browser)",
        size="~4.8 m at the shoulder",
        lived="Oligocene (~34-23 Ma)",
        fact="It was one of the largest land mammals ever — a hornless rhino taller than a giraffe.",
        source_1="https://research.amnh.org/paleontology/perissodactyl/concepts/deep-time/oligocene",
        source_2="https://www.nationalgeographic.com/science/article/the-last-of-the-rhinoceros-titans"),
    "Andrewsarchus": dict(
        group="Large hoofed mammal (an artiodactyl relative)",
        diet="Omnivore / scavenger",
        size="skull ~83 cm",
        lived="Middle Eocene (~48-43 Ma)",
        fact="It is known mainly from one enormous skull found in Mongolia in 1923.",
        source_1="https://www.amnh.org/explore/news-blogs/andrewsarchus-prehistoric-mammal",
        source_2="https://www.amnh.org/exhibitions/permanent/advanced-mammals/cetaceans"),

    # ---- Age 10: Ice Age ----
    "Woolly mammoth": dict(
        group="Elephant family (Elephantidae)",
        diet="Herbivore (grasses and plants)",
        size="~2.8-3.2 m at the shoulder",
        lived="Pleistocene into the early Holocene",
        fact="It had small ears and a short tail to avoid frostbite in the cold.",
        source_1="https://www.nhm.ac.uk/discover/last-mammoths.html",
        source_2="https://www.britannica.com/animal/woolly-mammoth"),
    "Smilodon": dict(
        group="Sabre-toothed cat (not closely related to tigers)",
        diet="Apex carnivore",
        size="~55-470 kg depending on species",
        lived="Pleistocene (~2.5 Ma-8 ka)",
        fact="Its cubs had baby sabre-teeth that fell out, just like children lose their baby teeth.",
        source_1="https://tarpits.org/stories/smilodon-saber-tooths-and-tigersoh-my",
        source_2="https://www.amnh.org/exhibitions/permanent/primitive-mammals/saber-toothed-cat"),
    "Woolly rhinoceros": dict(
        group="Rhino family (Rhinocerotidae)",
        diet="Herbivore (grazer)",
        size="~3.2-3.6 m long",
        lived="Pleistocene",
        fact="Ice-age humans painted it on cave walls over 30,000 years ago.",
        source_1="https://www.britannica.com/animal/woolly-rhinoceros",
        source_2="https://research.amnh.org/paleontology/perissodactyl/environment/interval4"),
    "Megatherium": dict(
        group="Giant ground sloth",
        diet="Herbivore (browser)",
        size="~6 m long; ~4 tonnes",
        lived="Pliocene to Late Pleistocene",
        fact="It was a sloth as heavy as an elephant that could rear up to reach high leaves.",
        source_1="https://www.britannica.com/animal/Megatherium",
        source_2="https://ucmp.berkeley.edu/mammal/xenarthra/xenarthrafr.html"),
    "Megaloceros": dict(
        group="Giant deer ('Irish elk')",
        diet="Herbivore (grazer/browser)",
        size="~2 m at the shoulder",
        lived="Pleistocene into the mid-Holocene",
        fact="It had the largest antlers of any deer ever — up to about 3.5 m across.",
        source_1="https://www.nhm.ac.uk/discover/irish-elk-giant-deer.html",
        source_2="https://www.britannica.com/animal/Irish-elk"),
    "Cave bear": dict(
        group="Bear family (Ursidae)",
        diet="Mostly herbivorous",
        size="~350-600 kg (males)",
        lived="Middle to Late Pleistocene",
        fact="Cave bears hibernated in caves so often that they wore hollows into the rock.",
        source_1="https://www.britannica.com/animal/cave-bear",
        source_2="https://pmc.ncbi.nlm.nih.gov/articles/PMC5059403/"),
}

# Creatures whose two sources are peer-reviewed papers / general pages rather than
# a dedicated kid-friendly museum page — flagged for the parent in the approval sheet.
THINLY_SOURCED = {"Pulmonoscorpius", "Petrolacosaurus", "Pholiderpeton"}
