"""
One-shot script: extract from Designer + generate HTML report.

Usage:
    python run.py --host 192.168.1.100
    python run.py --host 192.168.1.100 --port 80 --out mon_spectacle
"""

import argparse
import json
from pathlib import Path

from extract import extract_from_designer
from generate_report import generate_report


def main():
    parser = argparse.ArgumentParser(
        description="Disguise Timeline Exporter — extract + report in one step"
    )
    parser.add_argument("--host", required=True, help="Designer machine IP or hostname")
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--out", default="timeline", help="Output base name (no extension)")
    args = parser.parse_args()

    base = Path(args.out)
    json_path = base.with_suffix(".json")
    html_path = base.with_suffix(".html")

    print(f"[1/3] Extraction depuis {args.host}:{args.port}...")
    data = extract_from_designer(host=args.host, port=args.port)

    print(f"[2/3] Sauvegarde JSON → {json_path}")
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[3/3] Génération du rapport → {html_path}")
    generate_report(data, html_path)

    # Summary
    tracks = data.get("tracks", [])
    print(f"\nRésumé :")
    for track in tracks:
        name = track.get("name", "?")
        n_layers = len(track.get("layers", []))
        n_cues = len(track.get("cues", []))
        print(f"  Piste '{name}': {n_layers} layer(s), {n_cues} cue(s)")

    if data.get("errors"):
        print("\nAvertissements :")
        for e in data["errors"]:
            print(f"  ! {e}")

    print(f"\nOuvrir le rapport : {html_path.resolve()}")


if __name__ == "__main__":
    main()
