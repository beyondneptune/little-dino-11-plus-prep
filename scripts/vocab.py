#!/usr/bin/env python3
"""
Graded 11+ vocabulary (original, authored). Deliberately mixes common short
words with harder 11+ words so the generated questions' word-length profile
matches the real papers (~11-12% of words 8+ letters).
"""
SYN = [
    # common tier
    ("big", "large"), ("happy", "glad"), ("fast", "quick"), ("begin", "start"),
    ("cold", "chilly"), ("clever", "smart"), ("tired", "weary"), ("brave", "bold"),
    ("calm", "peaceful"), ("tiny", "small"), ("angry", "cross"), ("neat", "tidy"),
    ("quiet", "silent"), ("rich", "wealthy"), ("strange", "odd"),
    # harder 11+ tier (longer / rarer words)
    ("abundant", "plentiful"), ("reluctant", "unwilling"), ("conceal", "hide"),
    ("fragile", "delicate"), ("generous", "giving"), ("courageous", "brave"),
    ("tremendous", "huge"), ("furious", "angry"), ("cautious", "careful"),
    ("genuine", "real"), ("vacant", "empty"), ("feeble", "weak"),
    ("essential", "vital"), ("sturdy", "strong"), ("enormous", "massive"),
    ("gloomy", "dismal"), ("peculiar", "unusual"), ("hesitate", "pause"),
    ("vanish", "disappear"), ("summit", "peak"),
]
ANT = [
    ("hot", "cold"), ("fast", "slow"), ("happy", "sad"), ("big", "small"),
    ("open", "shut"), ("light", "dark"), ("early", "late"), ("wet", "dry"),
    ("hard", "soft"), ("full", "empty"),
    # harder 11+ tier
    ("expand", "contract"), ("ancient", "modern"), ("generous", "selfish"),
    ("victory", "defeat"), ("permanent", "temporary"), ("artificial", "natural"),
    ("transparent", "opaque"), ("abundant", "scarce"), ("increase", "decrease"),
    ("ascend", "descend"), ("conceal", "reveal"), ("cautious", "reckless"),
    ("arrive", "depart"), ("praise", "criticise"), ("courage", "cowardice"),
]
# Categories chosen so that no word plausibly belongs to two categories
# (e.g. no plum/peach/lemon: also colours; no silver/copper/bronze: also colours).
CATS = {
    "fruit": ["apple", "pear", "grape", "melon", "mango", "banana", "papaya"],
    "animal": ["tiger", "horse", "rabbit", "otter", "camel", "zebra", "donkey"],
    "colour": ["scarlet", "crimson", "maroon", "turquoise", "magenta", "beige"],
    "vehicle": ["lorry", "tractor", "scooter", "ferry", "glider", "barge"],
    "metal": ["iron", "nickel", "pewter", "zinc", "tin", "aluminium"],
    "tree": ["oak", "willow", "birch", "cedar", "sycamore", "beech"],
    "instrument": ["trumpet", "trombone", "clarinet", "violin", "cymbal", "piano"],
    "occupation": ["plumber", "engineer", "architect", "librarian", "carpenter", "surgeon"],
    "weather": ["blizzard", "drizzle", "thunder", "hurricane", "sunshine", "breeze"],
    "building": ["cathedral", "cottage", "mansion", "bungalow", "warehouse", "tower"],
}

# Extra same-meaning links not captured by SYN pairs alone. Used to build
# meaning clusters so a distractor is never a second correct answer.
EXTRA_SAME = [
    ("big", "huge"), ("big", "massive"), ("big", "enormous"), ("big", "tremendous"),
    ("large", "huge"), ("strange", "peculiar"), ("odd", "unusual"),
    ("small", "little"), ("angry", "furious"), ("scared", "afraid"),
    ("happy", "cheerful"), ("sad", "gloomy"), ("sad", "dismal"),
    ("cold", "freezing"), ("hot", "boiling"), ("empty", "vacant"),
    ("brave", "courageous"), ("bold", "courageous"), ("calm", "quiet"),
]


def _clusters():
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    for a, b in SYN + EXTRA_SAME:
        parent[find(a)] = find(b)
    groups = {}
    for w in list(parent):
        groups.setdefault(find(w), set()).add(w)
    return {w: groups[find(w)] for w in parent}


_CL = _clusters()


def same_meaning(a, b):
    """True if a and b are (transitively) listed as meaning the same."""
    return a == b or b in _CL.get(a, ())


def opposite_of(a, b):
    """True if a and b are opposites, allowing synonyms of either side."""
    return any((same_meaning(a, x) and same_meaning(b, y)) or
               (same_meaning(a, y) and same_meaning(b, x)) for x, y in ANT)
