#!/usr/bin/env python3
"""
Visual QA v3 for the UI overhaul (Checkpoint 3). Starts the app, seeds a little
progress (so the Museum + Parent dashboard render richly), then captures every
slice screen at 390x844 / 768x1024 / 1024x768 / 1440x900 as v3_*.png:
Home, Map, Lineup, Meet (Trilobite + the now-file-pipeline Anomalocaris & Pikaia),
Learn, Learn-number-line, Practise, Practise-wrong (per-option explanation),
Practise-correct (confetti + flying star + journey step), Finish ("Great work!"),
Fossil Dig (sand + revealed fossil), Museum (plinths + flipped fact card),
Parent dashboard (PIN -> heatmap + weak topics + time). Records a full-path flow
video, measures frame rate under 4x CPU throttle, then STOPS the server.
"""
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "design" / "screenshots"
PORT = 5057
SIZES = [(390, 844), (768, 1024), (1024, 768), (1440, 900)]


def _wait_up(port, timeout=25):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def _round(stem):
    m = re.search(r"Round (\d+) to the nearest (\d+)", stem)
    if not m:
        return None
    n, b = int(m[1]), int(m[2])
    return str((n + b // 2) // b * b)


def _answer_one(page, correct=True):
    page.wait_for_function("()=>{const t=document.querySelector('.tiles .tile');return t&&!t.disabled;}",
                           timeout=6000)
    ans = _round(page.inner_text(".stem"))
    tiles = page.locator(".tiles .tile")
    for i in range(tiles.count()):
        if (tiles.nth(i).inner_text().strip() == ans) == correct:
            tiles.nth(i).click()
            return
    tiles.first.click()


def _checks(page):
    return page.evaluate("""() => {let tiny=0;
      document.querySelectorAll('button,a,.tile').forEach(b=>{const r=b.getBoundingClientRect();
        if(r.width>0&&r.height>0&&r.height<44) tiny++;});
      return {overflow: document.documentElement.scrollWidth>window.innerWidth+2, tiny};}""")


def _play(api, base, who, topic, creature, sessions, perq, right):
    """Drive real attempts through the API to reach a chosen mastery state.
    Peeks the correct index with a non-counting answer, then records the real one."""
    for _ in range(sessions):
        for i in range(perq):
            q = api.get(f"{base}/api/question?who={who}&topic={topic}&level=1").json()
            if "id" not in q:
                return
            peek = api.post(base + "/api/answer",
                            data={"who": who, "topic": topic, "qid": q["id"], "chosen": 0, "count": False}).json()
            ai = peek["answer_index"]
            chosen = ai if i < right else (ai + 1) % max(2, len(q["options"]))
            api.post(base + "/api/answer",
                     data={"who": who, "topic": topic, "qid": q["id"], "chosen": chosen, "count": True})
        api.post(base + "/api/master", data={"who": who, "topic": topic, "creature": creature})


def _seed(api, base):
    """Genuinely master Trilobite's two topics across sessions (earns its museum
    card), leave a weaker topic for the heatmap, add time + a fossil."""
    _play(api, base, "child_a", "MA-A05", "trilobite", sessions=2, perq=6, right=6)
    _play(api, base, "child_a", "MA-B01", "trilobite", sessions=2, perq=6, right=6)
    _play(api, base, "child_a", "MA-B04", "anomalocaris", sessions=1, perq=6, right=5)  # Secure, 1 session
    api.post(base + "/api/tick", data={"who": "child_a", "topic": "MA-A05", "seconds": 180})
    api.post(base + "/api/dig", data={"who": "child_a", "fossil": "ammonite"})


def _brush(page):
    el = page.query_selector(".digsite .sand")
    box = el.bounding_box() if el else None
    if not box:
        return
    x, y, w, h = box["x"], box["y"], box["width"], box["height"]
    for r in range(10):
        ry = y + h * (r + 0.5) / 10
        page.mouse.move(x + 6, ry)
        page.mouse.down()
        page.mouse.move(x + w - 6, ry, steps=14)
        page.mouse.up()
    for c in range(6):
        cx = x + w * (c + 0.5) / 6
        page.mouse.move(cx, y + 6)
        page.mouse.down()
        page.mouse.move(cx, y + h - 6, steps=14)
        page.mouse.up()


def run():
    SHOTS.mkdir(parents=True, exist_ok=True)
    for old in list(SHOTS.glob("v2_*")) + list(SHOTS.glob("v3_*")):
        old.unlink()
    (ROOT / "platform" / "age1.db").unlink(missing_ok=True)
    proc = subprocess.Popen([sys.executable, str(ROOT / "platform" / "age1_app.py"), "--port", str(PORT)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results, fps_val, video = [], None, None
    base = f"http://127.0.0.1:{PORT}"
    try:
        if not _wait_up(PORT):
            raise RuntimeError("server did not start")
        with sync_playwright() as p:
            api = p.request.new_context()
            _seed(api, base)
            browser = p.chromium.launch()
            for w, h in SIZES:
                page = browser.new_page(viewport={"width": w, "height": h})
                errs = []
                page.on("console", lambda m: m.type == "error" and errs.append(m.text))
                page.on("pageerror", lambda e: errs.append(str(e)))

                def shot(name):
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(SHOTS / f"v3_{name}_{w}x{h}.png"))
                    c = _checks(page)
                    results.append({"s": name, "size": f"{w}x{h}", "err": len(errs),
                                    "overflow": c["overflow"], "tiny": c["tiny"]})
                    errs.clear()

                def meet_shot(creature, name):
                    page.goto(base + f"/station/child_a/{creature}")
                    page.wait_for_selector("#start")
                    greet = page.get_attribute("#station", "data-greet")
                    page.wait_for_function(
                        "g=>document.querySelector('#say')&&document.querySelector('#say').textContent.length>=g.length",
                        arg=greet, timeout=7000)
                    page.wait_for_timeout(400)
                    shot(name)

                try:
                    page.goto(base + "/"); page.wait_for_timeout(1100); shot("home")
                    page.goto(base + "/map/child_a"); page.wait_for_timeout(1000); shot("map")
                    page.goto(base + "/lineup"); page.wait_for_timeout(900); shot("lineup")
                    meet_shot("trilobite", "meet")
                    # learn — click through the teaching cards until the tiles appear
                    page.click("#start"); page.wait_for_selector(".learncard"); page.wait_for_timeout(500); shot("learn")
                    for _ in range(10):
                        if page.query_selector(".tiles"):
                            break
                        if page.query_selector(".numline"):
                            shot("learn_numberline")
                        nxt = page.query_selector("#nxt")
                        if not nxt:
                            break
                        nxt.click(); page.wait_for_timeout(350)
                    page.wait_for_selector(".tiles"); page.wait_for_timeout(400); shot("practise")
                    _answer_one(page, correct=False); page.wait_for_timeout(500); shot("practise_wrong")
                    page.click("#next")
                    _answer_one(page, correct=True); page.wait_for_timeout(350); shot("practise_correct")
                    page.click("#next")
                    for _ in range(14):
                        if page.query_selector(".finish"):
                            break
                        if page.query_selector(".tiles"):
                            _answer_one(page, correct=True); page.wait_for_timeout(250)
                            if page.query_selector("#next"):
                                page.click("#next")
                        page.wait_for_timeout(200)
                    if page.query_selector(".finish"):
                        page.wait_for_timeout(400); shot("finish")
                        # advance to the next topic (Rounding) to capture the number-line card
                        if not page.query_selector(".numline") and page.query_selector("#cont"):
                            page.click("#cont")
                            try:
                                page.wait_for_selector(".learncard", timeout=5000)
                                for _ in range(10):
                                    if page.query_selector(".numline"):
                                        page.wait_for_timeout(300); shot("learn_numberline"); break
                                    if page.query_selector(".tiles"):
                                        break
                                    nxt = page.query_selector("#nxt")
                                    if not nxt:
                                        break
                                    nxt.click(); page.wait_for_timeout(300)
                            except Exception:
                                pass
                    # the two newly file-pipeline stations rolling out
                    meet_shot("anomalocaris", "meet_anomalocaris")
                    meet_shot("pikaia", "meet_pikaia")
                    # Fossil Dig — sand, then brushed to reveal
                    page.goto(base + "/dig/child_a"); page.wait_for_selector(".digsite"); page.wait_for_timeout(500)
                    shot("dig")
                    _brush(page)
                    try:
                        page.wait_for_selector(".factcard", timeout=4000); page.wait_for_timeout(400); shot("dig_found")
                    except Exception:
                        pass
                    # Museum — plinths, then a flipped fact card
                    page.goto(base + "/museum/child_a"); page.wait_for_selector(".exhibit"); page.wait_for_timeout(700)
                    shot("museum")
                    if page.query_selector(".exhibit.earned .flip"):
                        page.click(".exhibit.earned .flip"); page.wait_for_timeout(800); shot("museum_card")
                    # Parent dashboard — PIN gate then heatmap
                    page.goto(base + "/parent"); page.wait_for_timeout(400)
                    if page.query_selector("input[name=pin]"):
                        page.fill("input[name=pin]", "2468")
                        page.click("form button"); page.wait_for_timeout(500)
                    if page.query_selector(".heatmap"):
                        page.wait_for_timeout(300); shot("parent")
                    # scaling-kit demo (Jurassic theme + template dinosaurs)
                    page.goto(base + "/kit"); page.wait_for_selector(".kit-card")
                    page.wait_for_timeout(1000); shot("kit_jurassic")

                    if (w, h) == (1024, 768):
                        page.goto(base + "/map/child_a"); page.wait_for_timeout(800)
                        try:
                            cdp = page.context.new_cdp_session(page)
                            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                        except Exception:
                            pass
                        fps_val = page.evaluate("""()=>new Promise(r=>{let n=0,t0=performance.now();
                          (function f(){n++;performance.now()-t0<2000?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)))})();})""")
                except Exception as e:
                    results.append({"s": "ERROR", "size": f"{w}x{h}", "err": 1, "overflow": False, "tiny": 0, "msg": str(e)[:120]})
                page.close()

            # full-path flow video at 1024x768
            ctx = browser.new_context(viewport={"width": 1024, "height": 768},
                                      record_video_dir=str(SHOTS), record_video_size={"width": 1024, "height": 768})
            vp = ctx.new_page()
            try:
                vp.goto(base + "/"); vp.wait_for_timeout(1400)
                vp.goto(base + "/map/child_a"); vp.wait_for_timeout(1600)
                vp.goto(base + "/station/child_a/trilobite"); vp.wait_for_selector("#start")
                vp.wait_for_timeout(2600); vp.click("#start"); vp.wait_for_selector(".learncard")
                for _ in range(10):
                    if vp.query_selector(".tiles"):
                        break
                    nxt = vp.query_selector("#nxt")
                    if not nxt:
                        break
                    nxt.click(); vp.wait_for_timeout(450)
                vp.wait_for_selector(".tiles")
                _answer_one(vp, correct=False); vp.wait_for_timeout(1400); vp.click("#next")
                _answer_one(vp, correct=True); vp.wait_for_timeout(1600); vp.click("#next")
                for _ in range(14):
                    if vp.query_selector(".finish"):
                        break
                    if vp.query_selector(".tiles"):
                        _answer_one(vp, correct=True); vp.wait_for_timeout(350)
                        if vp.query_selector("#next"):
                            vp.click("#next")
                    vp.wait_for_timeout(200)
                vp.wait_for_timeout(800)
                vp.goto(base + "/dig/child_a"); vp.wait_for_selector(".digsite"); vp.wait_for_timeout(600)
                _brush(vp); vp.wait_for_timeout(1400)
                vp.goto(base + "/museum/child_a"); vp.wait_for_selector(".exhibit"); vp.wait_for_timeout(1200)
                if vp.query_selector(".exhibit.earned .flip"):
                    vp.click(".exhibit.earned .flip"); vp.wait_for_timeout(1500)
            except Exception:
                pass
            path = vp.video.path(); ctx.close()
            video = Path(path).rename(SHOTS / "v3_flow_1024x768.webm")
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    bad = [r for r in results if r.get("err") or r.get("overflow") or r.get("tiny") or r["s"] == "ERROR"]
    lines = ["# Visual QA v3 (UI overhaul — Checkpoint 3)", "",
             f"Frame rate under 4x CPU throttle (1024x768 map): **{fps_val} fps**.",
             f"Flow video: `{video.relative_to(ROOT) if video else 'n/a'}`.",
             f"Captures: {len(results)}; flagged: **{len(bad)}**.", "",
             "| Screen | Size | console | overflow | <44px | note |", "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['s']} | {r['size']} | {r['err']} | {'YES' if r['overflow'] else 'no'} | {r['tiny']} | {r.get('msg','')} |")
    (ROOT / "design" / "VISUAL_QA.md").write_text("\n".join(lines) + "\n")
    print(f"captures {len(results)}  flagged {len(bad)}  fps {fps_val}")
    for r in bad:
        print("  !", r)


if __name__ == "__main__":
    run()
