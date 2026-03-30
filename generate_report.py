"""
Generate a human-readable HTML report from the extracted timeline JSON.
The HTML can be printed to PDF from any browser.

Usage:
    python generate_report.py timeline_data.json
    python generate_report.py timeline_data.json --out report.html
"""

import argparse
import json
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reprise de Spectacle — {project_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 12px;
    color: #1a1a1a;
    background: #fff;
    padding: 20px;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 4px;
    color: #111;
  }}
  .meta {{
    font-size: 11px;
    color: #666;
    margin-bottom: 30px;
  }}
  .track-section {{
    margin-bottom: 40px;
    border: 1px solid #ddd;
    border-radius: 6px;
    overflow: hidden;
  }}
  .track-header {{
    background: #1a1a2e;
    color: #fff;
    padding: 10px 16px;
    font-size: 15px;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .track-header .track-meta {{
    font-size: 11px;
    font-weight: 400;
    color: #aaa;
  }}
  .section-title {{
    padding: 8px 16px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: #f0f0f0;
    border-top: 1px solid #ddd;
    color: #555;
  }}

  /* Cues table */
  table.cues {{
    width: 100%;
    border-collapse: collapse;
  }}
  table.cues th {{
    background: #f7f7f7;
    padding: 5px 12px;
    text-align: left;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #888;
    border-bottom: 1px solid #e0e0e0;
  }}
  table.cues td {{
    padding: 6px 12px;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: top;
  }}
  table.cues tr:last-child td {{ border-bottom: none; }}
  table.cues tr:nth-child(even) {{ background: #fafafa; }}
  .cue-note {{
    color: #555;
    font-style: italic;
  }}
  .beat {{
    font-family: monospace;
    color: #333;
  }}
  .timecode {{
    font-family: monospace;
    font-size: 11px;
    color: #0066cc;
  }}

  /* Layer cards */
  .layers-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
    padding: 12px 16px;
  }}
  .layer-card {{
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
  }}
  .layer-card-header {{
    padding: 8px 12px;
    font-weight: 700;
    font-size: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .layer-card-header.content {{ background: #e8f4e8; color: #2d6a2d; }}
  .layer-card-header.fx {{ background: #e8e8f4; color: #2d2d6a; }}
  .layer-card-header.unknown {{ background: #f4f4e8; color: #6a6a2d; }}
  .layer-card-header.disabled {{ background: #f0f0f0; color: #999; }}
  .layer-type-badge {{
    font-size: 9px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    background: rgba(0,0,0,0.08);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}
  .layer-card-body {{
    padding: 8px 12px;
  }}
  .layer-timing {{
    font-size: 10px;
    color: #888;
    margin-bottom: 6px;
    font-family: monospace;
  }}
  .layer-resource {{
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 10px;
    margin-bottom: 6px;
    word-break: break-all;
    color: #5d4037;
  }}
  .layer-resource strong {{ color: #e65100; }}
  .params-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
  }}
  .params-table td {{
    padding: 2px 4px;
    font-size: 10px;
    border-bottom: 1px solid #f0f0f0;
  }}
  .params-table td:first-child {{
    color: #888;
    width: 40%;
    font-family: monospace;
  }}
  .params-table td:last-child {{
    color: #333;
    font-family: monospace;
  }}
  .params-table tr:last-child td {{ border-bottom: none; }}
  .no-params {{
    font-size: 10px;
    color: #bbb;
    font-style: italic;
  }}

  /* Print */
  @media print {{
    body {{ padding: 10px; }}
    .track-section {{ page-break-inside: avoid; }}
    .layer-card {{ page-break-inside: avoid; }}
  }}
  @page {{ margin: 15mm; }}
</style>
</head>
<body>

<h1>Reprise de Spectacle</h1>
<div class="meta">
  Projet : <strong>{project_name}</strong> &nbsp;|&nbsp;
  Généré le {generated_at} &nbsp;|&nbsp;
  {n_tracks} piste(s) extraite(s)
</div>

{tracks_html}

</body>
</html>
"""


def beats_to_timecode(beats: float, bpm: float = 60.0) -> str:
    """Convert beats to a HH:MM:SS timecode string (assuming 60 BPM by default)."""
    seconds = beats * (60.0 / bpm)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    frames = int((seconds - int(seconds)) * 25)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}:{frames:02d}"
    return f"{m:02d}:{s:02d}:{frames:02d}"


def classify_layer(layer: dict) -> str:
    """Classify a layer as content, fx, or unknown."""
    mtype = layer.get("module_type", "").lower()
    if not layer.get("enabled", True):
        return "disabled"
    if any(k in mtype for k in ["video", "image", "text", "web", "stream", "capture", "ndi"]):
        return "content"
    if any(k in mtype for k in ["fx", "effect", "blur", "color", "lut", "warp", "mask"]):
        return "fx"
    if any(k in mtype for k in ["audio", "sound"]):
        return "content"
    return "unknown"


def format_field_value(value) -> str:
    """Format a field value for display."""
    if value is None:
        return ""
    if isinstance(value, list):
        if len(value) == 1:
            return str(value[0].get("value", ""))
        # Multiple keyframes — show first and last
        if len(value) > 1:
            first = value[0].get("value", "")
            last = value[-1].get("value", "")
            return f"{first} → {last} ({len(value)} keys)"
    return str(value)


def render_layer_card(layer: dict) -> str:
    kind = classify_layer(layer)
    name = layer.get("name") or "(sans nom)"
    mtype = layer.get("module_type", "?")
    enabled = layer.get("enabled", True)
    t_start = layer.get("t_start", 0)
    t_end = layer.get("t_end", 0)
    t_length = layer.get("t_length", 0)
    resource = layer.get("resource")
    fields = layer.get("fields", {})

    disabled_tag = "" if enabled else " [DÉSACTIVÉ]"
    header_class = kind

    resource_html = ""
    if resource:
        resource_html = f'<div class="layer-resource"><strong>Contenu :</strong> {resource}</div>'

    # Params
    params_rows = ""
    if fields:
        for fname, fval in sorted(fields.items()):
            display = format_field_value(fval)
            if display:
                params_rows += f"<tr><td>{fname}</td><td>{display}</td></tr>"

    params_html = (
        f'<table class="params-table">{params_rows}</table>'
        if params_rows
        else '<p class="no-params">Paramètres par défaut</p>'
    )

    return f"""
<div class="layer-card">
  <div class="layer-card-header {header_class}">
    {name}{disabled_tag}
    <span class="layer-type-badge">{mtype}</span>
  </div>
  <div class="layer-card-body">
    <div class="layer-timing">
      Début : {t_start:.2f} beats &nbsp;|&nbsp;
      Fin : {t_end:.2f} beats &nbsp;|&nbsp;
      Durée : {t_length:.2f} beats
    </div>
    {resource_html}
    {params_html}
  </div>
</div>"""


def render_track(track: dict) -> str:
    name = track.get("name") or "Piste sans nom"
    length = track.get("length_in_beats", 0)
    cues = track.get("cues", [])
    layers = track.get("layers", [])

    # Cues table
    cues_rows = ""
    for cue in cues:
        beat = cue.get("beat", 0)
        tc = beats_to_timecode(beat)
        cue_name = cue.get("name", "") or "—"
        note = cue.get("note", "") or ""
        cue_type = cue.get("type", "") or ""
        cues_rows += f"""
<tr>
  <td class="beat">{beat:.2f}</td>
  <td class="timecode">{tc}</td>
  <td>{cue_name}</td>
  <td class="cue-note">{note}</td>
  <td>{cue_type}</td>
</tr>"""

    cues_section = ""
    if cues:
        cues_section = f"""
<div class="section-title">Cues ({len(cues)})</div>
<table class="cues">
  <thead>
    <tr>
      <th>Beat</th>
      <th>Timecode</th>
      <th>Nom</th>
      <th>Note</th>
      <th>Type</th>
    </tr>
  </thead>
  <tbody>
    {cues_rows}
  </tbody>
</table>"""

    # Layers grid
    layers_html = ""
    if layers:
        cards = "".join(render_layer_card(l) for l in layers)
        layers_html = f"""
<div class="section-title">Layers ({len(layers)})</div>
<div class="layers-grid">
  {cards}
</div>"""

    return f"""
<div class="track-section">
  <div class="track-header">
    {name}
    <span class="track-meta">{length:.2f} beats &nbsp;|&nbsp; {len(layers)} layer(s) &nbsp;|&nbsp; {len(cues)} cue(s)</span>
  </div>
  {cues_section}
  {layers_html}
</div>"""


def generate_report(data: dict, out_path: Path):
    from datetime import datetime

    project_name = data.get("project", {}).get("name") or "Inconnu"
    tracks = data.get("tracks", [])

    tracks_html = "\n".join(render_track(t) for t in tracks)
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    html = TEMPLATE.format(
        project_name=project_name,
        generated_at=generated_at,
        n_tracks=len(tracks),
        tracks_html=tracks_html,
    )

    out_path.write_text(html, encoding="utf-8")
    print(f"Report generated: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML show report from Disguise timeline JSON"
    )
    parser.add_argument("input", help="Input JSON file (from extract.py)")
    parser.add_argument("--out", default=None, help="Output HTML file (default: same name as input)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        raise SystemExit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))

    out_path = Path(args.out) if args.out else input_path.with_suffix(".html")
    generate_report(data, out_path)


if __name__ == "__main__":
    main()
