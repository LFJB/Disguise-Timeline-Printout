"""
Main extraction script (Python 3).
Connects to Disguise Designer via python-plugin, runs the inner extractor,
and saves the raw JSON data.

Usage:
    python extract.py --host 192.168.1.100
    python extract.py --host 192.168.1.100 --port 80 --out timeline_data.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

from designer_plugin.d3sdk.client import D3PluginClient


INNER_SCRIPT_PATH = Path(__file__).parent / "extractor_inner.py"


def load_inner_script() -> str:
    return INNER_SCRIPT_PATH.read_text(encoding="utf-8")


class TimelineExtractor(D3PluginClient):
    def extract_timeline(self) -> dict:
        """Execute the inner script on Designer and return parsed JSON data."""
        # The body of this method runs inside Designer (Python 2.7)
        # We use a raw script approach via session instead of class inheritance
        # to avoid limitations with the inner script size.
        pass


def extract_from_designer(host: str, port: int = 80) -> dict:
    """Connect to Designer and extract timeline data."""
    inner_script = load_inner_script()

    from designer_plugin.d3sdk.session import D3Session
    from designer_plugin.models import PluginPayload

    session = D3Session(host=host, port=port)

    payload = PluginPayload[str](
        script=inner_script,
        returnType=str,
    )

    print(f"Connecting to Designer at {host}:{port}...")
    with session:
        response = session.rpc(payload)

    if response is None:
        raise RuntimeError("No response from Designer")

    # response is a JSON string returned by extract_all_tracks()
    data = json.loads(response)
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Extract Disguise Designer timeline data to JSON"
    )
    parser.add_argument("--host", required=True, help="Designer machine IP or hostname")
    parser.add_argument("--port", type=int, default=80, help="Designer API port (default: 80)")
    parser.add_argument("--out", default="timeline_data.json", help="Output JSON file path")
    args = parser.parse_args()

    data = extract_from_designer(host=args.host, port=args.port)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Data saved to {out_path}")

    # Print summary
    tracks = data.get("tracks", [])
    print(f"\nFound {len(tracks)} track(s):")
    for track in tracks:
        name = track.get("name", "?")
        n_layers = len(track.get("layers", []))
        n_cues = len(track.get("cues", []))
        print(f"  - {name}: {n_layers} layer(s), {n_cues} cue(s)")

    if data.get("errors"):
        print("\nWarnings during extraction:")
        for e in data["errors"]:
            print(f"  ! {e}")

    return data


if __name__ == "__main__":
    main()
