# Disguise Timeline Printout — context for Claude

## What this project is

A plugin for **Disguise Designer** (show control / media server software) that extracts timeline data and generates a printable HTML report. Used for show documentation and reproduction.

Two delivery modes:
1. **Designer plugin** (`timeline-printout-plugin/`) — self-contained HTML/JS/Python file dropped into a Disguise project's `plugins/` folder
2. **Python 3 CLI** — standalone scripts for offline use or automation

---

## File map

```
timeline-printout-plugin/   ← Drop into {project}/plugins/
  d3plugin.json             ← Plugin manifest (name + requiresSession)
  index.html                ← Self-contained plugin UI (HTML + CSS + JS + embedded Python extractor)
  icon.svg                  ← Plugin icon

extract.py                  ← CLI: connect to Designer REST API and fetch data (Python 3)
extractor_inner.py          ← Python 2.7 script executed *inside* Designer via POST /api/session/python/execute
generate_report.py          ← CLI: render the extracted JSON into an HTML report (uses Jinja2)
run.py                      ← One-shot: extract + generate report in sequence
test_with_mock.py           ← Dev helper: run with mock data, no Designer needed
requirements.txt            ← Python 3 deps: designer-plugin, jinja2, zeroconf
```

---

## Key architecture points

- The **inner extractor** (`extractor_inner.py`) runs inside Designer's embedded **Python 2.7** interpreter. It must stay Python 2/3 compatible and avoid modern syntax.
- The **plugin UI** (`index.html`) is a single self-contained file — no build step, no bundler. All CSS and JS are inlined.
- The plugin communicates with Designer via `POST /api/session/python/execute` (local REST API, default port 80).
- Data flows: Designer Python objects → JSON string → parsed in CLI/plugin → Jinja2 HTML report.

### Designer Python objects used (inside extractor_inner.py)
- `guisystem.currentSetList.tracks` — all tracks
- `track.cueBeats()` — section boundaries
- `track.layers` — layer objects (`SuperLayer`)
- `layer.nSequences()` / `layer.sequence(i)` — parameter field sequences
- `cue.sectionTransition` — crossfade/transition info (`TrackTransitionInfo`)

---

## Data model (extracted JSON)

```json
{
  "tracks": [
    {
      "name": "...",
      "cues": [ { "name", "start_tc", "end_tc", "transition": {...} } ],
      "layers": [ { "module_type", "start_tc", "end_tc", "resource", "params": [...] } ]
    }
  ],
  "errors": ["..."]
}
```

---

## Layer colour coding (in report)

| Colour | Type |
|--------|------|
| Green  | Video / Image / Text / Web |
| Purple | FX / Effects / Colour grading |
| Orange | Audio |
| Grey   | Disabled layers |

---

## CLI usage

```bash
pip install -r requirements.txt

# Extract + report in one shot
python run.py --host 192.168.1.100

# Extract only
python extract.py --host 192.168.1.100 --out data.json

# Report only from saved JSON
python generate_report.py data.json --out report.html

# Dev: mock data, no Designer needed
python test_with_mock.py
```

---

## Constraints to keep in mind

- `extractor_inner.py` must remain **Python 2.7 compatible** (Designer's embedded interpreter).
- `index.html` is intentionally a **single file** — do not split it or add a build pipeline unless asked.
- Designer API runs on **localhost port 80** by default; port is configurable via `--port`.
- Target: **Disguise Designer r32+**.
