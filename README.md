# Disguise Timeline Exporter

A local Disguise Designer plugin that extracts timeline data — tracks, sections, cues, layers and their parameters — and generates a printable HTML report for show reproduction.

![Plugin screenshot](docs/screenshot.png)

---

## What it does

- Connects directly to a running Disguise Designer session via its local REST API
- Reads all tracks, sections (cues), and layers with their module type, timing, resource file, and modified parameters
- Resolves enum parameter values to their human-readable names (e.g. `loop` instead of `2`)
- Shows animated keyframe values with their timecodes
- Displays crossfade / transition info between sections
- Generates a self-contained HTML report suitable for printing or saving as PDF

---

## Installation

1. Copy the `timeline-exporter-plugin/` folder into your Disguise project's `plugins/` directory:

```
{project}/plugins/timeline-exporter-plugin/
  d3plugin.json
  index.html
  icon.svg
```

2. Open or restart the project in Designer — the plugin will appear in the plugin panel.

---

## Usage

1. Open the **Timeline Exporter** plugin inside Designer
2. Click **Extract** — the plugin reads all tracks from the current set list
3. Browse the extracted data directly in the plugin panel
4. Click **Report** to generate a printable HTML report
5. Use **Print / PDF** to save or print the report

---

## Layer colour coding

| Colour | Type |
|--------|------|
| Green  | Video / Image / Text / Web (content) |
| Purple | FX / Effects / Colour grading |
| Orange | Audio |
| Grey   | Disabled layers |

---

## Data extracted per layer

- Module type
- Timing: absolute start → end timecode within the timeline
- Resource file (media, image, audio…)
- All **modified** parameters only (defaults are hidden)
- Animated parameters shown as keyframe timecode sequences

---

## Requirements

- Disguise Designer r32 or later (uses the local plugin API + Python 2.7 embedded interpreter)
- No external dependencies — single self-contained HTML file

---

## Python CLI (optional)

A standalone Python 3 extractor is also included for offline use:

```bash
# Extract from a running Designer instance and generate a report
python run.py --host 192.168.1.100

# Test with mock data (no Designer needed)
python test_with_mock.py
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## File structure

```
timeline-exporter-plugin/   ← Drop into {project}/plugins/
  d3plugin.json             ← Plugin manifest
  index.html                ← Self-contained plugin (HTML + CSS + JS + Python extractor)
  icon.svg                  ← Plugin icon

extract.py                  ← Python CLI: fetch data from Designer REST API
extractor_inner.py          ← Python 2.7 script executed inside Designer
generate_report.py          ← Python CLI: render HTML report from extracted JSON
run.py                      ← One-shot: extract + generate report
test_with_mock.py           ← Run with mock data for development/testing
requirements.txt            ← Python dependencies
```

---

## API used

The plugin sends a `POST /api/session/python/execute` request to the local Designer REST API with a Python 2.7 script. The script traverses the `guisystem.currentSetList` to extract track, section, layer and parameter data.

Key Designer Python objects used:
- `guisystem.currentSetList.tracks` — all tracks
- `track.cueBeats()` — section boundaries
- `track.layers` — layer objects (`SuperLayer`)
- `layer.nSequences()` / `layer.sequence(i)` — parameter field sequences
- `cue.sectionTransition` — crossfade/transition info (`TrackTransitionInfo`)

---

## License

MIT
