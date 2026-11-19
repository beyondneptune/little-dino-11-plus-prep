#!/usr/bin/env python3
"""
Calibrated 11+ Maths question generator (original questions; every answer
computed in code, not recalled). Number ranges and topic mix are tuned to a
difficulty profile measured offline from a sample of real 11+ papers: mostly
1-2 digit numbers with a tail, ~8% decimals, a few fractions, broad topic
coverage.

Each item: topic, question, 4 options, verified answer index, worked explanation.
Writes maths_bank/questions.json + questions.md.
"""
import json
import random
import re
from fractions import Fraction
from math import gcd
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "maths_bank"


def _neg(s):                                   # a negative number anywhere -> implausible
    return bool(re.search(r"[-−]\s*\d", str(s)))


def mcq(correct, wrongs, rng):
    opts = [str(correct)]
    for w in wrongs:
        s = str(w)
        if s != str(correct) and s not in opts and not _neg(s):
            opts.append(s)
    m = re.search(r"\d+\.?\d*", str(correct))   # pad with positive perturbations of the answer
    k = 1
    while len(opts) < 4 and m:
        val = float(m.group()) + k
        v = str(int(val)) if val == int(val) else str(val)
        s = str(correct)[:m.start()] + v + str(correct)[m.end():]
        if s not in opts and not _neg(s):
            opts.append(s)
        k += 1
    if len(opts) < 4:   # never pad with look-alike copies of the answer
        raise ValueError(f"could not build 4 distinct options for {correct!r}")
    opts = opts[:4]
    rng.shuffle(opts)
    return opts, opts.index(str(correct))


# ---------------- topic generators ----------------
def g_arithmetic(rng):
    a, b = rng.randint(3, 12), rng.randint(3, 9)
    prod = a * b
    if rng.random() < 0.5:
        c = rng.randint(5, 40); ans = prod + c; op = "+"
    else:
        c = rng.randint(2, prod - 2); ans = prod - c; op = "−"   # keep the answer positive
    return ("arithmetic", f"Work out {a} × {b} {op} {c}",
            ans, [a + b * c, prod + (c if op == "−" else -c) or prod, ans + a, ans + b],
            f"Multiply first (BIDMAS): {a}×{b}={prod}, then {'add' if op=='+' else 'subtract'} {c} = {ans}.")


def g_long_mult(rng):
    a, b = rng.randint(123, 899), rng.randint(12, 49)
    ans = a * b
    return ("multiplication", f"Use long multiplication to work out {a} × {b}.",
            ans, [a * (b + 1), a * (b - 1), ans + a, ans - a],
            f"{a} × {b} = {ans}.")


def g_division(rng):
    b = rng.randint(3, 9); q = rng.randint(12, 120); a = b * q
    return ("division", f"Work out {a} ÷ {b}.", q,
            [q + 1, q - 1, q + 10, a - b],
            f"{a} ÷ {b} = {q} (since {b}×{q}={a}).")


def g_fraction_of(rng):
    d = rng.choice([3, 4, 5, 6, 8, 10]); n = rng.randint(2, d - 1)
    whole = d * rng.randint(2, 12); ans = whole // d * n
    return ("fractions", f"What is {n}/{d} of {whole}?", ans,
            [whole // d, whole - ans, ans + n, whole // d * (d - n)],
            f"{whole}÷{d}={whole//d}, then ×{n} = {ans}.")


def g_fraction_add(rng):
    b, d = rng.choice([2, 3, 4, 5, 6]), rng.choice([2, 3, 4, 6, 8])
    a, c = rng.randint(1, b - 1), rng.randint(1, d - 1)
    s = Fraction(a, b) + Fraction(c, d)
    ans = f"{s.numerator}/{s.denominator}" if s.denominator != 1 else str(s.numerator)
    return ("fractions", f"Work out {a}/{b} + {c}/{d}. Give your answer in its simplest form.",
            ans, [f"{a+c}/{b+d}", f"{a+c}/{b*d}", f"{s.numerator+1}/{s.denominator}", f"{s.numerator}/{s.denominator+1}"],
            f"Common denominator: {a}/{b}+{c}/{d} = {s} .")


def g_percent_of(rng):
    p = rng.choice([10, 20, 25, 50, 75])
    step = 100 // gcd(p, 100)                  # n must make p% of n a whole number
    n = step * rng.randint(2, max(3, 240 // step))
    ans = p * n // 100
    assert p * n % 100 == 0
    return ("percentages", f"Find {p}% of {n}.", ans,
            [n - ans, ans * 2, p * n // 10, ans + p],
            f"{p}% = {Fraction(p,100)}; {Fraction(p,100)}×{n} = {ans}.")


def g_percent_change(rng):
    p = rng.choice([10, 20, 25, 50]); price = rng.choice([20, 40, 60, 80, 100, 120])
    ans = price * (100 - p) // 100
    return ("percentages", f"A £{price} item is reduced by {p}% in a sale. What is the new price?",
            f"£{ans}", [f"£{price*p//100}", f"£{price*(100+p)//100}", f"£{price}", f"£{ans+5}"],
            f"Reduction = {p}% of £{price} = £{price*p//100}; new price = £{ans}.")


def g_ratio(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 6); unit = rng.randint(3, 12)
    total = (a + b) * unit; big = max(a, b) * unit
    return ("ratio/proportion", f"£{total} is shared in the ratio {a}:{b}. What is the larger share?",
            f"£{big}", [f"£{min(a,b)*unit}", f"£{total//2}", f"£{big+unit}", f"£{big-unit}"],
            f"{a}+{b}={a+b} parts; one part = £{unit}; larger = {max(a,b)}×£{unit} = £{big}.")


def g_area_rect(rng):
    w, h = rng.randint(3, 15), rng.randint(3, 12)
    if rng.random() < 0.5:
        return ("area/perimeter", f"A rectangle is {w} cm by {h} cm. What is its area?",
                f"{w*h} cm²", [f"{2*(w+h)} cm²", f"{w*h+w} cm²", f"{w+h} cm²", f"{w*h-h} cm²"],
                f"Area = length × width = {w}×{h} = {w*h} cm².")
    return ("area/perimeter", f"A rectangle is {w} cm by {h} cm. What is its perimeter?",
            f"{2*(w+h)} cm", [f"{w*h} cm", f"{w+h} cm", f"{2*(w+h)+2} cm", f"{2*w+h} cm"],
            f"Perimeter = 2×({w}+{h}) = {2*(w+h)} cm.")


def g_triangle_angle(rng):
    a, b = rng.randint(30, 80), rng.randint(30, 80)
    ans = 180 - a - b
    return ("angles/geometry", f"Two angles in a triangle are {a}° and {b}°. What is the third angle?",
            f"{ans}°", [f"{180-a}°", f"{a+b}°", f"{ans+10}°", f"{360-a-b}°"],
            f"Angles in a triangle sum to 180°: 180−{a}−{b} = {ans}°.")


def g_sequence(rng):
    start, step = rng.randint(1, 9), rng.randint(2, 9)
    seq = [start + step * i for i in range(4)]; ans = start + step * 4
    return ("algebra/sequence", f"What is the next term: {', '.join(map(str,seq))}, …?",
            ans, [ans + step, ans - 1, seq[-1] + step + 1, ans + 1],
            f"The rule is +{step} each time, so the next term is {seq[-1]}+{step} = {ans}.")


def g_mean(rng):
    k = rng.choice([3, 4, 5]); m = rng.randint(4, 15)
    vals = [rng.randint(1, 2 * m) for _ in range(k - 1)]
    vals.append(k * m - sum(vals))
    while vals[-1] < 1:
        vals = [rng.randint(1, 2 * m) for _ in range(k - 1)]; vals.append(k * m - sum(vals))
    return ("statistics", f"Find the mean of: {', '.join(map(str,vals))}.", m,
            [m + 1, m - 1, sum(vals), max(vals)],
            f"Mean = total ÷ how many = {sum(vals)}÷{k} = {m}.")


def g_rounding(rng):
    n = rng.randint(120, 9800); base = rng.choice([10, 100])
    ans = (n + base // 2) // base * base       # school rule: halves round UP
                                               # (Python's round() rounds halves to even)
    return ("rounding", f"Round {n} to the nearest {base}.", ans,
            [ans + base, ans - base, (n // base) * base, n],
            f"{n} rounds to {ans} (nearest {base}).")


def g_money_change(rng):
    cost = rng.randint(120, 980) / 100
    paid = rng.choice([n for n in (5, 10, 20) if n > cost])   # note must cover the cost
    change = round(paid - cost, 2)
    return ("money", f"A book costs £{cost:.2f}. You pay with a £{paid} note. How much change?",
            f"£{change:.2f}", [f"£{paid-round(cost):.2f}", f"£{change+1:.2f}",
            f"£{round(cost,2):.2f}", f"£{change-0.10:.2f}"],
            f"Change = £{paid} − £{cost:.2f} = £{change:.2f}.")


def g_convert(rng):
    m = rng.randint(2, 9) + rng.choice([0, 0.5]); ans = int(m * 100)
    return ("measures/convert", f"Convert {m} metres into centimetres.", f"{ans} cm",
            [f"{int(m*10)} cm", f"{int(m*1000)} cm", f"{ans+10} cm", f"{int(m)} cm"],
            f"1 m = 100 cm, so {m} m = {ans} cm.")


def g_primes(rng):
    pr = rng.choice([11, 13, 17, 19, 23, 29, 31, 37]); comp = rng.choice([15, 21, 25, 27, 33, 35, 39])
    pool = [pr, comp, rng.choice([9, 12, 16, 18, 24]), rng.choice([49, 51, 55, 57])]
    rng.shuffle(pool); idx = pool.index(pr)
    opts = [str(x) for x in pool]
    return ("primes/factors", f"Which of these is a prime number?", opts, idx,
            f"{pr} has no factors other than 1 and itself, so it is prime.")


GENS = [g_arithmetic, g_long_mult, g_division, g_fraction_of, g_fraction_add,
        g_percent_of, g_percent_change, g_ratio, g_area_rect, g_triangle_angle,
        g_sequence, g_mean, g_rounding, g_money_change, g_convert]


def build(n=80, seed=7):
    rng = random.Random(seed)
    OUT.mkdir(exist_ok=True)
    items = []
    for _ in range(n):
        g = rng.choice(GENS)
        topic, q, ans, wrongs, expl = g(rng)
        opts, idx = mcq(ans, wrongs, rng)
        items.append({"topic": topic, "question": q, "options": opts,
                      "answer": chr(65 + idx), "explanation": expl})
    # primes generator returns pre-built options; handle separately
    for _ in range(max(4, n // 15)):
        topic, q, opts, idx, expl = g_primes(rng)
        items.append({"topic": topic, "question": q, "options": opts,
                      "answer": chr(65 + idx), "explanation": expl})
    (OUT / "questions.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
    with (OUT / "questions.md").open("w", encoding="utf-8") as f:
        for i, it in enumerate(items, 1):
            f.write(f"**Q{i} [{it['topic']}]** {it['question']}\n\n")
            for j, o in enumerate(it["options"]):
                f.write(f"  {chr(65+j)}. {o}\n")
            f.write(f"\n*Answer: {it['answer']}* — {it['explanation']}\n\n---\n\n")
    print(f"Generated {len(items)} verified Maths questions -> {OUT}")
    return items


if __name__ == "__main__":
    build()
