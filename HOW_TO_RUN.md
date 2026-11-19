# How to run

Plain-English instructions.

## Check everything is healthy
```
cd little-dino-11-plus-prep
make test
```
All tests should say `passed`.

## See what has been built (the map)
```
.venv/bin/python scripts/coverage_report.py   # ages x creatures x topics
```
Open `content/coverage_report.md` to read it.

## Play the Age 1 slice
```
.venv/bin/python platform/age1_app.py
```
Then open **http://127.0.0.1:5000** in a browser. Pick Child A or Child B, tap a
creature on the Cambrian Seas map, and go Meet → Learn → Practise → Finish. The
"Grown-ups" link opens the parent dashboard (you set a PIN the first time).
When run locally it makes no third‑party calls (assets are self‑hosted), and every
question shown has passed the automated verification gate. Stop the app with Ctrl-C.

### Play on a tablet over your home Wi-Fi (not the internet)
```
.venv/bin/python platform/age1_app.py --lan
```
This still serves from your Mac, but also lets devices **on the same Wi-Fi** reach
it. The command prints two addresses — use the `http://192.168.x.x:5000/` one on
the tablet's browser. The first time, macOS may ask *"Do you want python to accept
incoming network connections?"* — click **Allow** (System Settings → Network →
Firewall). It is reachable only on your local network, never the public internet;
stop it (Ctrl-C) or run **without** `--lan` to go back to this-Mac-only. Add
`--port 8099` to pick a different port.

## Re-run the visual QA (screenshots + video + frame-rate)
```
.venv/bin/python scripts/visual_qa.py
```
Writes `v3_*` screenshots + a flow video to `design/screenshots/` and a summary to
`design/VISUAL_QA.md` (it starts the app, captures at four sizes, and stops the app).
