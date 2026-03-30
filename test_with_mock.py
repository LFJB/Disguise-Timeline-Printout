"""
Test the report generator with mock data (no Designer connection needed).
Run: python test_with_mock.py
"""

import json
from pathlib import Path
from generate_report import generate_report

MOCK_DATA = {
    "project": {"name": "SPECTACLE_TEST_2025"},
    "errors": [],
    "tracks": [
        {
            "name": "MAIN SHOW",
            "length_in_beats": 3600.0,
            "cues": [
                {"beat": 0.0,    "time_seconds": 0.0,   "name": "GO",       "note": "Début spectacle — fade in 3s", "type": "CUE"},
                {"beat": 240.0,  "time_seconds": 240.0, "name": "SCENE 1",  "note": "Entrée danseurs côté jardin",  "type": "CUE"},
                {"beat": 480.0,  "time_seconds": 480.0, "name": "SCENE 2",  "note": "Projection plein écran",       "type": "CUE"},
                {"beat": 720.0,  "time_seconds": 720.0, "name": "ENTRACTE", "note": "Musique douce — 15min",        "type": "CUE"},
                {"beat": 1440.0, "time_seconds": 1440.0,"name": "ACT 2",    "note": "Reprise — tous en scène",      "type": "CUE"},
                {"beat": 3540.0, "time_seconds": 3540.0,"name": "FIN",      "note": "Fade out total",               "type": "CUE"},
            ],
            "layers": [
                {
                    "name": "BG_VIDEO",
                    "enabled": True,
                    "module_type": "VideoModule",
                    "t_start": 0.0,
                    "t_end": 3600.0,
                    "t_length": 3600.0,
                    "resource": "media/bg_loop_v3.mov",
                    "fields": {
                        "opacity":   [{"beat": 0, "value": "1.0"}],
                        "brightness":[{"beat": 0, "value": "0.85"}],
                        "mapping":   [{"beat": 0, "value": "ECRAN_CENTRE"}],
                        "loop":      [{"beat": 0, "value": "true"}],
                        "fit":       [{"beat": 0, "value": "fill"}],
                    }
                },
                {
                    "name": "FX_COLOR_GRADE",
                    "enabled": True,
                    "module_type": "FXModule",
                    "t_start": 0.0,
                    "t_end": 3600.0,
                    "t_length": 3600.0,
                    "resource": None,
                    "fields": {
                        "saturation": [{"beat": 0, "value": "1.2"}],
                        "contrast":   [{"beat": 0, "value": "1.1"}],
                        "r":          [{"beat": 0, "value": "1.05"}],
                        "b":          [{"beat": 0, "value": "0.95"}],
                    }
                },
                {
                    "name": "LOGO_OVERLAY",
                    "enabled": True,
                    "module_type": "ImageModule",
                    "t_start": 0.0,
                    "t_end": 240.0,
                    "t_length": 240.0,
                    "resource": "media/logo_blanc.png",
                    "fields": {
                        "opacity": [
                            {"beat": 0,   "value": "0.0"},
                            {"beat": 30,  "value": "1.0"},
                            {"beat": 210, "value": "1.0"},
                            {"beat": 240, "value": "0.0"},
                        ],
                        "x": [{"beat": 0, "value": "0.85"}],
                        "y": [{"beat": 0, "value": "0.9"}],
                        "scale": [{"beat": 0, "value": "0.3"}],
                        "mapping": [{"beat": 0, "value": "ECRAN_CENTRE"}],
                    }
                },
                {
                    "name": "TITLES",
                    "enabled": True,
                    "module_type": "TextModule",
                    "t_start": 250.0,
                    "t_end": 480.0,
                    "t_length": 230.0,
                    "resource": None,
                    "fields": {
                        "text":    [{"beat": 250, "value": "ACTE 1"}],
                        "opacity": [
                            {"beat": 250, "value": "0.0"},
                            {"beat": 270, "value": "1.0"},
                            {"beat": 460, "value": "1.0"},
                            {"beat": 480, "value": "0.0"},
                        ],
                        "mapping": [{"beat": 250, "value": "ECRAN_CENTRE"}],
                    }
                },
            ],
        },
        {
            "name": "AUDIO",
            "length_in_beats": 3600.0,
            "cues": [
                {"beat": 0.0,    "time_seconds": 0.0,   "name": "AUDIO_GO",  "note": "Son ambiance — vol 80%", "type": "CUE"},
                {"beat": 720.0,  "time_seconds": 720.0, "name": "FADE_OUT",  "note": "Fade 5s",               "type": "CUE"},
                {"beat": 1440.0, "time_seconds": 1440.0,"name": "AUDIO_ACT2","note": "Musique acte 2",        "type": "CUE"},
            ],
            "layers": [
                {
                    "name": "MUSIQUE_PRINCIPALE",
                    "enabled": True,
                    "module_type": "AudioModule",
                    "t_start": 0.0,
                    "t_end": 3600.0,
                    "t_length": 3600.0,
                    "resource": "audio/musique_finale_stereo.wav",
                    "fields": {
                        "volume": [
                            {"beat": 0,   "value": "0.8"},
                            {"beat": 720, "value": "0.0"},
                        ],
                    }
                },
                {
                    "name": "AMBIANCE_2",
                    "enabled": False,
                    "module_type": "AudioModule",
                    "t_start": 1440.0,
                    "t_end": 3600.0,
                    "t_length": 2160.0,
                    "resource": "audio/ambiance_acte2.wav",
                    "fields": {
                        "volume": [{"beat": 1440, "value": "0.6"}],
                    }
                },
            ],
        },
    ],
}


if __name__ == "__main__":
    out = Path("test_report.html")
    generate_report(MOCK_DATA, out)
    print(f"Test report: {out.resolve()}")
    print("Ouvre ce fichier dans un navigateur pour vérifier le rendu.")
